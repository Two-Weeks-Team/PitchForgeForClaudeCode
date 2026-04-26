# Lessons (cross-run)

Auto-appended by the `auto-retro` critic at the end of each run that exposed
a recurring failure mode. Reviewed by every agent before generating a new
plan in the next run.

Each entry has the format:

```
## L<N> — <one-line summary>
- Date: YYYY-MM-DD
- Phase: P1 | P2 | P3 | P4 | P5 | P6 | P7 | cross
- Trigger: what surfaced the failure
- Root cause: why it happened
- Mitigation: what every future run should do
- Fixture: tests/fixtures/<dir>/ (regression test if applicable)
```

---

## L1 — Modifier keys must never be intercepted by deck handlers

- Date: 2026-04-26
- Phase: P7 (recording)
- Trigger: User pressed `Cmd+R` to reload a generated deck. Browser refresh
  was blocked AND the recording-mode toggle fired, leaving a stale ● timer
  on screen.
- Root cause: `keydown` handler matched on `e.key === 'r'` regardless of
  `e.metaKey` / `e.ctrlKey` / `e.altKey`.
- Mitigation: Every generated deck's keyboard switch starts with
  `if (e.metaKey || e.ctrlKey || e.altKey) return;`. Layer-0 hook
  `cmd-modifier-guard.py` validates this string is present before publish.
- Fixture: `tests/fixtures/cmd-modifier-guard/` (pending v0.1.0).

## L2 — Grid auto-flow places visible items into the FIRST track when display:none ones are stripped

- Date: 2026-04-26
- Phase: P7 (recording mode CSS)
- Trigger: Recording mode hid `topbar` and `navbar` (3 grid children → 1).
  The remaining `body` was placed in the 0-height first row of
  `grid-template-rows: 0 1fr 0`. Result: entire viewport showed only the
  slide background color.
- Root cause: CSS Grid auto-flow scans tracks left-to-right / top-to-bottom
  for unfilled cells; `display: none` items don't reserve a track.
- Mitigation: In `body.rec`, set `grid-template-rows: 1fr` (single track)
  and `grid-row: 1 !important` on `.body`. Never use multi-track with
  conditional `display:none` on grid children.
- Fixture: `tests/fixtures/rec-mode-grid/` (pending).

## L3 — Hero copy must hold for ≥ 5 seconds even after F4 trim

- Date: 2026-04-26
- Phase: P3 / P6
- Trigger: User reduced F4 hero hold from 30s to 10s. Hero word reveal
  finishes around 2.88s (last word "need." animates from 1.98s for 0.9s).
  Echo-mini at 3.4s. Vo-overlay at 4.0s. With a 10s budget, hero is
  visible from ~2.88s to 10s = 7.1s. Adequate but tight.
- Root cause: Hero animations were timed for 30s budget, not 10s.
- Mitigation: When the assembler computes hero placement, ensure the
  hold (full appearance to next-slide transition) is ≥ 5 seconds. If
  the budget is < 8s, compress hero word-reveal stagger from 0.12s to
  0.08s per word.
- Fixture: pending.

## L4 — Reordering slides must reflow ALL timestamps, not just the moved frame

- Date: 2026-04-26
- Phase: P2 / P5
- Trigger: User asked to move F4 from position 5 → position 2. Manual
  reorder caught the 4 directly-affected timestamps but missed F5's
  `time` field (still showed `0:55–1:00` after F3 ended at 0:35).
  SLIDE_DURATION array also out of sync.
- Root cause: Eleven separate `time` fields scattered across HTML +
  one JS array — too many places for a manual edit to cover.
- Mitigation: `/pitch:reorder` regenerates all timestamps + array
  + summary metadata + button labels in a single pass from `frames-spec.json`.
  Never edit timestamps in HTML directly.
- Fixture: `tests/fixtures/reorder-reflow/` (pending v0.5.0).

## L5 — Floating recording timer leaks into cinematic recordings

- Date: 2026-04-26
- Phase: P7
- Trigger: User entered cinematic mode (`O` key) but the floating
  ● timer that helps in plain rec mode also showed in cinematic capture.
- Root cause: Two layered modes (`body.rec` vs `body.cinematic`)
  weren't differentiated for the floating timer.
- Mitigation: `body.cinematic #rec-timer { display: none !important }`
  overrides `body.rec` reveal. Cinematic = absolutely clean canvas.
- Fixture: pending.
