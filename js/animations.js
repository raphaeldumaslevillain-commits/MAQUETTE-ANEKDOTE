(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.remove('waiting');
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {threshold: 0.05, rootMargin: '0px 0px -20px 0px'});
    document.querySelectorAll('.reveal').forEach(element => {
      if (element.getBoundingClientRect().top > innerHeight) element.classList.add('waiting');
      observer.observe(element);
    });
    reduced.addEventListener('change', event => {
      if (event.matches) document.querySelectorAll('.waiting').forEach(e => e.classList.remove('waiting'));
    });
  }
  let pending = false;
  const update = () => {
    const range = document.documentElement.scrollHeight - innerHeight;
    document.documentElement.style.setProperty('--progress', range > 0 ? String(scrollY / range) : '0');
    pending = false;
  };
  window.addEventListener('scroll', () => {if (!pending) {pending = true; requestAnimationFrame(update);}}, {passive: true});
  update();
})();
