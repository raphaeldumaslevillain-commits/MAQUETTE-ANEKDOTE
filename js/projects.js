(() => {
  const controls = document.querySelector('[data-filters]');
  if (!controls) return;
  const projects = [...document.querySelectorAll('[data-project]')];
  const count = document.querySelector('[data-project-count]');
  const empty = document.querySelector('[data-empty-projects]');
  const filter = value => {
    let visible = 0;
    projects.forEach(project => {
      const categories = JSON.parse(project.dataset.categories || '[]');
      project.hidden = value !== 'all' && !categories.includes(value);
      if (!project.hidden) visible++;
    });
    controls.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filter === value)));
    if (count) count.textContent = `${String(visible).padStart(2, '0')} projet${visible > 1 ? 's' : ''}`;
    if (empty) empty.hidden = visible !== 0;
    const url = new URL(location.href);
    if (value === 'all') url.searchParams.delete('expertise'); else url.searchParams.set('expertise', value);
    history.replaceState(null, '', url);
  };
  controls.addEventListener('click', event => {
    const button = event.target.closest('button[data-filter]');
    if (button) filter(button.dataset.filter);
  });
  const initial = new URLSearchParams(location.search).get('expertise');
  if (initial && [...controls.querySelectorAll('button')].some(b => b.dataset.filter === initial)) filter(initial);
})();
