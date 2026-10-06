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
  document.querySelectorAll('.nav-primary a').forEach((link, i) => link.style.setProperty('--nav-order', i));
  // Depth only on editorial hero images; portraits and client logos stay unaffected.
  const scenes = [...document.querySelectorAll('.company-stage,.service-intro + .page-visual,.case-hero')];
  const activeScenes = new Set();
  let sceneFrame = 0;
  const paintScenes = () => {
    sceneFrame = 0;
    document.querySelector('.site-header')?.classList.toggle('is-scrolled', scrollY > 12);
    if (reduced.matches || document.hidden) return;
    for (const scene of activeScenes) {
      const box = scene.getBoundingClientRect();
      const shift = Math.max(-14, Math.min(14, (innerHeight / 2 - box.top - box.height / 2) * .035));
      scene.style.setProperty('--scene-shift', `${shift.toFixed(2)}px`);
    }
  };
  const scheduleScenes = () => { if (!sceneFrame) sceneFrame = requestAnimationFrame(paintScenes); };
  if ('IntersectionObserver' in window) {
    const sceneObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) activeScenes.add(entry.target); else activeScenes.delete(entry.target);
      });
      scheduleScenes();
    });
    scenes.forEach(scene => { scene.classList.add('scene-motion'); sceneObserver.observe(scene); });
  }
  window.addEventListener('scroll', scheduleScenes, {passive:true});
  window.addEventListener('resize', scheduleScenes, {passive:true});
  reduced.addEventListener('change', event => {
    if (event.matches) scenes.forEach(scene => scene.style.removeProperty('--scene-shift'));
    scheduleScenes();
  });
  paintScenes();
})();
