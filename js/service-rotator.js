(() => {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('[data-service-rotator]').forEach(rotator => {
    const phrases = JSON.parse(rotator.dataset.services);
    const button = rotator.querySelector('[data-service-toggle]');
    const copy = rotator.querySelector('[data-service-copy]');
    const fallback = rotator.querySelector('.service-static');
    let current = 0, timer, frame, running = false;
    let onScreen = !('IntersectionObserver' in window), paused = false, focused = false, hovered = false;
    const finish = () => {
      cancelAnimationFrame(frame);
      copy.textContent = phrases[current];
    };
    const type = () => {
      cancelAnimationFrame(frame);
      rotator.dataset.serviceIndex = String(current);
      const characters = Array.from(phrases[current]);
      const start = performance.now();
      copy.textContent = '';
      const tick = now => {
        const progress = Math.min(1, (now - start) / 260);
        copy.textContent = characters.slice(0, Math.ceil(characters.length * progress)).join('');
        if (progress < 1) frame = requestAnimationFrame(tick);
      };
      frame = requestAnimationFrame(tick);
    };
    const update = () => {
      clearInterval(timer);
      finish();
      const reduced = motion.matches;
      button.hidden = reduced;
      fallback.hidden = !reduced;
      button.setAttribute('aria-pressed', String(paused));
      button.setAttribute('aria-label', paused ? 'Reprendre les domaines d’expertise' : 'Mettre en pause les domaines d’expertise');
      button.title = paused ? 'Reprendre l’animation' : 'Mettre en pause l’animation';
      const active = !reduced && !paused && !focused && !hovered && onScreen && !document.hidden;
      if (active) {
        if (!running) type();
        timer = setInterval(() => { current = (current + 1) % phrases.length; type(); }, 2000);
      }
      running = active;
    };
    button.addEventListener('click', () => { paused = !paused; update(); });
    button.addEventListener('focus', () => { focused = true; update(); });
    button.addEventListener('blur', () => { focused = false; update(); });
    button.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') { hovered = true; update(); } });
    button.addEventListener('pointerleave', () => { hovered = false; update(); });
    document.addEventListener('visibilitychange', update);
    motion.addEventListener('change', update);
    if ('IntersectionObserver' in window) new IntersectionObserver(entries => {
      onScreen = entries.some(entry => entry.isIntersecting);
      update();
    }).observe(rotator);
    update();
  });
})();
