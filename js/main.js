(() => {
  // Native controls remain available even when JavaScript is unavailable.
  const mediaDialog = document.querySelector('#video-dialog');
  const dialogPlayer = mediaDialog?.querySelector('video');
  let previousFocus;
  document.querySelectorAll('[data-video-open]').forEach(button => {
    button.addEventListener('click', () => {
      if (!mediaDialog || !dialogPlayer) return;
      previousFocus = button;
      mediaDialog.querySelector('[data-video-title]').textContent = button.dataset.title || 'Le film Anekdote';
      dialogPlayer.src = button.dataset.videoOpen;
      mediaDialog.showModal();
      dialogPlayer.play().catch(() => {});
    });
  });
  mediaDialog?.querySelector('[data-video-close]')?.addEventListener('click', () => mediaDialog.close());
  mediaDialog?.addEventListener('close', () => {
    dialogPlayer.pause();
    dialogPlayer.removeAttribute('src');
    dialogPlayer.load();
    previousFocus?.focus();
  });
  document.querySelectorAll('[data-lazy-video]').forEach(video => {
    // The browser fetches no video until the visitor chooses to play it.
    video.preload = 'none';
  });
})();
