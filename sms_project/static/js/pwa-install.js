/**
 * SMS (Student Management System) — PWA Installation & Service Worker Registration
 */

// 1. Register Service Worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/static/js/serviceworker.js')
      .then((reg) => {
        console.log('[PWA] Service Worker registered with scope:', reg.scope);
      })
      .catch((err) => {
        console.warn('[PWA] Service Worker registration failed:', err);
      });
  });
}

// 2. Install App Banner & Button Handling
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
  // Prevent mini-infobar from appearing on mobile
  e.preventDefault();
  deferredPrompt = e;

  // Show all install buttons on the page
  const installBtns = document.querySelectorAll('.pwa-install-btn');
  installBtns.forEach((btn) => {
    btn.classList.remove('d-none');
    btn.addEventListener('click', async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      console.log('[PWA] Install prompt outcome:', outcome);
      deferredPrompt = null;
      installBtns.forEach((b) => b.classList.add('d-none'));
    });
  });
});

// 3. Hide Install Button if already installed
window.addEventListener('appinstalled', () => {
  console.log('[PWA] App successfully installed');
  const installBtns = document.querySelectorAll('.pwa-install-btn');
  installBtns.forEach((btn) => btn.classList.add('d-none'));
});
