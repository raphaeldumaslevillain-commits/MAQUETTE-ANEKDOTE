(() => {
  const form = document.querySelector('[data-contact-form]');
  if (!form) return;
  const steps = [...form.querySelectorAll('[data-step]')];
  const indicators = [...form.querySelectorAll('[data-step-indicator]')];
  const status = form.querySelector('[data-form-status]');
  const submit = form.querySelector('[type=submit]');
  let current = 0;
  const show = (step, scroll = false) => {
    current = step;
    steps.forEach((element, index) => {element.hidden = index !== step;});
    indicators.forEach((element, index) => {
      element.classList.toggle('active', index === step);
      if (index === step) element.setAttribute('aria-current', 'step'); else element.removeAttribute('aria-current');
    });
    const drink = form.querySelector('[name=your-drink]:checked')?.value;
    const place = form.querySelector('[name=your-place]:checked')?.value;
    const recap = form.querySelector('[data-recap]');
    if (recap) recap.textContent = [drink, place].filter(Boolean).join(' / ');
    steps[step].querySelector('h2')?.focus({preventScroll: true});
    if (scroll) form.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
  };
  const advance = () => {
    const inputs = [...steps[current].querySelectorAll('input,select,textarea')];
    const invalid = inputs.find(input => !input.checkValidity());
    if (invalid) {invalid.reportValidity(); return;}
    show(Math.min(current + 1, steps.length - 1), true);
  };
  const choose = event => {
    const input = event.target;
    if (!input.matches('input[type=radio][name=your-drink],input[type=radio][name=your-place]') || !input.checked) return;
    if (input.closest('[data-step]') !== steps[current]) return;
    advance();
  };
  // Click also handles choosing the same option again after going back.
  // The active-step guard prevents click and change from advancing twice.
  form.addEventListener('click', choose);
  form.addEventListener('change', choose);
  form.querySelectorAll('[data-prev]').forEach(button => button.addEventListener('click', () => show(Math.max(0, current - 1), true)));
  // The static site keeps the existing Anekdote contact destination (CF7 form 547).
  // No new service receives this information. Never simulate a successful delivery.
  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (!form.checkValidity()) {form.reportValidity(); return;}
    submit.disabled = true;
    status.textContent = 'Votre message est en cours d’envoi…';
    const data = new FormData(form);
    data.set('_wpcf7', '547');
    data.set('_wpcf7_version', '6.1.6');
    data.set('_wpcf7_locale', 'fr_FR');
    data.set('_wpcf7_unit_tag', 'wpcf7-f547-o1');
    data.set('_wpcf7_container_post', '0');
    try {
      const response = await fetch(form.dataset.endpoint, {method: 'POST', body: data, signal: AbortSignal.timeout(20000)});
      if (!response.ok) throw new Error('HTTP error');
      const result = await response.json();
      if (result.status === 'mail_sent') {
        status.textContent = result.message;
        form.reset();
        submit.textContent = 'Message envoyé';
        submit.disabled = true;
      } else {
        status.textContent = result.message || 'Le message n’a pas été envoyé. Vous pouvez réessayer dans quelques instants.';
        if (Array.isArray(result.invalid_fields)) {
          for (const field of result.invalid_fields) {
            const input = form.elements.namedItem(field.field);
            if (input && 'setCustomValidity' in input) {
              input.setCustomValidity(field.message);
              input.addEventListener('input', () => input.setCustomValidity(''), {once: true});
            }
          }
          form.reportValidity();
        }
        submit.disabled = false;
      }
    } catch {
      status.textContent = 'L’envoi n’a pas pu être confirmé. Réessayez dans quelques instants.';
      submit.disabled = false;
    }
  });
  // Keep all form fields visible without JavaScript; collapse only after setup.
  show(0);
})();
