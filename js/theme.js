(() => {
  const root = document.documentElement;
  const buttons = [...document.querySelectorAll('[data-theme-toggle]')];
  if (!buttons.length) return;
  const system = matchMedia('(prefers-color-scheme: dark)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const status = document.querySelector('[data-theme-status]');
  let busy = false;
  let fallbackTimer;

  function savedTheme() {
    try { return localStorage.getItem('anekdote-theme'); } catch (_) { return null; }
  }
  function sync() {
    const dark = root.dataset.theme === 'dark';
    buttons.forEach(button => {
      button.setAttribute('aria-checked', String(dark));
      button.title = dark ? 'Passer au thème clair' : 'Passer au thème sombre';
    });
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#191918' : '#f4f2eb');
  }
  function apply(theme, remember = false) {
    root.dataset.theme = theme;
    if (remember) {
      try { localStorage.setItem('anekdote-theme', theme); } catch (_) {}
      if (status) status.textContent = theme === 'dark' ? 'Thème sombre activé.' : 'Thème clair activé.';
    }
    sync();
  }
  function fade(theme) {
    if (!reduced.matches) {
      root.classList.add('theme-fading');
      clearTimeout(fallbackTimer);
      fallbackTimer = setTimeout(() => root.classList.remove('theme-fading'), 420);
    }
    apply(theme, true);
  }
  async function toggle(button) {
    // Keep keyboard focus in place; ignore repeated clicks while the reveal is running.
    if (busy) return;
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    if (reduced.matches || typeof document.startViewTransition !== 'function') {
      fade(theme);
      return;
    }
    busy = true;
    root.classList.add('theme-reveal');
    const bounds = button.getBoundingClientRect();
    const x = bounds.left + bounds.width / 2;
    const y = bounds.top + bounds.height / 2;
    const radius = Math.hypot(Math.max(x, innerWidth - x), Math.max(y, innerHeight - y));
    let transition;
    try {
      transition = document.startViewTransition(() => apply(theme, true));
      await transition.ready;
      const reveal = root.animate(
        {clipPath: [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`]},
        {duration: 620, easing: 'cubic-bezier(.22,.8,.25,1)', fill: 'both', pseudoElement: '::view-transition-new(root)'}
      );
      await reveal.finished;
      await transition.finished;
    } catch (_) {
      transition?.skipTransition();
      // A skipped or unsupported snapshot must never prevent the actual theme change.
      if (root.dataset.theme !== theme) fade(theme);
    } finally {
      root.classList.remove('theme-reveal');
      busy = false;
    }
  }
  buttons.forEach(button => button.addEventListener('click', () => toggle(button)));
  system.addEventListener('change', event => {
    if (!['light', 'dark'].includes(savedTheme())) apply(event.matches ? 'dark' : 'light');
  });
  window.addEventListener('storage', event => {
    if (event.key === 'anekdote-theme') {
      apply(['light', 'dark'].includes(event.newValue) ? event.newValue : (system.matches ? 'dark' : 'light'));
    }
  });
  sync();
})();
