(function () {
  var VARS = [
    '--color-main', '--color-complementary', '--color-action',
    '--color-navbar', '--color-footer',
  ];

  var PALETTES = {
    argentina: {
      '--color-main':          '#6CACE4',
      '--color-complementary': '#FFB81C',
      '--color-action':        '#7D4016',
      '--color-navbar':        '#ffffff',
      '--color-footer':        '#ffffff',
    },
    wenufoye: {
      '--color-main':          '#b01f20',
      '--color-complementary': '#ffd700',
      '--color-action':        '#75aadb',
      '--color-navbar':        '#ffffff',
      '--color-footer':        '#ffffff',
    },
    wiphala: {
      '--color-main':          '#eb7711',
      '--color-complementary': '#FCDD09',
      '--color-action':        '#742c64',
      '--color-navbar':        '#ffffff',
      '--color-footer':        '#ffffff',
    },
  };

  function setFlag(name) {
    var palette = PALETTES[name];
    if (!palette) return;
    var root = document.documentElement;
    VARS.forEach(function (v) { root.style.removeProperty(v); });
    Object.keys(palette).forEach(function (v) { root.style.setProperty(v, palette[v]); });
    try { localStorage.setItem('lacamiseta-flag', name); } catch (e) {}
  }

  try {
    var saved = localStorage.getItem('lacamiseta-flag');
    if (saved && PALETTES[saved]) setFlag(saved);
  } catch (e) {}

  window.setFlag = setFlag;
}());
