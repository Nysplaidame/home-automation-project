/* Nutrition label scanning: images and recognised text stay in this browser. */
(function (root) {
  'use strict';
  const KEYS = ['calories', 'protein', 'carbs', 'fat'];
  function parseLabel(text, column = null) {
    const rows = { calories: [], protein: [], carbs: [], fat: [] };
    const kjRows = [];
    const warnings = [];
    const lines = String(text).replace(/\r/g, '').split('\n').map(line => line.toLowerCase().replace(/(\d),(\d)/g, '$1.$2').replace(/\d+(?:\.\d+)?\s*%/g, '').replace(/k\s*c\s*a\s*[l1i](?:s)?\b/g, 'kcal'));
    for (let index = 0; index < lines.length - 1; index++) {
      if (/^\s*(?:kcal|kj)\s*$/.test(lines[index + 1]) && /\d/.test(lines[index]) && !/(?:kcal|kj)\b/.test(lines[index])) { lines[index] += ' ' + lines[index + 1].trim(); lines[index + 1] = ''; }
    }
    const number = '(?<![\\w.,])<?\\s*(?:\\d+(?:\\.\\d+)?|\\.\\d+)';
    const readNumbers = line => [...line.matchAll(new RegExp(number + '(?![\\w.,])', 'g'))].map(match => match[0].trim());
    const withUnit = (line, unit) => [...line.matchAll(new RegExp('(' + number + ')\\s*' + unit + '\\b', 'g'))].map(match => match[1].trim());
    for (let index = 0; index < lines.length; index++) {
      let line = lines[index];
      const energy = /\b(?:energy|calories)\b|kcal\b|kj\b/.test(line);
      let key = /^\s*(?:total\s+)?protein\b/.test(line) ? 'protein' : /^\s*(?:total\s+)?carbohydrates?\b/.test(line) ? 'carbs' : /^\s*(?:total\s+)?fat\b/.test(line) ? 'fat' : energy ? 'calories' : null;
      if (!key) continue;
      if (/-\s*\d|\b(?:mg|micrograms|milligrams)\b|\d\s*(?:mg|µg)\b|less than/.test(line)) { warnings.push(`${key}: unsupported or uncertain value; enter manually.`); continue; }
      let values = [];
      if (key === 'calories') {
        values = withUnit(line, 'kcal');
        const header = line.match(/(kj|kcal)\s*\/\s*(kj|kcal)/);
        if (!values.length && header && header[1] !== header[2]) {
          let rest = line.slice(header.index + header[0].length).replace(/^\s*[):]/, '');
          if (!readNumbers(rest).length && /^[\s\d.,/()<]+$/.test(lines[index + 1] || '')) rest = lines[++index];
          const pairs = readNumbers(rest);
          if (pairs.length && pairs.length % 2 === 0) values = pairs.filter((_, position) => position % 2 === (header[1] === 'kcal' ? 0 : 1));
        }
        if (!values.length && /^\s*(?:energy|calories|kcal)\s*[:()]?\s*$/.test(line) && /^[\s\d.,()<]+$/.test(lines[index + 1] || '')) values = readNumbers(lines[++index]);
        if (!values.length && !/kj\b/.test(line)) values = readNumbers(line.replace(/calories|energy|kcal/g, ''));
        const kj = withUnit(line, 'kj'); if (kj.length) kjRows.push(kj);
      } else {
        const rest = line.replace(/^(?:\s*)(?:total\s+)?(?:protein|carbohydrates?|fat)\b\s*:?/, '');
        values = withUnit(rest, 'g');
        if (!values.length && /^[\s\d.,()<]+$/.test(rest)) values = readNumbers(rest);
      }
      if (values.length) rows[key].push(values);
    }
    // Prefer labelled kcal. Convert labelled kJ only when no kcal values were read.
    if (!rows.calories.length && kjRows.length) {
      rows.calories = kjRows.map(row => row.map(raw => raw.includes('<') ? raw : String(Math.round(Number(raw) / 4.184 * 100) / 100)));
      warnings.push('Calories converted from kJ; check the energy line against the label.');
    }
    const multiColumn = Object.values(rows).some(entries => entries.some(row => row.length > 1));
    const values = {};
    for (const key of KEYS) {
      const entries = rows[key];
      if (entries.length !== 1) { warnings.push(`${key}: ${entries.length ? 'multiple matching rows; enter manually' : 'not read; enter manually'}.`); continue; }
      if (multiColumn && column === null) continue;
      const raw = entries[0][column === null ? 0 : column];
      if (!raw || raw.includes('<')) { warnings.push(`${key}: uncertain or missing value; enter manually.`); continue; }
      const value = Number(raw);
      if (!Number.isFinite(value) || value < 0) continue;
      values[key] = value;
    }
    if (multiColumn && column === null) warnings.push('Multiple nutrition columns found. Choose the column matching your label basis.');
    const bases = [...String(text).toLowerCase().matchAll(/(?:per\s*)?100\s*(ml|g)\b/g)].map(match => '100' + match[1]);
    return { values, warnings, multiColumn, basis: new Set(bases).size === 1 ? bases[0] : null };
  }
  let libraryPromise;
  function loadLibrary() {
    if (root.Tesseract) return Promise.resolve(root.Tesseract);
    if (!libraryPromise) libraryPromise = new Promise((resolve, reject) => {
      const script = document.createElement('script'); script.src = '/static/ocr/tesseract.min.js';
      script.onload = () => resolve(root.Tesseract);
      script.onerror = () => { script.remove(); libraryPromise = null; reject(Error('OCR could not load. Try again when connected to Recomp.')); };
      document.head.append(script);
    });
    return libraryPromise;
  }
  function attach(form, foodBasis) {
    const node = (tag, props = {}) => Object.assign(document.createElement(tag), props);
    const panel = node('details'); const summary = node('summary', { textContent: 'Scan nutrition label' }); panel.append(summary);
    panel.append(node('p', { className: 'v2-diet-note', textContent: 'Take or choose a clear photo of the nutrition table. Recognition happens on this device. Review every value and its basis before applying.' }));
    const controls = node('div', { className: 'v2-toolbar' });
    const camera = node('input', { type: 'file', accept: 'image/*', capture: 'environment' }); camera.setAttribute('aria-label', 'Take a nutrition label photo');
    const upload = node('input', { type: 'file', accept: 'image/*' }); upload.setAttribute('aria-label', 'Choose a nutrition label photo');
    function field(label, control) { const wrapper = node('label', { className: 'v2-field' }); wrapper.append(node('span', { textContent: label }), control); return wrapper; }
    controls.append(field('Take photo', camera), field('Choose photo', upload)); panel.append(controls);
    const canvas = node('canvas'); canvas.style.cssText = 'display:none;max-width:100%;height:auto;margin:12px 0'; panel.append(canvas);
    const crop = node('div', { className: 'v2-grid' }); const edges = {};
    for (const edge of ['Left', 'Top', 'Right', 'Bottom']) { const control = node('input', { type: 'number', min: '0', max: '90', step: '1', value: '0' }); edges[edge] = control; crop.append(field(`Trim ${edge.toLowerCase()} (%)`, control)); }
    panel.append(crop);
    const actions = node('div', { className: 'v2-toolbar' });
    const rotate = node('button', { className: 'v2-btn', type: 'button', textContent: 'Rotate photo', disabled: true });
    const scan = node('button', { className: 'v2-btn', type: 'button', textContent: 'Read label', disabled: true });
    const cancel = node('button', { className: 'v2-btn', type: 'button', textContent: 'Cancel scan', disabled: true }); actions.append(rotate, scan, cancel); panel.append(actions);
    const status = node('p', { className: 'v2-diet-note' }); status.setAttribute('role', 'status'); panel.append(status);
    const review = node('div'); review.hidden = true; panel.append(review);
    const text = node('textarea', { rows: 7 }); review.append(field('Recognised text — correct it if needed', text));
    const basis = node('select'); [['', 'Choose label basis'], ['100g', 'Per 100g'], ['100ml', 'Per 100ml'], ['serving-g', 'Per serving (grams)'], ['serving-ml', 'Per serving (millilitres)']].forEach(([value, textContent]) => basis.append(node('option', { value, textContent })));
    const amount = node('input', { type: 'number', min: '0.1', step: 'any', placeholder: 'e.g. 30' }); amount.disabled = true;
    const column = node('select'); [['', 'Choose column if more than one'], ['0', 'First value column'], ['1', 'Second value column'], ['2', 'Third value column']].forEach(([value, textContent]) => column.append(node('option', { value, textContent })));
    review.append(field('Values on label are', basis), field('Serving weight or volume (g/ml)', amount), field('Nutrition column (left to right)', column));
    const preview = node('div', { className: 'v2-grid' }); const inputs = {};
    for (const key of KEYS) { inputs[key] = node('input', { type: 'number', min: '0', step: 'any' }); preview.append(field(key === 'calories' ? 'Calories (kcal)' : `${key[0].toUpperCase() + key.slice(1)} (g)`, inputs[key])); }
    review.append(preview);
    const warnings = node('p', { className: 'v2-diet-note' }); review.append(warnings);
    const confirmed = node('input', { type: 'checkbox' }); review.append(field('I checked the values, column and basis against the label', confirmed));
    const apply = node('button', { className: 'v2-btn primary', type: 'button', textContent: 'Apply reviewed values' }); review.append(apply);
    let image = null, worker = null, workerPromise = null, workerEpoch = 0, idleTimer = null, generation = 0, busy = false, rotation = 0;
    async function releaseWorker() {
      clearTimeout(idleTimer); workerEpoch++; workerPromise = null;
      if (worker) { const old = worker; worker = null; await old.terminate().catch(() => {}); }
    }
    function scheduleIdleRelease() { clearTimeout(idleTimer); idleTimer = setTimeout(() => { if (!busy) void releaseWorker(); }, 60000); }
    function prepareWorker() {
      if (worker) return Promise.resolve(worker);
      if (workerPromise) return workerPromise;
      const epoch = workerEpoch;
      workerPromise = (async () => {
        const Tesseract = await loadLibrary(); if (epoch !== workerEpoch) throw Error('Preparation cancelled');
        const created = await Tesseract.createWorker('eng', 1, {
          workerPath: '/static/ocr/worker.min.js', corePath: '/static/ocr', langPath: '/static/ocr/eng-fast-v1', cachePath: 'recomp-eng-fast-v1', workerBlobURL: false,
          logger: message => { if (epoch === workerEpoch && panel.open) status.textContent = `${message.status}${Number.isFinite(message.progress) ? ' ' + Math.round(message.progress * 100) + '%' : ''}`; }
        });
        if (epoch !== workerEpoch) { await created.terminate(); throw Error('Preparation cancelled'); }
        worker = created; if (!busy) scheduleIdleRelease(); return created;
      })().catch(error => { if (epoch === workerEpoch) workerPromise = null; throw error; });
      return workerPromise;
    }
    panel.addEventListener('toggle', () => {
      if (!panel.open || busy) return;
      const epoch = workerEpoch;
      status.textContent = worker ? 'Reader ready. Choose a photo.' : 'Preparing reader… You can choose and crop a photo while it loads.';
      void prepareWorker().then(() => { if (epoch === workerEpoch && !busy && panel.open) status.textContent = image ? 'Reader ready. Trim to the nutrition table, then read the label.' : 'Reader ready. Choose a photo.'; }).catch(() => { if (epoch === workerEpoch && !busy && panel.open) status.textContent = 'Reader could not prepare. Read label will retry; manual entry is still available.'; });
    });
    function draw() {
      if (!image) return;
      const sourceWidth = image.width, sourceHeight = image.height;
      const scale = Math.min(1, 2000 / Math.max(sourceWidth, sourceHeight));
      const w = Math.round(sourceWidth * scale), h = Math.round(sourceHeight * scale);
      const rotated = document.createElement('canvas'); rotated.width = rotation % 2 ? h : w; rotated.height = rotation % 2 ? w : h;
      const ctx = rotated.getContext('2d'); ctx.translate(rotated.width / 2, rotated.height / 2); ctx.rotate(rotation * Math.PI / 2); ctx.drawImage(image, -w / 2, -h / 2, w, h);
      const e = Object.fromEntries(Object.entries(edges).map(([key, control]) => [key, Math.min(90, Math.max(0, Number(control.value) || 0)) / 100]));
      if (e.Left + e.Right >= .95 || e.Top + e.Bottom >= .95) { scan.disabled = true; status.textContent = 'Leave at least 5% of the photo visible.'; return; }
      canvas.width = Math.max(1, Math.round(rotated.width * (1 - e.Left - e.Right))); canvas.height = Math.max(1, Math.round(rotated.height * (1 - e.Top - e.Bottom)));
      canvas.getContext('2d').drawImage(rotated, rotated.width * e.Left, rotated.height * e.Top, canvas.width, canvas.height, 0, 0, canvas.width, canvas.height); canvas.style.display = 'block'; scan.disabled = busy;
    }
    function extract() { const result = parseLabel(text.value, column.value === '' ? null : Number(column.value)); KEYS.forEach(key => { inputs[key].value = result.values[key] ?? ''; }); warnings.textContent = result.warnings.join(' '); confirmed.checked = false; }
    column.onchange = extract; text.oninput = extract;
    basis.onchange = () => { amount.disabled = !basis.value.startsWith('serving'); confirmed.checked = false; };
    amount.oninput = () => { confirmed.checked = false; }; KEYS.forEach(key => { inputs[key].oninput = () => { confirmed.checked = false; }; });
    Object.values(edges).forEach(control => { control.oninput = draw; });
    rotate.onclick = () => { rotation = (rotation + 1) % 4; draw(); };
    async function stop(release = true) { generation++; if (release) await releaseWorker(); busy = false; cancel.disabled = true; rotate.disabled = !image; camera.disabled = upload.disabled = false; Object.values(edges).forEach(control => { control.disabled = false; }); draw(); if (!release && worker) scheduleIdleRelease(); }
    cancel.onclick = () => { void stop(); status.textContent = 'Scan cancelled. You can still enter values manually.'; };
    async function choose(event) {
      await stop(busy); const current = ++generation; const file = event.target.files[0]; if (!file) return;
      review.hidden = true; confirmed.checked = false; scan.disabled = true; rotate.disabled = true; canvas.style.display = 'none'; image?.close(); image = null;
      try {
        if (!file.type.startsWith('image/') || file.size > 20 * 1024 * 1024) throw Error('Choose an image smaller than 20 MB.');
        const decoded = await createImageBitmap(file); if (current !== generation) { decoded.close(); return; } image = decoded;
        if (image.width * image.height > 40000000) { image.close(); image = null; throw Error('Photo is too large. Choose an image below 40 megapixels.'); }
        rotation = 0; Object.values(edges).forEach(control => { control.value = '0'; }); draw(); rotate.disabled = false; status.textContent = 'Trim to the nutrition table, then read the label.';
      } catch (error) { status.textContent = error.message || 'Photo could not be opened. Try a JPEG or PNG.'; }
    }
    camera.onchange = upload.onchange = choose;
    scan.onclick = async () => {
      busy = true; scan.disabled = rotate.disabled = camera.disabled = upload.disabled = true; cancel.disabled = false; Object.values(edges).forEach(control => { control.disabled = true; }); review.hidden = true;
      clearTimeout(idleTimer); const current = ++generation; let timer, failed = false;
      try {
        status.textContent = 'Loading label reader…'; timer = setTimeout(() => { if (current === generation) { void stop(); status.textContent = 'Scan timed out. Try a smaller crop or enter values manually.'; } }, 90000);
        const reader = await prepareWorker(); if (current !== generation) return;
        const result = await reader.recognize(canvas); if (current !== generation) return;
        text.value = result.data.text; column.value = ''; basis.value = parseLabel(text.value).basis || ''; basis.onchange(); extract(); review.hidden = false;
        status.textContent = 'Check the recognised text and choose the correct column and basis. Unread values remain blank.';
      } catch (error) { failed = true; if (current === generation) status.textContent = 'Could not read this label. Try a clearer photo or enter values manually.'; }
      finally { clearTimeout(timer); if (current === generation) await stop(failed); }
    };
    apply.onclick = () => {
      if (parseLabel(text.value).multiColumn && column.value === '') { warnings.textContent = 'Choose the nutrition column matching the label basis before applying.'; return; }
      const numbers = Object.fromEntries(KEYS.map(key => [key, inputs[key].value.trim() === '' ? NaN : Number(inputs[key].value)]));
      if (!confirmed.checked || !basis.value || KEYS.some(key => !Number.isFinite(numbers[key]) || numbers[key] < 0)) { warnings.textContent = 'Enter all four values, choose the basis and confirm your review.'; return; }
      const serving = basis.value.startsWith('serving'); const size = Number(amount.value);
      if (serving && (!Number.isFinite(size) || size <= 0)) { warnings.textContent = 'Enter the serving weight or volume to convert to per 100g/ml.'; return; }
      const factor = serving ? 100 / size : 1;
      if (KEYS.some(key => numbers[key] * factor > (key === 'calories' ? 1000 : 100))) { warnings.textContent = 'Values exceed a plausible per-100 basis. Check the column, decimal points and serving size.'; return; }
      KEYS.forEach(key => { const control = form.querySelector(`[name="${key}"]`); control.value = String(Math.round(numbers[key] * factor * 100) / 100); control.dispatchEvent(new Event('input', { bubbles: true })); });
      foodBasis.value = basis.value.endsWith('ml') ? '100ml' : '100g'; status.textContent = 'Reviewed values applied. Check the food name and save using the food form.'; panel.open = false;
    };
    const onVisibility = () => { if (document.hidden) { void stop(); if (busy) status.textContent = 'Scan stopped while the app was in the background. Read label to retry.'; } };
    document.addEventListener('visibilitychange', onVisibility);
    const observer = new MutationObserver(() => { if (!form.isConnected) { observer.disconnect(); document.removeEventListener('visibilitychange', onVisibility); void stop(); image?.close(); image = null; } });
    observer.observe(document.body, { childList: true, subtree: true });
    return panel;
  }
  root.NutritionOCR = { parseLabel, attach };
  if (typeof module !== 'undefined' && module.exports) module.exports = { parseLabel };
})(typeof window === 'undefined' ? globalThis : window);
