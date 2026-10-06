(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.querySelectorAll('[data-deck]').forEach(deck => {
    const slides = [...deck.querySelectorAll(':scope > .deck-stage > [data-slide]')];
    const tabs = [...deck.querySelectorAll(':scope > .deck-controls [data-deck-go]')];
    let current = 0;
    const show = index => {
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        const active = i === current;
        slide.classList.toggle('active', active);
        slide.setAttribute('aria-hidden', String(!active));
        slide.inert = !active;
        tabs[i].setAttribute('aria-pressed', String(active));
      });
      deck.querySelector('[data-deck-status]').textContent = `${current + 1} / ${slides.length}`;
    };
    deck.classList.add('enhanced');
    show(0);
    tabs.forEach((tab, i) => tab.addEventListener('click', () => show(i)));
    deck.querySelector('[data-deck-prev]').addEventListener('click', () => show(current - 1));
    deck.querySelector('[data-deck-next]').addEventListener('click', () => show(current + 1));
    deck.addEventListener('keydown', event => {
      if (!event.target.closest('.deck-controls')) return;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        show(current + (event.key === 'ArrowRight' ? 1 : -1));
        tabs[current].focus();
      }
    });
  });
  document.querySelectorAll('.expertise-accordion').forEach(group => {
    group.querySelectorAll('details').forEach(detail => detail.addEventListener('toggle', () => {
      if (detail.open) group.querySelectorAll('details').forEach(other => {
        if (other !== detail) other.open = false;
      });
    }));
  });
  document.querySelectorAll('[data-marquee]').forEach(marquee => {
    const button = marquee.querySelector('[data-marquee-toggle]');
    button.addEventListener('click', () => {
      const paused = marquee.classList.toggle('paused');
      marquee.classList.toggle('resume-requested', !paused);
      button.setAttribute('aria-pressed', String(paused));
      button.innerHTML = paused ? 'Reprendre <span aria-hidden="true">▷</span>' : 'Pause <span aria-hidden="true">Ⅱ</span>';
    });
    button.addEventListener('blur', () => marquee.classList.remove('resume-requested'));
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver(entries => entries.forEach(entry => marquee.classList.toggle('offscreen', !entry.isIntersecting)));
      observer.observe(marquee);
    }
    document.addEventListener('visibilitychange', () => marquee.classList.toggle('offscreen', document.hidden));
  });
  const counters = [...document.querySelectorAll('[data-count]')];
  const frames = new Map();
  const finish = element => {
    if (frames.has(element)) cancelAnimationFrame(frames.get(element));
    element.textContent = element.dataset.final;
    element.style.transform = '';
    element.dataset.counted = 'true';
    frames.delete(element);
  };
  counters.forEach(element => element.dataset.final = element.textContent);
  const animate = element => {
    if (reduced.matches) return finish(element);
    const value = Number(element.dataset.count), decimals = Number(element.dataset.decimals);
    const start = performance.now();
    const tick = now => {
      if (reduced.matches) return finish(element);
      const progress = Math.min(1, (now - start) / 720);
      const eased = 1 - Math.pow(1 - progress, 4);
      let number = (value * eased).toFixed(decimals);
      number = element.dataset.separator === ' ' ? number.replace(/\B(?=(\d{3})+(?!\d))/g, ' ') : number.replace('.', element.dataset.separator);
      element.textContent = number + element.dataset.suffix;
      element.style.transform = `scale(${.94 + eased * .06})`;
      if (progress < 1) frames.set(element, requestAnimationFrame(tick));
      else finish(element);
    };
    frames.set(element, requestAnimationFrame(tick));
  };
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { animate(entry.target); observer.unobserve(entry.target); }
    }), {threshold:.6});
    counters.forEach(element => observer.observe(element));
  }
  reduced.addEventListener('change', event => { if (event.matches) counters.forEach(finish); });
  document.querySelectorAll('.person').forEach(person => {
    const toggle = person.querySelector('[data-person-toggle]');
    const bio = person.querySelector('[data-person-bio]');
    const anecdote = person.querySelector('[data-person-anecdote]');
    toggle.addEventListener('click', () => {
      const active = toggle.getAttribute('aria-pressed') !== 'true';
      toggle.setAttribute('aria-pressed', String(active));
      bio.hidden = active;
      anecdote.hidden = !active;
      toggle.querySelector('span').textContent = active ? 'Le portrait' : 'Une Anekdote';
      person.querySelector('[data-person-label]').textContent = active ? 'Une Anekdote' : 'Le portrait';
    });
    const photo = person.querySelector('.person-photo');
    const tasteToggle = photo.querySelector('[data-tastes-toggle]');
    const overlay = photo.querySelector('.photo-tastes');
    let pinned = false;
    const showTastes = active => {
      photo.classList.toggle('show-tastes', active);
      tasteToggle.setAttribute('aria-expanded', String(active));
      overlay.setAttribute('aria-hidden', String(!active));
    };
    showTastes(false);
    photo.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') showTastes(true); });
    photo.addEventListener('pointerleave', () => { if (!pinned && !photo.contains(document.activeElement)) showTastes(false); });
    tasteToggle.addEventListener('focus', () => showTastes(true));
    photo.addEventListener('focusout', event => { if (!pinned && !photo.contains(event.relatedTarget)) showTastes(false); });
    tasteToggle.addEventListener('click', () => { pinned = !pinned; showTastes(pinned); });
    tasteToggle.addEventListener('keydown', event => { if (event.key === 'Escape') { pinned = false; showTastes(false); } });
  });
})();
