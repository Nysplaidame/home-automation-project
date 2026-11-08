# Browser OCR assets

Selected release assets served by Recomp itself. No CDN or external recognition
endpoint is used at runtime. Photos, crop canvases and recognised text remain in
browser memory; only explicitly applied food values enter the normal save flow.

- `tesseract.min.js`, `worker.min.js`: npm `tesseract.js@6.0.1`, Apache-2.0.
- `tesseract-core*.wasm*`: npm `tesseract.js-core@6.1.2`, Apache-2.0.
- `eng-fast-v1/eng.traineddata.gz`: English fast integer LSTM model from
  `https://raw.githubusercontent.com/naptha/tessdata/gh-pages/4.0.0_fast/eng.traineddata.gz`.
  Tesseract language data uses Apache-2.0. Downloaded 2026-10-10.
- License texts and `SHA256SUMS` accompany the retained assets. Hashes pin this
  exact downloaded model generation; the upstream branch URL is mutable.

SIMD/non-SIMD and LSTM/full core variants are retained per Tesseract.js local
installation guidance. Approximately 32 MB of deployment assets; the browser
loads only its selected core and English data. The fast language download is
1,984,273 bytes (previous combined model: 10,923,060 bytes). Recognition starts
preparing when the scan panel opens and reuses its worker for subsequent scans.
Workers are released after 60 seconds idle, on cancellation/errors, when the
form is removed or when the page is backgrounded.

Language data uses a new IndexedDB cache key to avoid reusing the old large
model. The root-scoped service worker caches OCR assets separately, cache-first,
across shell upgrades. First use requires a connection to Recomp. The speed
model passed synthetic label checks; accuracy on real packaging remains to be
evaluated. This version reads English only and adds no inference service.

Reproduce JavaScript assets outside the vault with
`npm install --prefix <temporary-directory> tesseract.js@6.0.1 tesseract.js-core@6.1.2 --ignore-scripts`,
then copy the selected distributions, core files and licenses into this directory.
Check SHA256SUMS before replacing any retained asset.
