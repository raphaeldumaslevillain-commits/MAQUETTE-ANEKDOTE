// Apply the saved choice before styles paint, including on nested pages.
(() => {
  let saved;
  try { saved = localStorage.getItem('anekdote-theme'); } catch (_) {}
  const theme = saved === 'dark' || saved === 'light'
    ? saved
    : (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', theme === 'dark' ? '#191918' : '#f4f2eb');
})();
