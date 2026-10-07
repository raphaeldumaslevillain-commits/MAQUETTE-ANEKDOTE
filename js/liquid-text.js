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
        stage.style.filter = 'none';
        from.style.filter = to.style.filter = 'none';
        from.style.opacity = '1';
        to.style.opacity = '0';
      } else {
        stage.style.filter = '';
        from.style.filter = `blur(${Math.min(8 / (1 - fraction) - 8, 100)}px)`;
        from.style.opacity = String(Math.pow(1 - fraction, .4));
        to.style.filter = `blur(${Math.min(8 / fraction - 8, 100)}px)`;
        to.style.opacity = String(Math.pow(fraction, .4));
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
  });
})();
