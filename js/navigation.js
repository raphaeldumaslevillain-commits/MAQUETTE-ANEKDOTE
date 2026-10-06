(() => {
  const dialog = document.querySelector('#navigation-dialog');
  const toggle = document.querySelector('[data-menu-open]');
  const close = dialog?.querySelector('[data-menu-close]');
  if (!dialog || !toggle) return;
  toggle.addEventListener('click', () => {
    dialog.showModal();
    toggle.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  });
  close?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    toggle.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    toggle.focus();
  });
  dialog.querySelectorAll('a').forEach(link => link.addEventListener('click', () => dialog.close()));
  document.querySelector('[data-top]')?.addEventListener('click', () => window.scrollTo({top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth'}));
})();
