# Hero Copy Catalog

Cross-run archive of accepted hero copy. Consulted by `hero-copywriter`
before generating new candidates to avoid near-duplicates.

## Format

```yaml
- date: YYYY-MM-DD
  project: <name>
  pattern: paper-title-inversion | stop-start | first-reordering | confession | rule-of-three
  hero: "<verbatim copy>"
  outcome: shipped | rejected | superseded
  audience: hackathon-judges | investors | customers | internal-team | conference-audience
  notes: <optional>
```

## Entries

```yaml
- date: 2026-04-26
  project: Preview Forge
  pattern: paper-title-inversion
  hero: "Preview is all you need."
  outcome: shipped
  audience: hackathon-judges
  notes: |
    Echoes Vaswani et al. 2017 cadence. Doubles as YouTube title +
    submission summary header. F4 primary, F11 echo.
```
