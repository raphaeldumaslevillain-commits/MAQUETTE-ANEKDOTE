(() => {
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const typingJobs = new Map();
  const stopTyping = deck => {
    const job = typingJobs.get(deck);
    if (!job) return;
    cancelAnimationFrame(job.frame);
    job.copy.remove();
    job.slide.classList.remove('is-typing');
    typingJobs.delete(deck);
  };
  const typeSlide = (deck, slide) => {
    stopTyping(deck);
    if (reduced.matches) return;
    // The visual clone types; the complete semantic text stays stable for readers.
    const copy = document.createElement('div');
    copy.className = 'typing-copy';
    copy.setAttribute('aria-hidden', 'true');
    copy.inert = true;
    [...slide.children].forEach(child => copy.append(child.cloneNode(true)));
    const walker = document.createTreeWalker(copy, NodeFilter.SHOW_TEXT);
    const nodes = [];
    let node;
    while ((node = walker.nextNode())) { nodes.push({node, text:node.textContent}); node.textContent = ''; }
    const total = nodes.reduce((sum, item) => sum + item.text.length, 0);
    const start = performance.now();
    const job = {copy, slide, frame:0};
    typingJobs.set(deck, job);
    slide.append(copy);
    slide.classList.add('is-typing');
    const tick = now => {
      if (reduced.matches) return stopTyping(deck);
      const progress = Math.min(1, (now - start) / 460);
      let budget = Math.ceil(total * progress);
      for (const item of nodes) { item.node.textContent = item.text.slice(0, Math.max(0, budget)); budget -= item.text.length; }
      if (progress < 1) job.frame = requestAnimationFrame(tick); else stopTyping(deck);
    };
    job.frame = requestAnimationFrame(tick);
  };
  document.querySelectorAll('[data-deck]').forEach(deck => {
    const slides = [...deck.querySelectorAll(':scope > .deck-stage > [data-slide]')];
    const tabs = [...deck.querySelectorAll(':scope > .deck-controls [data-deck-go]')];
    const status = deck.querySelector('[data-deck-status]');
    const next = deck.querySelector('[data-deck-next]');
    const previous = deck.querySelector('[data-deck-prev]');
    let current = 0;
    const show = (index, animate = true) => {
      stopTyping(deck);
      deck.dataset.direction = index < current ? 'previous' : 'next';
      current = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => {
        const active = i === current;
        slide.classList.toggle('active', active);
        slide.setAttribute('aria-hidden', String(!active));
        slide.inert = !active;
        tabs[i]?.setAttribute('aria-pressed', String(active));
      });
      if (deck.classList.contains('agency-deck')) {
        status.textContent = slides[current].querySelector('h2').textContent;
        next.setAttribute('aria-label', 'Lire la section suivante : ' + slides[(current + 1) % slides.length].querySelector('h2').textContent);
        if (animate) typeSlide(deck, slides[current]);
      } else if (status) status.textContent = `${current + 1} / ${slides.length}`;
    };
    deck.classList.add('enhanced');
    show(0, false);
    tabs.forEach((tab, i) => tab.addEventListener('click', () => show(i)));
    previous?.addEventListener('click', () => show(current - 1));
    next?.addEventListener('click', () => show(current + 1));
    deck.addEventListener('keydown', event => {
      if (!event.target.closest('.deck-controls')) return;
      if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
        event.preventDefault();
        show(current + (event.key === 'ArrowRight' ? 1 : -1));
        (tabs[current] || next).focus();
      }
    });
    if (deck.classList.contains('team-carousel')) {
      let start;
      deck.addEventListener('pointerdown', event => { if (event.pointerType !== 'mouse') start = {x:event.clientX, y:event.clientY}; }, {passive:true});
      deck.addEventListener('pointerup', event => {
        if (!start) return;
        const x = event.clientX - start.x, y = event.clientY - start.y;
        start = null;
        if (Math.abs(x) > 60 && Math.abs(x) > Math.abs(y) * 1.4) {
          deck.dataset.swiped = 'true';
          show(current + (x < 0 ? 1 : -1));
          setTimeout(() => delete deck.dataset.swiped, 300);
        }
      }, {passive:true});
      deck.addEventListener('pointercancel', () => { start = null; }, {passive:true});
    }
  });
  document.querySelectorAll('.expertise-accordion').forEach(group => {
    group.querySelectorAll('details').forEach(detail => detail.addEventListener('toggle', () => {
      if (detail.open) group.querySelectorAll('details').forEach(other => { if (other !== detail) other.open = false; });
    }));
  });
  // Logos stay monochrome and behave identically when the pointer passes over them.
  document.querySelectorAll('[data-marquee]').forEach(marquee => {
    let onScreen = true;
    const update = () => marquee.classList.toggle('offscreen', !onScreen || document.hidden);
    if ('IntersectionObserver' in window) new IntersectionObserver(entries => entries.forEach(entry => { onScreen = entry.isIntersecting; update(); })).observe(marquee);
    document.addEventListener('visibilitychange', update);
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
  counters.forEach(element => { element.dataset.final = element.textContent; });
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
      element.textContent = (element.dataset.prefix || '') + number + element.dataset.suffix;
      element.style.transform = `scale(${.94 + eased * .06})`;
      if (progress < 1) frames.set(element, requestAnimationFrame(tick)); else finish(element);
    };
    frames.set(element, requestAnimationFrame(tick));
  };
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { animate(entry.target); observer.unobserve(entry.target); } }), {threshold:.6});
    counters.forEach(element => observer.observe(element));
  }
  reduced.addEventListener('change', event => {
    if (event.matches) { counters.forEach(finish); [...typingJobs.keys()].forEach(stopTyping); }
  });
  document.querySelectorAll('[data-profile-photo]').forEach(photo => {
    const overlay = photo.querySelector('.photo-tastes');
    let pinned = false;
    const show = active => {
      photo.classList.toggle('show-tastes', active);
      photo.setAttribute('aria-expanded', String(active));
      overlay.setAttribute('aria-hidden', String(!active));
    };
    photo.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse') show(true); });
    photo.addEventListener('pointerleave', () => { if (!pinned && !photo.contains(document.activeElement)) show(false); });
    photo.addEventListener('focus', () => show(true));
    photo.addEventListener('blur', () => { pinned = false; show(false); });
    photo.addEventListener('click', () => {
      if (photo.closest('.team-carousel').dataset.swiped) return;
      pinned = !pinned;
      show(pinned);
    });
    photo.addEventListener('keydown', event => {
      if (event.key === 'Escape') { pinned = false; show(false); }
      if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); pinned = !pinned; show(pinned); }
    });
  });
})();
