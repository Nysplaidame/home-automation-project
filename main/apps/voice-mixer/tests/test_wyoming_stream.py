"""Sentence-by-sentence synthesis in the Metrocop Wyoming server (no Piper needed: the engine is faked)."""
import asyncio
import json

from conftest import ROOT  # noqa: F401  (puts the app on sys.path)
from voice_mixer import wyoming_tts as W


class FakeEngine:
    """head = b'H', body = the sentence in upper case, ending = b'E'; records what was synthesised."""

    def __init__(self):
        self.spoken, self.seeds = [], set()

    def synthesize_parts(self, text, seed=None):
        self.spoken.append(text)
        self.seeds.add(seed)
        return b"HH", text.upper().encode(), b"EE"

    def synthesize(self, text, seed=None):
        return b"".join(self.synthesize_parts(text, seed))


class FakeWriter:
    def __init__(self):
        self.data = b""

    def write(self, chunk):
        self.data += chunk

    async def drain(self):
        pass

    def close(self):
        pass

    def get_extra_info(self, _name):
        return "test"


def events(blob):
    out, i = [], 0
    while i < len(blob):
        nl = blob.index(b"\n", i)
        hdr = json.loads(blob[i:nl])
        i = nl + 1 + hdr.get("data_length", 0)
        payload = blob[i:i + hdr.get("payload_length", 0)]
        i += hdr.get("payload_length", 0)
        out.append((hdr["type"], payload))
    return out


def run(messages):
    async def go():
        reader = asyncio.StreamReader()
        for etype, data in messages:
            reader.feed_data(W.encode_event(etype, data))
        reader.feed_eof()
        engine, writer = FakeEngine(), FakeWriter()
        await W.handle(engine, reader, writer)
        return engine, events(writer.data)
    return asyncio.run(go())


def audio(evts):
    return b"".join(payload for etype, payload in evts if etype == "audio-chunk")


def test_split_keeps_unfinished_text_and_decimals():
    done, rest = W.split_sentences("The garage is 3.5 degrees right now. The fan is")
    assert done == ["The garage is 3.5 degrees right now."]
    assert rest == "The fan is"
    assert W.split_sentences("The garage is 3.5 degrees right now.") == ([], "The garage is 3.5 degrees right now.")


def test_split_joins_short_fragments_to_what_follows():
    done, rest = W.split_sentences("1. Creamy Tarragon Chicken. 2. Lentil soup with bacon. ")
    assert done == ["1. Creamy Tarragon Chicken.", "2. Lentil soup with bacon."]
    assert rest == ""
    assert W.split_sentences("Yes. It is. ") == ([], "Yes. It is. ")


def test_split_points_clamp():
    assert W.split_points(100, 10, 50) == (10, 50)
    assert W.split_points(100, None, None) == (0, 100)
    assert W.split_points(100, 90, 50) == (90, 10)


def test_info_advertises_streaming():
    assert W.info_event()["tts"][0]["supports_synthesize_streaming"] is True


def test_streamed_reply_bleeps_once_and_ignores_the_compat_copy():
    text = "First story is about the weather today. Second story is about football."
    engine, evts = run([
        ("synthesize-start", {"voice": {"name": "metrocop"}}),
        ("synthesize-chunk", {"text": "First story is about the wea"}),
        ("synthesize-chunk", {"text": "ther today. Second story is "}),
        ("synthesize-chunk", {"text": "about football."}),
        ("synthesize", {"text": text}),
        ("synthesize-stop", None),
    ])
    assert engine.spoken == ["First story is about the weather today.", "Second story is about football."]
    assert len(engine.seeds) == 1 and None not in engine.seeds
    assert audio(evts) == (b"HH" + b"FIRST STORY IS ABOUT THE WEATHER TODAY." +
                           b"SECOND STORY IS ABOUT FOOTBALL." + b"EE")
    types = [etype for etype, _ in evts]
    assert types.count("audio-start") == 1 and types[0] == "audio-start"
    assert types[-2:] == ["audio-stop", "synthesize-stopped"]


def test_whole_text_in_one_chunk_is_still_split():
    engine, evts = run([
        ("synthesize-start", None),
        ("synthesize-chunk", {"text": "Heat the oil in a large pan. Add the onions and cook until soft."}),
        ("synthesize-stop", None),
    ])
    assert len(engine.spoken) == 2
    assert audio(evts).startswith(b"HH") and audio(evts).endswith(b"EE")


def test_empty_stream_still_terminates():
    engine, evts = run([("synthesize-start", None), ("synthesize-chunk", {"text": "  "}), ("synthesize-stop", None)])
    assert engine.spoken == []
    assert [etype for etype, _ in evts] == ["audio-start", "audio-stop", "synthesize-stopped"]


def test_plain_synthesize_is_unchanged():
    engine, evts = run([("synthesize", {"text": "Ready."})])
    assert audio(evts) == b"HHREADY.EE"
    assert [etype for etype, _ in evts][-1] == "audio-stop"
