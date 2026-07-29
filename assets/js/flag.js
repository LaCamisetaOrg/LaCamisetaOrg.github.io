(function () {
  var AVAILABLE_FLAGS = ['argentina', 'wiphala', 'wenufoye'];

  var VARS = [
    '--color-main', '--color-secondary', '--color-complementary', '--color-text-complementary',
    '--color-action', '--color-navbar', '--color-footer',
  ];

  var PALETTES = {
    'default': {
      '--color-main':               '#1a1a1a',
      '--color-secondary':          '#8b0000',
      '--color-complementary':      '#cc0000',
      '--color-text-complementary': '#ffffff',
      '--color-action':             '#cc0000',
      '--color-navbar':             '#ffffff',
      '--color-footer':             '#ffffff',
    },
    argentina: {
      '--color-main':               '#6CACE4',
      '--color-secondary':          '#6CACE4',
      '--color-complementary':      '#FFB81C',
      '--color-text-complementary': '#1a1a1a',
      '--color-action':             '#6CACE4',
      '--color-navbar':             '#ffffff',
      '--color-footer':             '#ffffff',
    },
    wenufoye: {
      '--color-main':               '#b01f20',
      '--color-secondary':          '#75aadb',
      '--color-complementary':      '#008000',
      '--color-text-complementary': '#ffffff',
      '--color-action':             '#ffd700',
      '--color-navbar':             '#ffffff',
      '--color-footer':             '#ffffff',
    },
    wiphala: {
      '--color-main':               '#008000',
      '--color-secondary':          '#742c64',
      '--color-complementary':      '#EB7711',
      '--color-text-complementary': '#FCDD09',
      '--color-action':             '#0F47AF',
      '--color-navbar':             '#ffffff',
      '--color-footer':             '#ffffff',
    },
    lule: {
      '--color-main':               '#eb7711',
      '--color-secondary':          '#8b0000',
      '--color-complementary':      '#da121a',
      '--color-text-complementary': '#ffffff',
      '--color-action':             '#1a1a1a',
      '--color-navbar':             '#ffffff',
      '--color-footer':             '#ffffff',
    },
  };

  var currentPalette = 'default';

  function swapImages(paletteName) {
    document.querySelectorAll(CAUSE_IMAGES + '[data-src-base]').forEach(function (img) {
      var base = img.dataset.srcBase;
      var newSrc;
      var isCauseImage = base.indexOf('assets/images/causes') !== -1;
      if (paletteName === 'default' || !isCauseImage) {
        newSrc = base;
      } else {
        var dot = base.lastIndexOf('.');
        if (dot === -1) return;
        newSrc = base.slice(0, dot) + '_' + paletteName + base.slice(dot);
      }
      var wrap = img.parentElement;
      img.onload = function () { wrap.classList.remove('is-loading'); img.onload = null; };
      img.onerror = function () { img.src = base; img.onerror = null; wrap.classList.remove('is-loading'); };
      wrap.classList.add('is-loading');
      img.src = newSrc;
      if (img.complete) wrap.classList.remove('is-loading');
    });
  }

  function setThemeColors(name) {
    var palette = PALETTES[name];
    if (!palette) return;
    currentPalette = name;
    var root = document.documentElement;
    VARS.forEach(function (v) { root.style.removeProperty(v); });
    Object.keys(palette).forEach(function (v) { root.style.setProperty(v, palette[v]); });
    try { localStorage.setItem('lacamiseta-flag', name); } catch (e) {}
    if (document.readyState !== 'loading') swapImages(name);
  }

  function resetThemeColors() {
    setThemeColors('default');
  }

  var CAUSE_IMAGES = '.cause-banner img, .cause-card__image-wrap img';

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll(CAUSE_IMAGES).forEach(function (img) {
      var src = img.getAttribute('src');
      if (src) img.dataset.srcBase = src;
    });
    swapImages(currentPalette);

    document.querySelectorAll('.hero-palette-option').forEach(function (btn) {
      if (AVAILABLE_FLAGS.indexOf(btn.dataset.palette) === -1) btn.remove();
    });

    var word = document.getElementById('hero-word');
    var menu = document.getElementById('hero-palette-menu');

    if (AVAILABLE_FLAGS.length <= 1) {
      if (word) {
        word.removeAttribute('tabindex');
        word.removeAttribute('role');
        word.removeAttribute('aria-haspopup');
        word.removeAttribute('aria-expanded');
        word.removeAttribute('aria-controls');
      }
    } else if (word && menu) {
      function closeMenu() {
        menu.hidden = true;
        word.setAttribute('aria-expanded', 'false');
      }
      function openMenu() {
        menu.hidden = false;
        word.setAttribute('aria-expanded', 'true');
      }
      word.addEventListener('click', function (e) {
        e.stopPropagation();
        menu.hidden ? openMenu() : closeMenu();
      });
      word.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); menu.hidden ? openMenu() : closeMenu(); }
        if (e.key === 'Escape') closeMenu();
      });
      menu.addEventListener('click', function (e) {
        var btn = e.target.closest('.hero-palette-option');
        if (!btn) return;
        var palette = btn.dataset.palette;
        if (palette) { setThemeColors(palette); } else { resetThemeColors(); }
        closeMenu();
      });
      document.addEventListener('click', closeMenu);
      document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
    }
  });

  try {
    var saved = localStorage.getItem('lacamiseta-flag');
    var initial;
    if (AVAILABLE_FLAGS.length === 1) {
      initial = AVAILABLE_FLAGS[0];
    } else {
      initial = saved && PALETTES[saved] && AVAILABLE_FLAGS.indexOf(saved) !== -1 ? saved : 'default';
    }
    setThemeColors(initial);
  } catch (e) {
    setThemeColors(AVAILABLE_FLAGS.length === 1 ? AVAILABLE_FLAGS[0] : 'default');
  }

  window.setThemeColors = setThemeColors;
  window.resetThemeColors = resetThemeColors;
}());
