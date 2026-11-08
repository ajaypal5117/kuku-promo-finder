# AI / pipeline log

- The assignment brief and screenplay pack were inspected directly. No LLM API call was executed in this environment, so there are no claimed model hallucinations or token/runtime measurements.
- Initial corpus inspection showed overlapping CAMERA/ACTION/dialogue blocks and variable scene counts; the parser therefore retains timed blocks as beats and does not flatten them into mutually exclusive intervals.
- The source pack contains 50 episode text files; these are kept out of the deliverable repository ZIP to respect Kuku's confidentiality note.
- The heuristic output is not human-labelled ground truth. Its ranking is a baseline only; visual-only hooks and final-video timing remain unverified.

## Heuristic spot-check failures (Round A)
- The heuristic ranked Episode 20 (27s) highly even though its ending includes a question followed by a complete answer: “Not through the winter. I've ensured her quiet comfort.” This is a plot reveal, but not necessarily an unresolved cliffhanger. The keyword/question scorer over-rewards dramatic language without understanding resolution.
- The Episode 21 candidate ends with Juliana taking a ledger from a workbench. That action may be a useful setup, but the text excerpt alone does not establish a sufficiently unresolved payoff. The heuristic does not reason about whether the ending creates a viewer question.
- The Episode 22 candidate ends with an introduction (“Julian, ma'am. New help for the winter cleaning.”) and a tableau. It was selected despite a weak final unresolved beat. The ending scorer can mistake a scene transition or identity detail for a cliffhanger.

These are observed weaknesses in the heuristic baseline, not claimed LLM mistakes. The LLM judge is designed to penalize resolved endings and weak cold-viewer context; its performance remains unmeasured until the Colab run.
