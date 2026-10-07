(() => {
  const section = document.querySelector('[data-manifesto]');
  if (!section) return;
  const items = [...section.querySelectorAll('[data-conviction]')];
  const links = [...section.querySelectorAll('[data-manifesto-link]')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let current = -1;
  const select = index => {
    if (index === current) return;
    current = index;
    section.dataset.activeConviction = String(index);
    section.style.setProperty('--manifesto-angle', `${index * 60}deg`);
    items.forEach((item, i) => item.classList.toggle('is-active', i === index));
    links.forEach((link, i) => {
      if (i === index) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  };
  const motion = () => section.classList.toggle('is-enhanced', !reduced.matches);
  motion();
  reduced.addEventListener('change', motion);
  select(0);
  if ('IntersectionObserver' in window) {
    const visible = new Set();
    let observer;
    const observe = () => {
      observer?.disconnect();
      visible.clear();
      observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) visible.add(entry.target);
          else visible.delete(entry.target);
        });
        const nearest = [...visible].sort((a, b) => {
          const center = innerHeight * .38;
          const distance = item => {
            const bounds = item.getBoundingClientRect();
            return Math.abs(bounds.top + Math.min(bounds.height / 2, 100) - center);
          };
          return distance(a) - distance(b);
        })[0];
        if (nearest) select(items.indexOf(nearest));
      }, {rootMargin:`-${Math.round(innerHeight * .24)}px 0px -${Math.round(innerHeight * .46)}px 0px`, threshold:[0,.2,.4,.6,.8,1]});
      items.forEach(item => observer.observe(item));
    };
    observe();
    let resizeFrame;
    addEventListener('resize', () => {
      cancelAnimationFrame(resizeFrame);
      resizeFrame = requestAnimationFrame(observe);
    });
  }
  links.forEach((link, index) => link.addEventListener('click', event => {
    // Modified clicks keep normal link behavior; plain activation follows the text.
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    select(index);
    const heading = items[index].querySelector('h3');
    heading.focus({preventScroll:true});
    items[index].scrollIntoView({behavior:reduced.matches ? 'instant' : 'smooth', block:'start'});
    history.replaceState(null, '', link.getAttribute('href'));
  }));
})();
