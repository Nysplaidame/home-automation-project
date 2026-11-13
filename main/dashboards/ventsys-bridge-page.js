// Only the same-origin parent that bootstrapped this frame can publish display state.
let sequence = 0, expiryTimer;
const status = document.querySelector('#status'), failsafe = document.querySelector('#failsafe');
function offline() { clearTimeout(expiryTimer); status.textContent = 'Offline'; failsafe.textContent = ''; }
function exactKeys(value, keys) { return value && typeof value === 'object' && !Array.isArray(value) && Object.keys(value).sort().join(',') === keys.sort().join(','); }
window.addEventListener('message', event => {
  const m = event.data, now = Date.now(), session = document.documentElement.dataset.ventsysSession;
  if (event.origin !== location.origin || event.source !== window.parent || window.parent === window || !session || !m || m.sessionId !== session) { offline(); return; }
  const keys = ['version','type','sessionId','sequence','issuedAtMs','expiresAtMs'];
  if (m.type === 'state_snapshot') keys.push('payload');
  if (!exactKeys(m, keys) || m.version !== 1 || !['state_snapshot','offline'].includes(m.type) ||
      !Number.isSafeInteger(m.sequence) || m.sequence <= sequence || !Number.isSafeInteger(m.issuedAtMs) ||
      !Number.isSafeInteger(m.expiresAtMs) || m.issuedAtMs > now || m.expiresAtMs <= now ||
      m.expiresAtMs <= m.issuedAtMs || m.expiresAtMs - m.issuedAtMs >= 60000 ||
      (m.type === 'state_snapshot' && (!exactKeys(m.payload, ['failsafe']) || !['on','off','unknown'].includes(m.payload.failsafe)))) { offline(); return; }
  sequence = m.sequence;
  if (m.type === 'offline') { offline(); return; }
  status.textContent = 'Connected'; failsafe.textContent = 'Failsafe: ' + m.payload.failsafe;
  clearTimeout(expiryTimer); expiryTimer = setTimeout(offline, m.expiresAtMs - now);
});
window.addEventListener('pagehide', offline);
