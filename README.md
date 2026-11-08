# Kuku Promo Finder (Problem 1)

A reproducible screenplay-to-promo candidate pipeline. The current runnable baseline parses timed beats and proposes/ranks heuristic clips. LLM-assisted judging is scaffolded as a Colab workflow; do not treat heuristic rankings as editor-approved promos.

## Run locally
1. `python -m venv .venv && source .venv/bin/activate` (Windows: `.venv\Scripts\activate`)
2. `pip install -r requirements.txt`
3. `python src/run.py --input /path/to/screenplay_folder_or_zip --provider heuristic`

Outputs go to `raw_outputs/heuristic/`. Input screenplays are intentionally excluded from version control.

## Tests
`python -m unittest discover -s tests -v`

## Colab
Open `colab_run.ipynb`, upload the repo ZIP and the screenplay ZIP, set a provider secret, and run all cells. The notebook includes model-based candidate extraction/judging and saves raw outputs. API model names/free limits can change; verify in the provider console before running.

## Important limitations
The script contains screenplay directions, not rendered video. A text-only system cannot reliably detect visual-only hooks, performance, pacing, music, or actual final-video timing. All timestamps are screenplay timestamps and require editor confirmation against picture lock. The heuristic baseline is a candidate generator, not a quality benchmark.

## LLM pipeline details
The Colab notebook and `src/llm_pipeline.py` run a candidate-selection pass per episode, then a separate judge pass with a cold-viewer test. Models return beat IDs only; Python maps those IDs to exact source timestamps and enforces 20–60s duration. Per-run prompt-response caching avoids duplicate API calls after interrupted runs. The second stability run uses a separate cache directory.
