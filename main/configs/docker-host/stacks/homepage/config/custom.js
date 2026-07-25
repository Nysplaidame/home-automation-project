(() => {
  const CARD_SELECTOR = '[id^="portal-"]:not(#portal-preview-dock)';
  const PREVIEW_CLASS = 'portal-preview-trigger';
  const PREVIEW_PROXY_PORTS = new Map([
    ['192.168.20.102:8091', 8180],
    ['192.168.20.102:8000', 8181],
    ['192.168.20.102:8088', 8182],
    ['192.168.10.10:8006', 8183],
    ['192.168.10.1', 8184],
    ['192.168.10.12', 8185],
    ['192.168.60.10:3001', 8186],
    ['192.168.40.50', 8187],
  ]);
  let observerQueued = false;
  let previousFocus = null;
  let previewLoadTimer = null;

  function setPreviewMessage(dock, title, detail) {
    dock.querySelector('.portal-preview-loading strong').textContent = title;
    dock.querySelector('.portal-preview-loading span').textContent = detail;
  }

  function setPreviewLoading(dock, loading) {
    window.clearTimeout(previewLoadTimer);
    dock.classList.toggle('is-loading', loading);
    if (!loading) return;

    // Cross-origin iframe failures do not provide a reliable error event. Do
    // not leave a loading veil over a working frame or its controls forever.
    previewLoadTimer = window.setTimeout(() => {
      dock.classList.remove('is-loading');
      dock.classList.add('preview-load-slow');
    }, 6000);
  }

  function getServiceName(card) {
    const link =
      [...card.querySelectorAll('a[href]')].find((anchor) => anchor.querySelector('p')) ||
      card.querySelector('a[href]');
    if (!link) return { href: null, name: 'Service' };
    const copy = link.cloneNode(true);
    copy.querySelectorAll('p, img, svg').forEach((element) => element.remove());
    return { href: link.href, name: copy.textContent.trim() || 'Service' };
  }

  function getFrameHref(href) {
    try {
      const url = new URL(href);
      const port = PREVIEW_PROXY_PORTS.get(url.host);
      if (!port) return href;
      return `http://${window.location.hostname}:${port}${url.pathname}${url.search}${url.hash}`;
    } catch {
      return href;
    }
  }

  function getPreviewDock() {
    let dock = document.getElementById('portal-preview-dock');
    if (dock) return dock;

    dock = document.createElement('section');
    dock.id = 'portal-preview-dock';
    dock.className = 'portal-preview-dock';
    dock.hidden = true;
    dock.setAttribute('role', 'region');
    dock.setAttribute('aria-labelledby', 'portal-preview-title');
    dock.innerHTML = `
      <div class="portal-preview-shell">
        <header class="portal-preview-toolbar">
          <div class="portal-preview-heading">
            <span class="portal-preview-kicker">Embedded workspace</span>
            <strong id="portal-preview-title">Service</strong>
          </div>
          <span class="portal-preview-hint">Some services block embedding; Open tab always remains available.</span>
          <div class="portal-preview-actions">
            <button type="button" data-preview-action="reload">Reload</button>
            <a data-preview-action="external" href="#" target="_blank" rel="noopener noreferrer">Open tab</a>
            <button type="button" data-preview-action="close">Close</button>
          </div>
        </header>
        <div class="portal-preview-frame-wrap">
          <div class="portal-preview-loading" role="status" aria-live="polite">
            <strong>Loading preview&hellip;</strong>
            <span>If this remains blank, the service is refusing to be embedded. Use Open tab.</span>
          </div>
          <iframe
            class="portal-preview-frame"
            title="Embedded portal preview"
            referrerpolicy="same-origin"
            allow="clipboard-read; clipboard-write; fullscreen"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    `;

    dock.querySelector('.portal-preview-frame').addEventListener('load', (event) => {
      const frame = event.currentTarget;
      if (!frame.dataset.src || frame.src === 'about:blank') return;
      setPreviewLoading(dock, false);
      dock.classList.remove('preview-load-slow');
    });

    // Keep the workspace below the active portal content, rather than between
    // the tab picker and its cards. Homepage replaces #layout-groups on tab
    // changes, so openPreview also calls placePreviewDock() before displaying.
    placePreviewDock(dock);
    return dock;
  }

  function placePreviewDock(dock) {
    const layoutGroups = document.getElementById('layout-groups');
    if (layoutGroups) {
      // Re-appending an existing iframe detaches and reloads it. Because that
      // DOM move is itself observed, doing it unconditionally creates a loop
      // that leaves previews blank and moves controls during pointer clicks.
      if (dock.previousElementSibling !== layoutGroups) layoutGroups.after(dock);
      return;
    }
    const tabs = document.getElementById('tabs');
    if (tabs) {
      if (dock.previousElementSibling !== tabs) tabs.after(dock);
      return;
    }
    const fallback = document.querySelector('#information-widgets, main, body');
    if (fallback && dock.parentElement !== fallback) fallback.append(dock);
  }

  function openPreview(card, href) {
    const dock = getPreviewDock();
    const { name } = getServiceName(card);
    const frame = dock.querySelector('.portal-preview-frame');
    previousFocus = document.activeElement;
    placePreviewDock(dock);
    dock.querySelector('#portal-preview-title').textContent = name;
    dock.dataset.href = href;
    dock.querySelector('[data-preview-action="external"]').href = href;
    dock.hidden = false;
    dock.classList.remove('preview-load-slow', 'preview-blocked');
    setPreviewMessage(
      dock,
      'Loading preview…',
      'If this remains blank, the service is refusing to be embedded. Use Open tab.',
    );
    const frameHref = getFrameHref(href);
    frame.dataset.src = frameHref;
    setPreviewLoading(dock, true);
    frame.src = frameHref;
    dock.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    dock.querySelector('[data-preview-action="close"]').focus({ preventScroll: true });
  }

  function closePreview() {
    const dock = document.getElementById('portal-preview-dock');
    if (!dock || dock.hidden) return;
    const frame = dock.querySelector('.portal-preview-frame');
    frame.src = 'about:blank';
    frame.dataset.src = '';
    dock.dataset.href = '';
    dock.querySelector('[data-preview-action="external"]').href = '#';
    dock.hidden = true;
    setPreviewLoading(dock, false);
    dock.classList.remove('preview-load-slow', 'preview-blocked');
    if (previousFocus instanceof HTMLElement) previousFocus.focus();
  }

  function decorateHeader() {
    const header = document.getElementById('widgets-wrap');
    if (!header) return;
    if (!header.querySelector('.portal-brand')) {
      const brand = document.createElement('div');
      brand.className = 'portal-brand';
      brand.innerHTML = '<span class="portal-brand-kicker">Household control plane</span><strong>Home Operations</strong>';
      header.prepend(brand);
    }

    const right = document.getElementById('information-widgets-right');
    const resource = [...header.children].find((element) => element.classList.contains('widget-container'));
    const search = right?.querySelector('.information-widget-search');
    if (right && resource && search && resource.parentElement !== right) {
      search.after(resource);
    }
  }

  function decorateCards() {
    document.querySelectorAll(CARD_SELECTOR).forEach((card) => {
      if (card.querySelector(`.${PREVIEW_CLASS}`)) return;
      const { href, name } = getServiceName(card);
      if (!href) return;

      const button = document.createElement('button');
      button.type = 'button';
      button.className = PREVIEW_CLASS;
      button.setAttribute('aria-label', `Preview ${name} inside the portal`);
      button.title = 'Preview inside portal';
      button.innerHTML = `
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M4 5h16v11H4zM8 20h8M12 16v4"/>
        </svg>
        <span>Preview</span>
      `;
      button.addEventListener('click', (event) => {
        event.preventDefault();
        event.stopPropagation();
        openPreview(card, href);
      });
      card.appendChild(button);
    });
  }

  function queueDecoration() {
    if (observerQueued) return;
    observerQueued = true;
    requestAnimationFrame(() => {
      observerQueued = false;
      decorateHeader();
      decorateCards();
      const dock = document.getElementById('portal-preview-dock');
      if (dock) placePreviewDock(dock);
    });
  }

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') closePreview();
  });

  // A preview belongs to the active Homepage tab. Close it before Homepage
  // replaces that tab's card grid so it cannot linger above the next layout.
  document.addEventListener('click', (event) => {
    const tab = event.target.closest('[role="tab"]');
    if (tab && tab.getAttribute('aria-selected') !== 'true') closePreview();
  }, true);
  window.addEventListener('hashchange', closePreview);

  // Delegate toolbar actions from the document. Homepage can replace or move
  // generated layout nodes during tab updates; delegation keeps these controls
  // live even when that happens.
  document.addEventListener('click', (event) => {
    const control = event.target.closest('[data-preview-action]');
    if (!control) return;
    const dock = control.closest('#portal-preview-dock');
    if (!dock) return;

    const action = control.dataset.previewAction;
    if (action === 'external') return;

    event.preventDefault();
    event.stopPropagation();
    if (action === 'close') {
      closePreview();
      return;
    }
    if (action === 'reload') {
      const frame = dock.querySelector('.portal-preview-frame');
      const current = frame.dataset.src;
      if (!current) return;
      dock.classList.remove('preview-load-slow');
      setPreviewLoading(dock, true);
      frame.src = 'about:blank';
      requestAnimationFrame(() => {
        requestAnimationFrame(() => { frame.src = current; });
      });
    }
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', queueDecoration, { once: true });
  } else {
    queueDecoration();
  }

  new MutationObserver(queueDecoration).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
})();
