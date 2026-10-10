"""A/B player: a Gradio HTML component driven by Web Audio.

Python sends one JSON payload per render: source (A, loudness-matched) and result (B) as WAV data
URIs plus the timing needed to map positions between them (B has bleeps in front and a different
speed). Switching A<->B keeps the *same point in the sentence* rather than the same raw second.
"""
import base64
import json

import numpy as np

from voicefx import dsp
from voicefx.audio import SR, to_wav_bytes


def _uri(a):
    return "data:audio/wav;base64," + base64.b64encode(to_wav_bytes(a)).decode()


def payload(src, out, info, autoplay, nonce):
    lead = (info.get("lead") or 0) / SR
    speech = (info.get("speech_len") or len(out)) / SR
    # loudness-match A to the speech part of B (RMS), never above full scale
    b_speech = out[info.get("lead") or 0: (info.get("lead") or 0) + (info.get("speech_len") or len(out))]
    gain = float(dsp.undb(dsp.rms_db(b_speech) - dsp.rms_db(src))) if len(src) else 1.0
    a = src * gain
    pk = float(np.max(np.abs(a))) if len(a) else 0
    if pk > 0.99:
        a = a * (0.99 / pk)
    return json.dumps({"a": _uri(a), "b": _uri(out), "lead": lead, "speech": speech,
                       "trim": (info.get("lead_trim") or 0) / SR, "autoplay": bool(autoplay), "nonce": nonce})


TEMPLATE = """
<div class="abp">
  <div class="row">
    <button data-act="play" class="btn primary" title="Play / pause (space)">&#9654; Play</button>
    <button data-act="stop" class="btn" title="Stop and rewind">&#9632;</button>
    <div class="seg" role="group" aria-label="A/B">
      <button data-act="A" class="btn segb" title="Unprocessed source, loudness-matched (A)">A&nbsp;source</button>
      <button data-act="B" class="btn segb on" title="Processed result (B)">B&nbsp;result</button>
    </div>
    <button data-act="toggle" class="btn" title="Switch A/B at the same point in the sentence (X)">&#8644; A/B</button>
    <label class="chk"><input type="checkbox" data-opt="loop"> loop</label>
    <span class="time">0.00 / 0.00 s</span>
  </div>
  <div class="bar" data-act="seek" title="Click to seek"><div class="fill"></div><div class="speech"></div></div>
  <div class="hint">Waiting for a source&hellip;</div>
</div>
"""

CSS = """
.abp { font: 14px system-ui, sans-serif; display: flex; flex-direction: column; gap: 8px; }
.abp .row { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; }
.abp .btn { padding: 6px 12px; border-radius: 6px; border: 1px solid var(--border-color-primary, #555);
  background: var(--button-secondary-background-fill, #2a2d35); color: var(--body-text-color, #eee); cursor: pointer; }
.abp .btn.primary { background: var(--button-primary-background-fill, #f97316); color: var(--button-primary-text-color, #fff); border-color: transparent; }
.abp .seg { display: inline-flex; }
.abp .segb { border-radius: 0; }
.abp .segb:first-child { border-radius: 6px 0 0 6px; }
.abp .segb:last-child { border-radius: 0 6px 6px 0; border-left: none; }
.abp .segb.on { background: var(--color-accent, #f97316); color: #fff; }
.abp .time { font-variant-numeric: tabular-nums; margin-left: auto; opacity: .85; }
.abp .chk { display: inline-flex; gap: 4px; align-items: center; }
.abp .bar { position: relative; height: 14px; border-radius: 7px; background: var(--block-background-fill, #1f2128);
  border: 1px solid var(--border-color-primary, #444); cursor: pointer; overflow: hidden; }
.abp .fill { position: absolute; inset: 0 auto 0 0; width: 0; background: var(--color-accent, #f97316); opacity: .55; }
.abp .speech { position: absolute; top: 0; bottom: 0; border-left: 1px dashed #fff8; border-right: 1px dashed #fff8; pointer-events: none; }
.abp .hint { font-size: 12px; opacity: .7; }
"""

JS = r"""
const st = { ctx: null, buf: { A: null, B: null }, which: 'B', node: null, t0: 0, off: 0, playing: false,
             meta: null, nonce: null, raf: 0 };
const $ = (s) => element.querySelector(s);
const ctx = () => (st.ctx ||= new (window.AudioContext || window.webkitAudioContext)());
const dur = (w) => (st.buf[w] ? st.buf[w].duration : 0);
const pos = () => (st.playing ? ctx().currentTime - st.t0 : st.off);

async function decode(uri) {
  const bin = atob(uri.split(',')[1]);
  const u8 = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) u8[i] = bin.charCodeAt(i);
  return await ctx().decodeAudioData(u8.buffer);
}
// map a position in buffer `from` to the same point of the sentence in buffer `to`
function mapPos(t, from, to) {
  const m = st.meta; if (!m || from === to) return t;
  const dA = dur('A'), sp = m.speech || dur('B');
  if (from === 'B') { const f = Math.min(Math.max((t - m.lead) / sp, 0), 1); return f * dA; }
  return m.lead + (dA ? t / dA : 0) * sp;
}
function stopNode() { if (st.node) { st.node.onended = null; try { st.node.stop(); } catch (e) {} st.node = null; } }
function start(at) {
  const b = st.buf[st.which]; if (!b) return;
  stopNode();
  if (at >= b.duration - 0.01) at = 0;
  const n = ctx().createBufferSource(); n.buffer = b; n.connect(ctx().destination);
  n.onended = () => { if (st.node !== n) return;
    if ($('[data-opt=loop]').checked) { start(0); } else { st.playing = false; st.off = 0; ui(); } };
  n.start(0, Math.max(0, at)); st.node = n; st.t0 = ctx().currentTime - at; st.playing = true; ui(); tick();
}
function pause() { st.off = pos(); stopNode(); st.playing = false; ui(); }
function setWhich(w) {
  if (w === st.which) return;
  const p = mapPos(pos(), st.which, w); st.which = w;
  if (st.playing) start(p); else { st.off = Math.min(p, dur(w)); ui(); }
}
function ui() {
  const d = dur(st.which), p = Math.min(pos(), d);
  $('.time').textContent = p.toFixed(2) + ' / ' + d.toFixed(2) + ' s';
  $('.fill').style.width = (d ? (100 * p / d) : 0) + '%';
  $('[data-act=play]').innerHTML = st.playing ? '&#10073;&#10073; Pause' : '&#9654; Play';
  element.querySelectorAll('.segb').forEach((b) => b.classList.toggle('on', b.dataset.act === st.which));
  const sp = $('.speech'), m = st.meta;
  if (m && d) {
    const s = st.which === 'B' ? m.lead : 0, e = st.which === 'B' ? m.lead + m.speech : d;
    sp.style.left = (100 * s / d) + '%'; sp.style.width = (100 * (e - s) / d) + '%';
  }
}
function tick() { cancelAnimationFrame(st.raf); const f = () => { ui(); if (st.playing) st.raf = requestAnimationFrame(f); }; f(); }

element.addEventListener('click', (ev) => {
  const t = ev.target.closest('[data-act]'); if (!t) return;
  ctx().resume();
  const a = t.dataset.act;
  if (a === 'play') st.playing ? pause() : start(st.off);
  else if (a === 'stop') { stopNode(); st.playing = false; st.off = 0; ui(); }
  else if (a === 'A' || a === 'B') setWhich(a);
  else if (a === 'toggle') setWhich(st.which === 'A' ? 'B' : 'A');
  else if (a === 'seek') { const r = t.getBoundingClientRect(); const p = (ev.clientX - r.left) / r.width * dur(st.which);
    if (st.playing) start(p); else { st.off = p; ui(); } }
});
document.addEventListener('keydown', (ev) => {
  const tag = (ev.target.tagName || '').toLowerCase();
  if (['input', 'textarea', 'select'].includes(tag) || ev.target.isContentEditable || !st.buf.B) return;
  if (ev.key === 'x' || ev.key === 'X') { ctx().resume(); setWhich(st.which === 'A' ? 'B' : 'A'); ev.preventDefault(); }
  else if (ev.key === ' ' && !tag.match(/button/)) { ctx().resume(); st.playing ? pause() : start(st.off); ev.preventDefault(); }
});

async function load() {
  let m; try { m = JSON.parse(props.value || '{}'); } catch (e) { return; }
  if (!m.b || m.nonce === st.nonce) return;
  st.nonce = m.nonce;
  const wasPlaying = st.playing, oldWhich = st.which, oldPos = pos(), oldMeta = st.meta;
  const [A, B] = await Promise.all([decode(m.a), decode(m.b)]);
  // keep the same point in the sentence across re-renders (speed/bleep changes move it)
  let frac = null;
  if (oldMeta && st.buf.B) { st.meta = oldMeta; frac = mapPos(oldPos, oldWhich, 'A') / (dur('A') || 1); }
  st.buf = { A, B }; st.meta = m;
  $('.hint').textContent = 'A = source (loudness-matched) · B = result · X toggles at the same point · space plays';
  if (wasPlaying) {
    const p = frac === null ? 0 : (st.which === 'A' ? frac * dur('A') : mapPos(frac * dur('A'), 'A', 'B'));
    start(p);
  } else if (m.autoplay) { st.which = 'B'; start(0); }
  else { st.off = 0; ui(); }
}
watch('value', load);
load();
"""
