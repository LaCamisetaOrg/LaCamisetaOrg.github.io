#!/usr/bin/env python3
"""
Fetchea posts de Instagram y crea archivos de action Jekyll con
valores `pending` para causa y alt text (completar con /actions-backfill).

Uso:
  python scripts/instagram_fetcher.py @cuenta1 @cuenta2
  python scripts/instagram_fetcher.py https://www.instagram.com/p/SHORTCODE/
  python scripts/instagram_fetcher.py @cuenta --max-posts 5
"""

import argparse
import hashlib
import re
import sys
import unicodedata
from datetime import date as date_type
from pathlib import Path

import instaloader
import requests
import yaml

SITE_ROOT = Path(__file__).resolve().parent.parent
ACTIONS_DIR = SITE_ROOT / "_actions"
IMAGES_DIR = SITE_ROOT / "assets" / "images" / "actions"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def slugify(text: str, max_len: int = 50) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")[:max_len]


def generate_title(caption: str, max_words: int = 10) -> str:
    clean = re.sub(r"#\w+", "", caption)
    clean = re.sub(r"https?://\S+", "", clean)
    clean = re.sub(r"@\w+", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    # First non-empty line, truncated at sentence boundary
    for line in clean.splitlines():
        line = line.strip()
        if not line:
            continue
        for sep in (".", "!", "?"):
            parts = line.split(sep)
            if parts[0].strip():
                line = parts[0].strip()
                break
        words = line.split()[:max_words]
        result = " ".join(words).strip()
        if result:
            return result
    return "Acción"


def clean_body(caption: str) -> str:
    caption = re.sub(r"https?://\S+", "", caption)
    caption = re.sub(r"[ \t]+", " ", caption)
    caption = re.sub(r"\n{3,}", "\n\n", caption)
    return caption.strip()


# ---------------------------------------------------------------------------
# Image download
# ---------------------------------------------------------------------------

def download_image(url: str) -> tuple[bytes, str]:
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, stream=True, timeout=30)
    r.raise_for_status()
    content_type = r.headers.get("Content-Type", "image/jpeg")
    ext = ".jpg"
    if "png" in content_type:
        ext = ".png"
    elif "webp" in content_type:
        ext = ".webp"
    data = b"".join(r.iter_content(8192))
    return data, ext


# ---------------------------------------------------------------------------
# Jekyll action file
# ---------------------------------------------------------------------------

def make_action_file(post: dict, cause_slug: str, image_path: Path) -> Path:
    date_str = post["date"].strftime("%Y-%m-%d") if hasattr(post["date"], "strftime") else str(post["date"])
    date_compact = date_str.replace("-", "")
    title_slug = slugify(post["title"])
    file_slug = f"{title_slug}-{date_compact}"

    image_rel = f"/assets/images/actions/{image_path.name}"
    description = clean_body(post["caption"])[:200].replace("\n", " ")

    # Use date object for from_date so PyYAML renders it without quotes
    try:
        from_date_val = date_type.fromisoformat(date_str)
    except ValueError:
        from_date_val = date_str

    data = {
        "layout": "action",
        "cause": cause_slug,
        "title": post["title"],
        "description": description,
        "from_date": from_date_val,
        "images": [{
            "src": image_rel,
            "alt": post["alt_text"],
            "image_source": post["url"],
            "main": True,
            "highlight": True,
        }],
    }

    body = clean_body(post["caption"])
    content = f"---\n{yaml.dump(data, allow_unicode=True, default_flow_style=False)}---\n\n{body}\n"

    out = ACTIONS_DIR / f"{file_slug}.md"
    suffix = 1
    while out.exists():
        out = ACTIONS_DIR / f"{file_slug}-{suffix}.md"
        suffix += 1

    out.write_text(content, encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# Instagram scraping
# ---------------------------------------------------------------------------

def _make_loader():
    return instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_comments=False,
        save_metadata=False,
        quiet=True,
    )


def scrape_post_url(loader, url: str) -> dict:
    m = re.search(r"/(?:p|reel)/([A-Za-z0-9_-]+)", url)
    if not m:
        raise ValueError(f"No se pudo extraer el shortcode de: {url}")
    shortcode = m.group(1)
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    return {
        "caption": post.caption or "",
        "date": post.date_local if hasattr(post, "date_local") else post.date,
        "url": url,
        "image_url": post.url,
        "account": post.owner_username,
    }


def scrape_account(loader, username: str, max_posts: int) -> list[dict]:
    username = username.lstrip("@")
    profile = instaloader.Profile.from_username(loader.context, username)
    posts = []
    for i, post in enumerate(profile.get_posts()):
        if i >= max_posts:
            break
        posts.append({
            "caption": post.caption or "",
            "date": post.date_local if hasattr(post, "date_local") else post.date,
            "url": f"https://www.instagram.com/p/{post.shortcode}/",
            "image_url": post.url,
            "account": username,
        })
    return posts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Scrapea posts de Instagram y crea acciones en Lacamiseta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/instagram_fetcher.py @greenpeace_ar @fuenteambiental
  python scripts/instagram_fetcher.py https://www.instagram.com/p/ABC123/
  python scripts/instagram_fetcher.py @conicet_argentina --max-posts 5
        """,
    )
    parser.add_argument("inputs", nargs="+", help="Cuentas (@usuario) o URLs de posts")
    parser.add_argument("--max-posts", type=int, default=3, metavar="N",
                        help="Máx. posts por cuenta (default: 3)")
    args = parser.parse_args()

    loader = _make_loader()

    # Collect posts
    all_posts = []
    for inp in args.inputs:
        print(f"\nObteniendo posts de: {inp}")
        try:
            if inp.startswith("http"):
                post = scrape_post_url(loader, inp)
                all_posts.append(post)
                print("  1 post encontrado")
            else:
                posts = scrape_account(loader, inp, args.max_posts)
                all_posts.extend(posts)
                print(f"  {len(posts)} posts encontrados")
        except Exception as e:
            print(f"  ERROR: {e}")

    if not all_posts:
        print("\nNo se encontraron posts. Saliendo.")
        return

    # Ensure output dirs exist
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nProcesando {len(all_posts)} posts...\n")
    created = []

    for i, post in enumerate(all_posts, 1):
        print(f"[{i}/{len(all_posts)}] {post['url']}")
        caption_preview = (post["caption"] or "")[:100].replace("\n", " ")
        print(f"  Caption: {caption_preview}...")

        try:
            # 1. Download image
            url_hash = hashlib.md5(post["image_url"].encode()).hexdigest()[:8]
            date_s = post["date"].strftime("%Y%m%d") if hasattr(post["date"], "strftime") else str(post["date"]).replace("-", "")
            img_data, ext = download_image(post["image_url"])
            img_name = f"{post['account']}_{date_s}_{url_hash}{ext}"
            img_path = IMAGES_DIR / img_name
            img_path.write_bytes(img_data)
            print(f"  Imagen: assets/images/actions/{img_name} ({len(img_data) // 1024} KB)")

            # 2. Generate title and create action file
            post["title"] = generate_title(post["caption"])
            post["alt_text"] = "pending"
            print(f"  Título: {post['title']}")

            action_file = make_action_file(post, "pending", img_path)
            print(f"  Acción: _actions/{action_file.name}")
            created.append(action_file)

        except Exception as e:
            print(f"  ERROR: {e}")

        print()

    print("=" * 55)
    print(f"Acciones creadas: {len(created)}/{len(all_posts)}")
    for f in created:
        print(f"  _actions/{f.name}")


if __name__ == "__main__":
    main()
