(() => {
  const CARD_SELECTOR = '[id^="portal-"]:not(#portal-preview-dock)';
  const PREVIEW_CLASS = 'portal-preview-trigger';
  let observerQueued = false;
  let previousFocus = null;
  let previewLoadTimer = null;

  function setPreviewLoading(dock, loading) {
    window.clearTimeout(previewLoadTimer);
    dock.classList.toggle('is-loading', loading);
    if (!loading) return;

    // Cross-origin iframe failures do not provide a reliable error event. Do
    // not leave a loading veil over a working frame or its controls forever.
    previewLoadTimer = window.setTimeout(() => {
      dock.classList.remove('is-loading');
      dock.classList.add('preview-load-slow');
    }, 2500);
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
          <span class="portal-preview-hint">If a service blocks embedding, use Open tab.</span>
          <div class="portal-preview-actions">
            <button type="button" data-preview-action="reload">Reload</button>
            <a data-preview-action="external" href="#" target="_blank" rel="noreferrer">Open tab</a>
            <button type="button" data-preview-action="close">Close</button>
          </div>
        </header>
        <div class="portal-preview-frame-wrap">
          <div class="portal-preview-loading">Loading preview…</div>
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

    dock.querySelector('[data-preview-action="close"]').addEventListener('click', closePreview);
    dock.querySelector('[data-preview-action="reload"]').addEventListener('click', () => {
      const frame = dock.querySelector('.portal-preview-frame');
      const current = frame.dataset.src;
      if (!current) return;
      setPreviewLoading(dock, true);
      frame.src = 'about:blank';
      requestAnimationFrame(() => { frame.src = current; });
    });
    dock.querySelector('.portal-preview-frame').addEventListener('load', () => {
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
      layoutGroups.append(dock);
      return;
    }
    const tabs = document.getElementById('tabs');
    if (tabs) tabs.after(dock);
    else document.querySelector('#information-widgets, main, body').append(dock);
  }

  function openPreview(card, href) {
    const dock = getPreviewDock();
    const { name } = getServiceName(card);
    const frame = dock.querySelector('.portal-preview-frame');
    previousFocus = document.activeElement;
    placePreviewDock(dock);
    dock.querySelector('#portal-preview-title').textContent = name;
    dock.querySelector('[data-preview-action="external"]').href = href;
    frame.dataset.src = href;
    dock.hidden = false;
    dock.classList.remove('preview-load-slow');
    setPreviewLoading(dock, true);
    frame.src = href;
    dock.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    dock.querySelector('[data-preview-action="close"]').focus({ preventScroll: true });
  }

  function closePreview() {
    const dock = document.getElementById('portal-preview-dock');
    if (!dock || dock.hidden) return;
    const frame = dock.querySelector('.portal-preview-frame');
    frame.src = 'about:blank';
    frame.dataset.src = '';
    dock.hidden = true;
    setPreviewLoading(dock, false);
    dock.classList.remove('preview-load-slow');
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
