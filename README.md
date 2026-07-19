# Ponete la camiseta

Jekyll site for social causes, deployable to GitHub Pages.

## Local development

```bash
bundle install
bundle exec jekyll serve --livereload
```

Then open `http://localhost:4000`.

## Adding a cause

Create a new file in `_causes/` following this template:

```yaml
---
title: "La Salud"
slug: "salud"
image_color: "#f08080"   # placeholder color; set image: /assets/images/salud.jpg when ready
hashtags:
  - Salud
order: 4
---

Content in Markdown here...
```

The cause will automatically appear in the nav pills and in the scrollable list.

## Deploying to GitHub Pages

Push to GitHub, then go to **Settings → Pages → Source: Deploy from branch → main / (root)**.

The site will be live at `https://<username>.github.io`.
