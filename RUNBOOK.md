# Round A runbook

## What has run in this environment
- Parser + heuristic baseline executed against all 50 supplied episodes.
- 3,727 timed beats parsed; 368 heuristic candidates; top 15 ranked.
- Zero parser warnings in this corpus.
- Three parser unit tests pass.
- No paid or free LLM API was called here. LLM candidate selection and cold-viewer judging are implemented in `src/llm_pipeline.py` and are intended to run in Colab after entering a current provider model ID and key.

## Local heuristic rerun
`python src/run.py --input /path/to/screenplay-folder-or.zip --provider heuristic`

## LLM rerun
`python src/run.py --input /path/to/screenplay-folder-or.zip --provider gemini --model <current-model-id> --run-label run1`
Supported adapters: `gemini`, `groq`, `anthropic`, `openai`. Set the matching API key environment variable first. Run twice with labels `run1` and `run2` to measure stability. Colab notebook automates this and zips outputs.

## Keep confidential material private
The screenplay ZIP and all raw outputs containing screenplay-derived text are excluded from the public repository ZIP. Share the raw outputs only through the assignment's intended private submission channel; do not publish them in a public GitHub repository.
