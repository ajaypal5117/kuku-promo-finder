# Runbook

## What has been run
- **Heuristic baseline** on all 50 episodes: 3,727 timed beats, 367 candidates, top 15 ranked, zero parser warnings.
- **LLM run1** (`gemini-3.5-flash-lite`, local via `src/run.py`): 123 model calls, 530 s, 73 candidates judged, 1 passed all checks, 1 schema failure (Episode 20).
- **LLM run2** (same model and input): 117 model calls, 734 s, 67 candidates judged, 3 passed, 0 failures.
- Three parser unit tests pass.

## Run on a new show in under 5 minutes
1. `pip install -r requirements.txt`
2. Quick check, no key needed:
   `python src/run.py --input <folder_or_zip> --provider heuristic`
3. Full run:
   `set GEMINI_API_KEY=<key>` (macOS/Linux: `export`)
   `python src/run.py --input <folder_or_zip> --provider gemini --model gemini-3.5-flash-lite --run-label run1`
4. Open `raw_outputs/llm/run1/ranked_top15.json` for the ranked list and `run_summary.json` for counts, runtime and failures.

## If something fails
- **404 "no longer available"** → use the model the error message names.
- **429 quota / 503 high demand** → try another model, wait for quota reset, or switch provider (`--provider groq` with `GROQ_API_KEY`).
- **No key or no internet** → fall back to `--provider heuristic`, which always runs.
- **Interrupted run** → re-run the same command with the same `--run-label`. Finished calls are cached and skipped.

## Keep confidential material private
Screenplays and raw outputs stay out of the public repo. Share raw outputs only through the private submission link.
