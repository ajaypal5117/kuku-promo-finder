# Kuku Promo Finder (Problem 1)

**Live app:** https://kuku-promo-finder-ajaypal.streamlit.app/ (heuristic baseline, upload a screenplay ZIP and get ranked promos instantly)

Reads microdrama screenplays and finds 20–60s promo clips: a hook in the first 3 seconds, an unresolved cliffhanger at the end, and enough context for a cold viewer. Outputs the episode, start/end timestamps, hook, cliffhanger and a one-line reason for each candidate, ranked.

**Status:** both modes have been run end to end on all 50 supplied episodes.
- Heuristic mode (no API): 3,727 beats parsed, 367 candidates, top 15 ranked.
- LLM mode (`gemini-3.5-flash-lite`, run twice for stability): 73 and 67 candidates, judged and ranked. Results, gold-set comparison and failures are in the solution doc and `raw_outputs/llm/evaluation.md` (shared privately, not in this repo).

## How it works
1. **Parser (code):** splits each screenplay into numbered, timestamped beats (`E001-B081` etc.).
2. **Candidate pass (LLM, per episode):** proposes hook→cliffhanger spans by citing beat IDs only. The model never writes a timestamp.
3. **Validation (code):** maps beat IDs back to real timestamps, enforces 20–60s, rejects any cut inside a line of dialogue, checks JSON against a schema.
4. **Judge pass (LLM, separate prompt):** scores hook, cliffhanger, standalone clarity and emotional appeal, with a cold-viewer test that sees only the clip text.
5. **Ranking (code):** weighted score, with a small preference for early episodes so promos send viewers to Episode 1.
6. **Editor (human):** reviews the ranked list before anything is posted.

## Run it (local, recommended)
```
pip install -r requirements.txt
```
No API key needed:
```
python src/run.py --input <screenplay_folder_or_zip> --provider heuristic
```
With an LLM (Windows uses `set`, macOS/Linux uses `export`):
```
set GEMINI_API_KEY=your_key
python src/run.py --input <screenplay_folder_or_zip> --provider gemini --model gemini-3.5-flash-lite --run-label run1
```
Run again with `--run-label run2` to measure stability. Outputs go to `raw_outputs/heuristic/` or `raw_outputs/llm/<run-label>/`.

## Swapping the model
The model is a command-line value, not hardcoded. Supported providers: `gemini`, `groq`, `openai`, `anthropic`, plus `heuristic` as a no-key fallback. Set the matching key (`GEMINI_API_KEY`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) and pass `--provider` and `--model`.

Free-tier model availability changes often. During this build, `gemini-3.8-flash` had no usable free quota and `gemini-2.5-flash-lite` returned "no longer available to new users"; `gemini-3.5-flash-lite` worked. If a model fails, read the API's error message, which usually names the replacement. Details in `AI_LOG.md`.

## Colab (alternative)
`colab_run.ipynb` runs the same pipeline and saves progress to Google Drive so a disconnect doesn't lose work. Colab's free runtime disconnected several times during long runs, so the local command above is more reliable.

## Tests
```
python -m unittest discover -s tests -v
```

## Limitations
- Text only: visual hooks (a slap described only in an ACTION line), performance, pacing and music are not seen.
- Screenplay timestamps are proxies; an editor must confirm them against the final cut.
- Candidates are generated one episode at a time, so many strong moments fail the cold-viewer test because they depend on earlier episodes. A rolling series synopsis is the planned fix.
- Run-to-run results vary; treat the ranking as a shortlist for an editor, not a final decision.

## Confidentiality
The screenplays and raw outputs are Kuku's content and are excluded from this repo (`.gitignore`).
