---
description: Deterministic replay of a past run from trace.jsonl. Re-applies every phase agent's input and verifies the output matches byte-for-byte (drift detection).
---

# /pitch:replay <run_id>

Deterministic replay. Useful for:

- Regression testing — does the same brief still produce the same deck?
- Debugging — when a regenerated artifact diverges from the original.
- Plugin self-test — the v0.1.0 acceptance test re-runs the reference
  deck's brief and diffs the output (see `tests/e2e/`).

## Usage

```bash
/pitch:replay runs/2026-04-27-preview-forge

# Strict — fail on any byte-level difference
/pitch:replay runs/2026-04-27-preview-forge --strict

# Tolerant — allow whitespace differences
/pitch:replay runs/2026-04-27-preview-forge --tolerant
```

## How it works

`trace.jsonl` records, per phase:

- which agent ran;
- the input artifacts' hashes;
- the output artifacts' hashes;
- the tier (auto/guided/master);
- the timestamp and token count.

Replay reads `trace.jsonl` from start, re-invokes each agent with the
recorded input, and diffs the produced output against the recorded
output hashes.

## Verdict

```
=== Replay runs/2026-04-27-preview-forge ===
P1 brief.json:                ✅ identical (sha256 match)
P2 scenario.md:               ✅ identical
P2 frame-spec.json:           ✅ identical
P3 storyboard.html:           ⚠ differs (12 byte delta)
                               → diff: timestamp drift on F8 (1:20:14 vs 1:20:00)
P4 frame-spec.json (post-VO): ✅ identical
P5 deck.html:                 ⚠ differs (downstream of P3)
…

Replay status: 2 phases drifted. Likely cause: P3 used a fresh time
when rendering meta-tags. Run --tolerant to accept clock-related drift.
```

## When replay fails

- A model output changed → log the divergence to `LESSONS.md` if it's a
  new failure pattern.
- A schema changed → update the run's pinned `_schema_version` and
  re-run the affected phases.
- A hero copy was paraphrased downstream → that's a Layer-0 Rule 4
  violation; surface as a hard fail.

## Cross-references

- `agents/meta/pitch-supervisor.md` § "trace.jsonl"
- `tests/e2e/regenerate-reference-deck.sh` (v0.1.0 acceptance test)
