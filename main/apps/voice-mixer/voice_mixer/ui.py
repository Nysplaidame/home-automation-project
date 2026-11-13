"""Gradio UI for the Voice Mixer."""
import os

os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")   # no runtime network calls
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")

import re
import shlex
import threading
import time
from collections import OrderedDict
from pathlib import Path

import gradio as gr

from voicefx import params as P
from voicefx.audio import save
from voicefx.pipeline import Pipeline, audio_key

from . import abplayer, analysis, sources

MODES = ["Dataset clip", "File", "Piper", "Piper + RVC", "Game clip"]
CURRENT = "(current mixer settings)"
_SAFE = re.compile(r"[^A-Za-z0-9 _.-]")


class SourceStore:
    """Prepared source clips by key (shared by all sessions; small LRU)."""

    def __init__(self, size=32):
        self.d, self.size, self.lock = OrderedDict(), size, threading.Lock()

    def put(self, audio, label, text=""):
        a = Pipeline.prepare_source(audio)
        k = audio_key(a)
        with self.lock:
            self.d[k] = (a, label, text)
            self.d.move_to_end(k)
            while len(self.d) > self.size:
                self.d.popitem(last=False)
        return k

    def get(self, k):
        with self.lock:
            return self.d.get(k)


def _safe_name(s):
    s = _SAFE.sub("", (s or "").strip()).strip(". ")
    return s[:60]


def _within(path, roots):
    try:
        rp = Path(path).resolve()
    except OSError:
        return False
    return any(r and (rp == r.resolve() or r.resolve() in rp.parents) for r in roots)


def build(cfg):
    avail = sources.check(cfg)
    pipe = Pipeline(str(cfg.p("bleep_dir")) if cfg.p("bleep_dir") and cfg.p("bleep_dir").exists() else None)
    store = SourceStore()
    presets_dir = cfg.p("presets_dir")
    for name, flat in P.BUILTIN.items():            # seed shipped presets if missing (never overwrite)
        f = presets_dir / f"{name}.json"
        if not f.exists():
            P.save_preset(f, name, flat, P.DESCRIPTIONS.get(name, ""))
    shipped = Path(__file__).resolve().parent.parent / "presets"
    if shipped.resolve() != presets_dir.resolve():  # also seed extra shipped presets (e.g. metrocop)
        for src in shipped.glob("*.json"):
            if not (presets_dir / src.name).exists():
                (presets_dir / src.name).write_bytes(src.read_bytes())
    ds_items, game_items = sources.dataset_items(cfg), sources.game_items(cfg)

    def preset_names():
        return sorted(p.stem for p in presets_dir.glob("*.json"))

    default_preset = cfg.get("default_preset") or "metrocop"
    if not (presets_dir / f"{default_preset}.json").exists():
        default_preset = "mid"
    start_flat, _, _ = P.load_preset(presets_dir / f"{default_preset}.json")

    # ------------------------------------------------------------------ core callbacks
    def vals_to_flat(vals):
        return P.complete({k: v for k, v in zip(P.KEYS, vals)})

    def do_render(src_key, autoplay, vals):
        item = store.get(src_key) if src_key else None
        if not item:
            return gr.skip(), "Load a source first.", gr.skip(), gr.skip()
        src, label, _ = item
        flat = vals_to_flat(vals)
        r = pipe.render(src, flat, source_key=src_key)
        total = max(len(src), len(r.audio)) / 22050
        return (abplayer.payload(src, r.audio, r.info, autoplay, time.time_ns()),
                analysis.metrics_md(src, r.audio, r.info),
                analysis.panel(src, total, colour=(170, 170, 180)),
                analysis.panel(r.audio, total))

    def auto_render(src_key, auto, autoplay, *vals):
        if not auto:
            return gr.skip(), gr.skip(), gr.skip(), gr.skip()
        return do_render(src_key, autoplay, vals)

    def manual_render(src_key, autoplay, *vals):
        return do_render(src_key, autoplay, vals)

    def load_source(mode, file, text, ls, rpitch, rprotect, rindex, ruse_index, ds, game, progress=gr.Progress()):
        try:
            if mode == "File":
                if not file:
                    raise ValueError("choose an audio file")
                path = file if isinstance(file, str) else file.name
                k = store.put(sources.load_any(path), os.path.basename(path))
                desc = f"**File:** `{os.path.basename(path)}`"
            elif mode == "Piper":
                if not avail.piper:
                    raise RuntimeError(avail.piper_msg)
                progress(0.2, desc="Piper synthesising…")
                path = sources.piper_tts(cfg, text, ls)
                k = store.put(sources.load_any(path), "piper", text)
                desc = f"**Piper** (length scale {ls}): “{' '.join(text.split())}”"
            elif mode == "Piper + RVC":
                if not avail.rvc:
                    raise RuntimeError(avail.rvc_msg)
                progress(0.1, desc="Piper → RVC (first run loads the model; can take a while)…")
                t = time.time()
                path = sources.rvc_convert(cfg, text, ls, rpitch, rprotect, rindex, ruse_index)
                k = store.put(sources.load_any(path), "rvc", text)
                desc = (f"**Piper → RVC** (pitch {int(rpitch)}, protect {rprotect}, index rate {rindex}"
                        f"{'' if ruse_index else ', no index'}; {time.time() - t:.1f} s): “{' '.join(text.split())}”")
            elif mode == "Dataset clip":
                if not ds:
                    raise ValueError("pick a dataset clip")
                label = next((l for l, p in ds_items if p == ds), os.path.basename(ds))
                k = store.put(sources.load_any(ds), os.path.basename(ds), label)
                desc = f"**Dataset:** `{label}`"
            else:
                if not game:
                    raise ValueError("pick a game clip")
                k = store.put(sources.load_any(game), os.path.basename(game))
                desc = f"**Game clip:** `{os.path.relpath(game, cfg.p('game_clips_dir'))}`"
            a = store.get(k)[0]
            return k, desc + f" · {len(a) / 22050:.2f} s"
        except Exception as e:  # shown in the UI; app keeps running
            raise gr.Error(str(e)[:800])

    def mode_vis(mode):
        return (gr.update(visible=mode == "File"), gr.update(visible=mode in ("Piper", "Piper + RVC")),
                gr.update(visible=mode == "Piper + RVC"), gr.update(visible=mode == "Dataset clip"),
                gr.update(visible=mode == "Game clip"))

    # ------------------------------------------------------------------ presets
    def preset_load(name):
        f = presets_dir / f"{_safe_name(name)}.json"
        if not f.exists():
            raise gr.Error(f"preset {name!r} not found")
        flat, doc, warnings = P.load_preset(f)
        msg = f"Loaded **{name}**" + (f" — {doc.get('description')}" if doc.get("description") else "")
        if warnings:
            msg += "<br><small>" + "; ".join(warnings) + "</small>"
        return [flat[k] for k in P.KEYS] + [msg, name]

    def preset_save(name, desc, *vals):
        n = _safe_name(name)
        if not n:
            raise gr.Error("give the preset a name (letters, digits, space, _ . -)")
        P.save_preset(presets_dir / f"{n}.json", n, vals_to_flat(vals), desc or "")
        return gr.update(choices=preset_names(), value=n), f"Saved **{n}** → `{presets_dir / (n + '.json')}`"

    def preset_delete(name):
        n = _safe_name(name)
        if n in P.BUILTIN:
            raise gr.Error("built-in presets can be overwritten but not deleted")
        f = presets_dir / f"{n}.json"
        if f.exists():
            f.unlink()
        names = preset_names()
        return gr.update(choices=names, value=default_preset if default_preset in names else "mid" if "mid" in names else (names[0] if names else None)), f"Deleted **{n}**"

    def cli_text(name, *vals):
        flat = vals_to_flat(vals)
        bleeps = str(cfg.p("bleep_dir") or "<bleep dir>")
        seed = flat["bleeps.seed"]
        q = lambda s: f'"{s}"' if os.name == "nt" or " " in str(s) else shlex.quote(str(s))
        sets = " ".join(f"--set {k}={str(v).lower() if isinstance(v, bool) else v}"
                        for k, v in P.diff_from_defaults(flat).items() if k != "bleeps.seed")
        lines = ["# Full fidelity (voicefx CLI in apps/voice-mixer; any setting):",
                 f"python -m voicefx in.wav out.wav --bleeps {q(bleeps)} --seed {seed} {sets}".rstrip()]
        saved = presets_dir / f"{_safe_name(name)}.json"
        if name and saved.exists():
            same, _, _ = P.load_preset(saved)
            if same == flat:
                lines += ["", "# Same thing via the saved preset file:",
                          f"python -m voicefx in.wav out.wav --bleeps {q(bleeps)} --seed {seed} --preset-file {q(saved)}"]
        leg, unsupported = P.to_legacy(flat)
        flags = (f"--semitones {leg['semitones']} --speed {leg['speed']} --lowcut {leg['lowcut']:g} "
                 f"--lowboost {leg['lowboost']} --drive {leg['drive']} --hf-db {leg['hf_db']} --presence {leg['presence']}")
        lines += ["", "# Original radio_fx.py flags (legacy subset):",
                  f"python radio_fx.py in.wav out.wav --bleeps {q(bleeps)} --seed {seed} {flags}"
                  + ("" if flat["radio.on"] else " --no-filter")]
        if unsupported:
            lines.append(f"# NOTE: radio_fx.py flags cannot express: {', '.join(unsupported)} -> use the voicefx line")
        return "\n".join(lines)

    def export(src_key, sr44, *vals):
        item = store.get(src_key) if src_key else None
        if not item:
            raise gr.Error("load a source first")
        src, label, _ = item
        r = pipe.render(src, vals_to_flat(vals), source_key=src_key)
        out = cfg.p("output_dir") / f"{time.strftime('%Y%m%d-%H%M%S')}_{_safe_name(Path(label).stem) or 'clip'}{'_44k' if sr44 else ''}.wav"
        save(str(out), r.audio, out_sr=44100 if sr44 else None)
        return str(out)

    # ------------------------------------------------------------------ batch
    def batch_run(mode, folder, sentences, outname, preset, vary, sr44, *vals, progress=gr.Progress()):
        if preset and preset != CURRENT:
            flat, _, _ = P.load_preset(presets_dir / f"{_safe_name(preset)}.json")
        else:
            flat = vals_to_flat(vals)
        sub = _safe_name(outname) or time.strftime("batch-%Y%m%d-%H%M%S")
        outdir = cfg.p("output_dir") / sub
        outdir.mkdir(parents=True, exist_ok=True)
        jobs = []
        if mode == "Folder of audio files":
            roots = [cfg.p(k) for k in ("dataset_dir", "game_clips_dir", "output_dir", "cache_dir")]
            roots += [Path(x) for x in cfg.get("batch_roots", [])]
            if not folder or not Path(folder).is_dir():
                raise gr.Error("folder not found")
            if not _within(folder, roots):
                raise gr.Error("folder must be inside the dataset, game clips, outputs, cache or a config 'batch_roots' entry")
            for f in sorted(Path(folder).iterdir()):
                if f.suffix.lower() in sources.AUDIO_EXT:
                    jobs.append((f.stem, lambda f=f: sources.load_any(f)))
        else:
            need = avail.rvc if mode.endswith("RVC") else avail.piper
            if not need:
                raise gr.Error(avail.rvc_msg if mode.endswith("RVC") else avail.piper_msg)
            lines = [l.strip() for l in (sentences or "").splitlines() if l.strip()]
            for i, line in enumerate(lines):
                if mode.endswith("RVC"):
                    fn = lambda line=line: sources.load_any(sources.rvc_convert(cfg, line))
                else:
                    fn = lambda line=line: sources.load_any(sources.piper_tts(cfg, line))
                jobs.append((f"{i:04d}_{_safe_name(line)[:40].strip().replace(' ', '_')}", fn))
        if not jobs:
            raise gr.Error("nothing to render")
        written, log = [], []
        for i, (stem, get) in enumerate(jobs):
            progress((i, len(jobs)), desc=stem)
            try:
                p = dict(flat)
                if vary:
                    p["bleeps.seed"] = flat["bleeps.seed"] + i
                r = pipe.render(Pipeline.prepare_source(get()), p)
                dst = outdir / f"{stem}.wav"
                save(str(dst), r.audio, out_sr=44100 if sr44 else None)
                written.append(str(dst))
            except Exception as e:
                log.append(f"- {stem}: FAILED {e}")
        summary = f"Wrote **{len(written)}/{len(jobs)}** files to `{outdir}`"
        return summary + ("\n" + "\n".join(log) if log else ""), written[:50]

    # ------------------------------------------------------------------ layout
    theme = gr.themes.Soft(primary_hue="orange", neutral_hue="slate",
                           font=["system-ui", "Segoe UI", "sans-serif"], font_mono=["ui-monospace", "Consolas", "monospace"])
    css = """
    .controls .gr-accordion { margin-bottom: 4px; }
    #status-line { font-size: 13px; opacity: .85; }
    footer { display: none !important; }
    """
    controls = {}
    with gr.Blocks(title="Voice Mixer", analytics_enabled=False) as demo:
        src_key = gr.State(None)
        gr.Markdown("## Voice Mixer · Metrocop radio voice")
        gr.Markdown(f"{'✅' if avail.piper else '⚠️'} {avail.piper_msg} &nbsp;·&nbsp; {'✅' if avail.rvc else '⚠️'} {avail.rvc_msg}",
                    elem_id="status-line")
        with gr.Tabs():
            with gr.Tab("Mixer"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=5, min_width=360):
                        with gr.Group():
                            mode = gr.Radio(MODES, value="Dataset clip" if ds_items else "File", label="Source", interactive=True)
                            with gr.Group(visible=not ds_items) as g_file:
                                f_in = gr.File(label="Audio file (wav / flac / mp3 / ogg)", file_types=["audio"], type="filepath")
                            with gr.Group(visible=False) as g_text:
                                text = gr.Textbox(label="Text", lines=2, placeholder="Hold it right there. This is your final warning.")
                                ls = gr.Slider(0.5, 2.0, value=float(cfg.get("piper_length_scale", 1.0)), step=0.05, label="Piper length scale",
                                               info="Phoneme length (>1 slower).", buttons=["reset"])
                            with gr.Group(visible=False) as g_rvc:
                                with gr.Row():
                                    rpitch = gr.Slider(-12, 12, value=0, step=1, label="RVC pitch (-pi)", buttons=["reset"])
                                    rprotect = gr.Slider(0, 0.5, value=0.33, step=0.01, label="RVC protect (-pr)",
                                                         info="Protect consonants/breaths.", buttons=["reset"])
                                with gr.Row():
                                    rindex = gr.Slider(0, 1, value=0.75, step=0.05, label="RVC index rate (-ir)", buttons=["reset"])
                                    ruse = gr.Checkbox(value=True, label="Use .index file")
                            with gr.Group(visible=bool(ds_items)) as g_ds:
                                ds = gr.Dropdown(choices=ds_items, value=ds_items[0][1] if ds_items else None, label=f"Dataset clip ({len(ds_items)})",
                                                 filterable=True)
                            with gr.Group(visible=False) as g_game:
                                game = gr.Dropdown(choices=game_items, value=None, label=f"Game clip ({len(game_items)})", filterable=True)
                            load_btn = gr.Button("Load source", variant="secondary")
                        src_info = gr.Markdown("No source loaded.")
                        player = gr.HTML(value="", html_template=abplayer.TEMPLATE, css_template=abplayer.CSS,
                                         js_on_load=abplayer.JS, padding=True)
                        with gr.Row():
                            auto = gr.Checkbox(value=True, label="Auto-render on change")
                            autoplay = gr.Checkbox(value=True, label="Play after render")
                            render_btn = gr.Button("Render", variant="primary", size="sm")
                        metrics = gr.Markdown()
                        img_src = gr.Image(label="Source: waveform + spectrogram (dotted line = 1.5 kHz)", type="numpy",
                                           interactive=False, height=180)
                        img_out = gr.Image(label="Result", type="numpy", interactive=False, height=180)
                        with gr.Accordion("Presets, CLI and export", open=True):
                            with gr.Row():
                                preset = gr.Dropdown(choices=preset_names(), value=default_preset, label="Preset", scale=3)
                                p_load = gr.Button("Load", size="sm", scale=1)
                                p_del = gr.Button("Delete", size="sm", scale=1, variant="stop")
                            with gr.Row():
                                p_name = gr.Textbox(label="Save as", placeholder="my-preset", scale=2)
                                p_desc = gr.Textbox(label="Description", scale=3)
                                p_save = gr.Button("Save", size="sm", scale=1)
                            p_msg = gr.Markdown()
                            cli_btn = gr.Button("Copy as CLI flags", size="sm")
                            cli = gr.Code(language="shell", label="CLI (use the copy button)", interactive=False, lines=8)
                            with gr.Row():
                                sr44 = gr.Checkbox(value=False, label="Export at 44.1 kHz")
                                exp_btn = gr.Button("Export WAV", size="sm", variant="primary")
                            exp_file = gr.File(label="Exported", interactive=False)
                    with gr.Column(scale=4, min_width=340, elem_classes="controls"):
                        group_resets = {}
                        for stage, title in P.GROUPS.items():
                            with gr.Accordion(title, open=stage in ("pitch", "eq", "radio")):
                                for p in [x for x in P.PARAMS if x.key.startswith(stage + ".")]:
                                    v = start_flat[p.key]
                                    if p.kind == "bool":
                                        c = gr.Checkbox(value=v, label=p.label, info=p.info or None)
                                    elif p.kind == "choice":
                                        c = gr.Dropdown(choices=list(p.choices), value=v, label=p.label, info=p.info or None)
                                    else:
                                        c = gr.Slider(p.lo, p.hi, value=v, step=p.step, label=p.label, info=p.info or None,
                                                      buttons=["reset"])
                                    controls[p.key] = c
                                group_resets[stage] = gr.Button(f"Reset {title} to defaults", size="sm")

            with gr.Tab("Batch"):
                gr.Markdown("Render many clips through the current settings or a saved preset. "
                            f"Output goes to a sub-folder of `{cfg.p('output_dir')}`.")
                b_mode = gr.Radio(["Folder of audio files", "Sentences → Piper", "Sentences → Piper + RVC"],
                                  value="Folder of audio files", label="Input")
                b_folder = gr.Textbox(label="Folder", value=str(cfg.p("dataset_dir") / "wav") if cfg.p("dataset_dir") else "",
                                      info="Must be inside the dataset, game clips, outputs, cache or a 'batch_roots' entry in config.json.")
                b_text = gr.Textbox(label="Sentences (one per line)", lines=6)
                with gr.Row():
                    b_out = gr.Textbox(label="Output sub-folder", placeholder="batch-YYYYmmdd-HHMMSS")
                    b_preset = gr.Dropdown(choices=[CURRENT] + preset_names(), value=CURRENT, label="Settings")
                with gr.Row():
                    b_vary = gr.Checkbox(value=True, label="Vary bleeps per file (seed + index)")
                    b_sr44 = gr.Checkbox(value=False, label="44.1 kHz")
                b_run = gr.Button("Run batch", variant="primary")
                b_log = gr.Markdown()
                b_files = gr.File(label="Output (first 50)", file_count="multiple", interactive=False)

            with gr.Tab("Settings"):
                gr.Markdown(f"Config file: `{cfg.path}`{' (created with defaults this run)' if cfg.created else ''}. "
                            "Edit it and restart to change paths, python, RVC device or the port.")
                gr.JSON(value={k: v for k, v in cfg.items()}, label="Active config")
                gr.Markdown(f"- Piper: {avail.piper_msg}\n- RVC: {avail.rvc_msg}\n"
                            f"- Bleeps: `{cfg.p('bleep_dir')}` {'✅' if pipe.bleep_dir else '⚠️ missing: bleeps disabled'}\n"
                            f"- Dataset clips: {len(ds_items)} · game clips: {len(game_items)}\n"
                            f"- Presets folder: `{presets_dir}`")

        # ------------------------------------------------------------------ events
        ctrl_list = [controls[k] for k in P.KEYS]
        outs = [player, metrics, img_src, img_out]
        ev = dict(fn=auto_render, inputs=[src_key, auto, autoplay] + ctrl_list, outputs=outs,
                  trigger_mode="always_last", show_progress="hidden")
        for k, c in controls.items():
            (c.release if isinstance(c, gr.Slider) else c.input)(**ev)
        render_btn.click(manual_render, [src_key, autoplay] + ctrl_list, outs, show_progress="minimal")

        mode.change(mode_vis, mode, [g_file, g_text, g_rvc, g_ds, g_game], show_progress="hidden")
        src_inputs = [mode, f_in, text, ls, rpitch, rprotect, rindex, ruse, ds, game]
        load_btn.click(load_source, src_inputs, [src_key, src_info]).success(
            manual_render, [src_key, autoplay] + ctrl_list, outs)
        for c in (ds, game):
            c.input(load_source, src_inputs, [src_key, src_info]).success(manual_render, [src_key, autoplay] + ctrl_list, outs)
        f_in.upload(load_source, src_inputs, [src_key, src_info]).success(manual_render, [src_key, autoplay] + ctrl_list, outs)

        p_load.click(preset_load, preset, ctrl_list + [p_msg, p_name]).then(manual_render, [src_key, autoplay] + ctrl_list, outs)
        p_save.click(preset_save, [p_name, p_desc] + ctrl_list, [preset, p_msg]).then(
            lambda: gr.update(choices=[CURRENT] + preset_names()), None, b_preset)
        p_del.click(preset_delete, preset, [preset, p_msg]).then(
            lambda: gr.update(choices=[CURRENT] + preset_names()), None, b_preset)
        cli_btn.click(cli_text, [preset] + ctrl_list, cli)
        exp_btn.click(export, [src_key, sr44] + ctrl_list, exp_file)

        for stage, btn in group_resets.items():
            keys = [k for k in P.KEYS if k.startswith(stage + ".")]
            btn.click(lambda keys=keys: [P.BY_KEY[k].default for k in keys], None, [controls[k] for k in keys]).then(
                auto_render, [src_key, auto, autoplay] + ctrl_list, outs)

        b_run.click(batch_run, [b_mode, b_folder, b_text, b_out, b_preset, b_vary, b_sr44] + ctrl_list, [b_log, b_files])

        if ds_items:
            demo.load(load_source, src_inputs, [src_key, src_info]).success(
                lambda k, *v: do_render(k, False, v), [src_key] + ctrl_list, outs)

    launch = dict(server_name=cfg["host"], server_port=int(cfg["port"]), theme=theme, css=css,
                  allowed_paths=[str(cfg.p("output_dir")), str(cfg.p("cache_dir"))], footer_links=[])
    return demo, launch
