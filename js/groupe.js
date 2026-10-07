(() => {
  const section = document.querySelector('[data-group-unfold]');
  if (!section) return;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  const stage = section.querySelector('.group-sticky');
  const origin = section.querySelector('.group-origin');
  const intro = section.querySelector('.group-heading');
  const finalHeading = section.querySelector('.group-heading-final');
  const shards = [...section.querySelectorAll('.group-shard')];
  const brands = [...section.querySelectorAll('.group-brand')];
  const tethers = section.querySelector('.group-tethers');
  const paths = [...tethers.querySelectorAll('path')];
  const clamp = value => Math.max(0, Math.min(1, value));
  const range = (value, start, end) => clamp((value - start) / (end - start));
  const ease = value => value * value * (3 - 2 * value);
  let start = 0, distance = 1, width = 0, height = 0;
  let progress = 0, target = 0, frame = 0;
  let enabled = false, compact = false;

  const render = p => {
    const depart = ease(range(p, .08, .5));
    const arrive = ease(range(p, .28, .76));
    const heading = ease(range(p, .56, .82));
    origin.style.opacity = String(1 - range(p, .08, .12));
    origin.style.transform = `translate(-50%,-50%) scale(${1 - depart * .07})`;
    intro.style.opacity = String(1 - ease(range(p, .08, .3)));
    intro.style.transform = `translateY(${-depart * 35}px)`;
    finalHeading.style.opacity = String(heading);
    finalHeading.style.transform = `translateY(${(1 - heading) * 24}px)`;
    shards.forEach((shard, index) => {
      const x = index % 2 ? 1 : -1;
      const y = index < 2 ? -1 : 1;
      shard.style.opacity = String(range(p, .07, .09) * (1 - ease(range(p, .3, .59))));
      shard.style.transform = `translate3d(${x * width * .18 * depart}px,${y * height * .16 * depart}px,0) rotate(${x * y * 5 * depart}deg) scale(${1 - depart * .2})`;
    });
    brands.forEach((brand, index) => {
      const local = ease(range(p, .29 + index * .022, .74 + index * .022));
      const x = (index % 2 ? 1 : -1) * width * (compact ? .235 : .25);
      const y = (index < 2 ? -.14 : .19) * height;
      brand.style.transform = `translate(calc(-50% + ${x * arrive}px),calc(-50% + ${y * arrive}px)) scale(${.42 + local * .58})`;
      brand.style.opacity = String(local);
      brand.classList.toggle('is-ready', p > .73);
      brand.inert = p <= .73;
    });
    tethers.style.opacity = String(range(p, .25, .45) * (1 - range(p, .67, .87)) * .24);
    paths.forEach(path => { path.style.strokeDashoffset = String(1 - arrive); });
  };
  const tick = () => {
    frame = 0;
    if (!enabled || document.hidden) return;
    // Short easing preserves a direct connection to the native scroll position.
    progress += (target - progress) * .16;
    if (Math.abs(target - progress) < .0002) progress = target;
    render(progress);
    if (progress !== target) frame = requestAnimationFrame(tick);
  };
  const onScroll = () => {
    if (!enabled) return;
    target = clamp((scrollY - start) / distance);
    if (!frame && !document.hidden) frame = requestAnimationFrame(tick);
  };
  const measure = () => {
    if (!enabled) return;
    const nav = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--nav')) || 82;
    start = section.getBoundingClientRect().top + scrollY - nav;
    distance = Math.max(1, section.offsetHeight - stage.offsetHeight);
    width = stage.clientWidth;
    height = stage.clientHeight;
    compact = width <= 800;
    target = clamp((scrollY - start) / distance);
    progress = target;
    render(progress);
  };
  const setup = () => {
    cancelAnimationFrame(frame); frame = 0;
    enabled = !reduce.matches;
    section.classList.toggle('is-animated', enabled);
    brands.forEach(brand => { brand.inert = false; });
    if (enabled) measure();
    else [origin, intro, finalHeading, ...shards, ...brands, tethers, ...paths].forEach(element => { element.removeAttribute('style'); });
  };
  addEventListener('scroll', onScroll, {passive: true});
  addEventListener('resize', measure, {passive: true});
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) { cancelAnimationFrame(frame); frame = 0; }
    else onScroll();
  });
  reduce.addEventListener('change', setup);
  document.fonts?.ready.then(measure);
  setup();
})();
