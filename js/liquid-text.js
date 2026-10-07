(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const cycleTime = 2000, cooldownTime = 500, morphTime = 1500;
  document.querySelectorAll('[data-liquid]').forEach(element => {
    const words = JSON.parse(element.dataset.liquidWords);
    if (words.length < 2) return;
    const button = element.querySelector('[data-liquid-switch]');
    const fallback = element.querySelector('.liquid-static');
    const stage = element.querySelector('.liquid-stage');
    const from = element.querySelector('[data-liquid-from]');
    const to = element.querySelector('[data-liquid-to]');
    const ink = element.querySelector('[data-liquid-ink]');
    const baseline = element.querySelector('[data-liquid-baseline]');
    const blurFrom = element.querySelector('[data-liquid-blur-from]');
    const blurTo = element.querySelector('[data-liquid-blur-to]');
    const alphaFrom = element.querySelector('[data-liquid-alpha-from]');
    const alphaTo = element.querySelector('[data-liquid-alpha-to]');
    // Keep blur, opacity and threshold in one SVG rendering tree. WebKit can
    // composite CSS-blurred HTML children outside their parent's SVG filter.
    const filterId = ink.dataset.liquidFilter;
    const measure = () => {
      if (button.hidden) return;
      const y = baseline.getBoundingClientRect().top - stage.getBoundingClientRect().top;
      from.setAttribute('y', String(y));
      to.setAttribute('y', String(y));
    };
    let elapsed = 0, frame, lastTime = null, running = false, renderedIndex = -1;
    let onScreen = !('IntersectionObserver' in window), paused = false, hovered = false, focused = false;
    const render = () => {
      const index = Math.floor(elapsed / cycleTime) % words.length;
      const fraction = Math.max(0, (elapsed % cycleTime - cooldownTime) / morphTime);
      if (index !== renderedIndex) {
        from.textContent = words[index];
        to.textContent = words[(index + 1) % words.length];
        element.dataset.liquidIndex = String(index);
        renderedIndex = index;
      }
      if (fraction === 0) {
        ink.setAttribute('filter', 'none');
        from.setAttribute('filter', 'none');
        to.setAttribute('filter', 'none');
        from.style.opacity = '1';
        to.style.opacity = '0';
      } else {
        ink.setAttribute('filter', `url(#${filterId}-threshold)`);
        from.setAttribute('filter', `url(#${filterId}-from)`);
        to.setAttribute('filter', `url(#${filterId}-to)`);
        blurFrom.setAttribute('stdDeviation', String(Math.min(8 / (1 - fraction) - 8, 100)));
        blurTo.setAttribute('stdDeviation', String(Math.min(8 / fraction - 8, 100)));
        alphaFrom.setAttribute('slope', String(Math.pow(1 - fraction, .4)));
        alphaTo.setAttribute('slope', String(Math.pow(fraction, .4)));
        from.style.opacity = to.style.opacity = '1';
      }
    };
    const settle = () => {
      const fraction = Math.max(0, (elapsed % cycleTime - cooldownTime) / morphTime);
      elapsed = (Math.floor(elapsed / cycleTime) + (fraction >= .5 ? 1 : 0)) * cycleTime;
      render();
    };
    const tick = now => {
      if (!running) return;
      if (lastTime !== null) elapsed += now - lastTime;
      lastTime = now;
      render();
      frame = requestAnimationFrame(tick);
    };
    const update = () => {
      const active = !reduced.matches && !paused && !hovered && !focused && onScreen && !document.hidden;
      button.hidden = reduced.matches;
      fallback.hidden = !reduced.matches;
      measure();
      button.setAttribute('aria-pressed', String(paused));
      button.title = paused ? 'Reprendre l’animation' : 'Mettre en pause l’animation';
      element.dataset.liquidState = reduced.matches ? 'reduced' : active ? 'running' : 'paused';
      if (active === running) return;
      running = active;
      cancelAnimationFrame(frame);
      lastTime = null;
      if (active) frame = requestAnimationFrame(tick);
      else settle();
    };
    button.addEventListener('click', () => { paused = !paused; update(); });
    button.addEventListener('focus', () => { focused = true; update(); });
    button.addEventListener('blur', () => { focused = false; update(); });
    button.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') { hovered = true; update(); } });
    button.addEventListener('pointerleave', () => { hovered = false; update(); });
    document.addEventListener('visibilitychange', update);
    reduced.addEventListener('change', update);
    if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
      onScreen = entries.some(entry => entry.isIntersecting);
      update();
    }, {threshold:.05}).observe(element);
    render();
    update();
    if ('ResizeObserver' in window) new ResizeObserver(measure).observe(stage);
    else window.addEventListener('resize', measure);
    if (document.fonts) document.fonts.ready.then(measure);
  });
})();
