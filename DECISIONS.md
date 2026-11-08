# Decisions and format reconnaissance

## Chosen problem
Problem 1: Find the Promos. The supplied 50-episode screenplay pack is real input, output is timestamp-checkable, and the workflow can be rerun on a new show.

## Observed input format
- 50 UTF-8 text files, episodes numbered 1–50; each begins with episode number, logline and continuity notes.
- Timed blocks use `**LABEL:**`, then `Start: (mm:ss.cc) | End: (mm:ss.cc)`, then prose/dialogue.
- Labels include CAMERA, ACTION, SOUND FX and named characters with emotion/tone tags. Blocks overlap (e.g. dialogue over camera directions); parser preserves beat IDs and times rather than treating them as a single non-overlapping timeline.
- Timestamps reset by episode. Scene headings and scene duration are present but scene counts vary. Several episodes contain explicit `cliffhanger` wording, but absence of that literal word is not evidence that a beat is not a cliffhanger.
- Parser diagnostics count Start markers versus parsed blocks and retain warnings.

## Alias map (provisional; do not merge ambiguous roles automatically)
- LADY JULIANA / JULIANA → Juliana (provisional, based on loglines and script dialogue).
- THE FORMER GROOM → Gerald (continuity notes explicitly identify him).
- LADY IN GOLD GOWN → Clarissa in the opening wedding context (logline/continuity); confirm on a new show before generalizing.
- MATRIARCH, BLOND NOBLEMAN, LADY CATHERINE and other role labels are retained as distinct labels unless continuity establishes identity.

## Series arc (10-line orientation, logline-derived)
1. Juliana is publicly abandoned by fiancé Gerald in favour of her sister Clarissa.
2. Her family compounds the humiliation rather than defending her.
3. Juliana's path intersects with a wounded/secretive soldier, Alexander.
4. The story develops a marriage/romance and aristocratic identity mystery around Alexander.
5. Juliana navigates hostile aristocratic households and power struggles.
6. The Duchess household and its succession/political interests become central.
7. Poisoning and the Dowager Duchess's safety become a major threat.
8. Lady Catherine and other antagonists use coercion, secrecy and alliances.
9. Later episodes broaden into scandal, blackmail and hidden relationships.
10. Episode 50's logline ends on Agnes witnessing Catherine and Father Thomas's intimacy.

## Operational definitions
- **Hook:** A beat or compact beat sequence that begins at clip start and establishes a high-stakes disruption, provocative line, reveal, threat, physical action or emotionally legible reaction within 0–3 seconds. Text cues alone are provisional; visual-only hooks are not detectable from screenplay text.
- **Cliffhanger:** The final beat leaves a concrete question, danger, decision, identity, exposure or consequence unresolved. Cut at the last complete beat before the answer/payoff; never claim a cliffhanger solely because a script says the word.
- **Standalone:** A cold viewer can identify the immediate relationship/roles and the immediate stake from information inside the clip, without relying on earlier episodes. If not, reject or add a separate segment only if it creates coherent context.

## Scope and assumptions
- Target 25–45 seconds; hard duration 20–60 seconds.
- Return up to 15 ranked candidates across the show, with no more than two per episode in the initial diversity pass.
- Prefer earlier episodes modestly to support viewer acquisition; avoid knowingly spoiling late-series twists.
- Screenplay timestamps are proxies for final video timestamps, not guaranteed sync.
- Editor reviews every candidate before posting.
- First iteration prioritizes one continuous segment. Composite/flash-forward promos are deferred until a validated continuous baseline exists.

## Design choices
- Code owns parsing, time conversion, duration limits and validation. The model should select beat IDs and judge story quality, never invent timestamps.
- Keep model adapters swappable; provider/model are configuration. Heuristic mode is always available without credentials.
- Use an editor-facing ranked shortlist rather than auto-publishing.
