# Methodology 03 — Tone Energy (Phase P4)

Voiceover that sounds AI-narrated kills a pitch. PitchForge ships a
mechanical ruleset that detects AI tone and rewrites it into human-presenter
energy.

The default tone is **`agro-drop-thrill`** — three-act delivery shape:

```
Act A — agro    : confront, don't describe
Act B — drop    : reveal the answer like you've been waiting all year
Act C — thrill  : show off — and you've earned it
```

---

## The Doumont staccato rule

Replace commas with periods. Each fragment is its own beat.

**Before** (AI-narrated):
> "Tests pass and specs are locked but the product is still wrong, every single time."

**After** (Doumont staccato):
> "Tests pass. Specs lock. Product wrong. Every. Single. Time."

The period is not punctuation. It is a breath instruction.

---

## NEVER list (auto-rejected)

| Pattern | Why |
|---|---|
| `as you can see` | Tutorial filler. |
| `in this video we'll see` | Narration self-reference. |
| `let me show you` | Hospitality opener. |
| `thanks for watching` | YouTube boilerplate. |
| Uptalk on declaratives | Insecurity tone. |
| `like, um, basically` | Verbal disfluency markers. |
| Adverb chains (`really very actually`) | Filler. |
| Smooth-overs of confrontation (`well, kind of, sort of`) | Defangs the agro beat. |

The `tone-auditor` agent flags any of these in a generated voiceover and
the `tone-editor` agent rewrites.

---

## ALWAYS list (the three acts)

### Act A — agro (cold open + indictment)

- Open like you've already lost patience with the room.
- *"Here's the lie."* / *"We've been lying."* — confessional present tense.
- No smile.
- Pause **before** every key fragment, not after.
- Drop pitch on staccato endings. *"Every. Single. Time."* = three discrete beats.

**Tone**: prosecutor opening statement.

---

### Act B — drop (pivot + wow)

- *"So we flipped it."* — say it like you've solved something.
- Then go quiet.
- *"Look. Twenty-six futures of your idea."* — pause.
- Then the hero line, slowly. *"Pre · view · is · all · you · need."*
- Half-beat silence after the hero. The audience exhales.

**Tone**: keynote reveal — Steve Jobs slow drop.

---

### Act C — thrill (architecture + payoff)

- *"How? 144 personas."* — the question is for the audience.
- *"Yeah, 144."* — casual confirmation.
- *"Now watch."* — pointing at the screen.
- *"Click two. Done."* — drop the tool onto the workbench.
- *"Three minutes ago — this was one line."* — quiet awe.

**Tone**: maker who built the thing, talking to peers.

---

## Mapping arc beats to acts

| Arc | Act A beats | Act B beats | Act C beats |
|---|---|---|---|
| `wow-first` | F1, F2 | F3, F4 | F5–F11 |
| `problem-first` | F1, F2 | F3, F4 | F5–F11 |
| `teaser` | (skipped) | F4 | F5, F11 |
| `story` | Act I beats | Act II climax | Act III beats |

---

## The em-dash convention

In the voiceover script, an em-dash means **held breath**.

```
"The harness self-corrects — until it earns the score."
"Three minutes ago — this was one line."
```

The recording presenter inserts a 0.4–0.6s pause where the em-dash sits.
Not a comma — that's a smaller beat. Not a period — that's a closure.
The em-dash is suspense.

---

## Tone audit (the rule mechanically applied)

`agents/reviewers/tone-auditor.md` runs on any generated `scenario.md`:

```
For each VO line:
  - count NEVER-list patterns → flag if > 0
  - count Doumont fragments (period-separated) → flag if avg > 12 words
  - count first-person verbs ("we", "you", "I") → flag if 0 in opening 3 lines
  - count em-dashes used as held-breath → flag if 0 in Act B
  - count rhetorical questions in Act C → flag if 0
  
If any flag fires, hand to tone-editor with the specific rule violated.
```

---

## Tone profile alternatives (v0.5+)

The `wave-2` of the plugin supports profile flags:

| Profile | When |
|---|---|
| `agro-drop-thrill` | Default. Hackathon, tech-keynote, founder pitch. |
| `calm-academic` | Conference talk, educational, technical deep-dive. |
| `playful-warm` | Consumer launch, lifestyle product. |
| `corporate-clean` | B2B, enterprise sales, internal company kickoff. |

Each profile ships its own NEVER/ALWAYS lists and act-mapping defaults.
v0.1.0 ships `agro-drop-thrill` only.

---

## Cross-references

- `agents/writers/tone-editor.md` — rewrites VO into the chosen profile.
- `agents/reviewers/tone-auditor.md` — flags violations.
- `commands/tone.md` — `/pitch:tone` standalone command.
