# Methodology 02 — Hero Copy Patterns (Cross-cutting)

The hero copy is one line that carries the entire pitch. It becomes:
the YouTube title, the submission summary header, the README h1, the social-card preview,
and the on-canvas overlay at the wow-reveal beat.

PitchForge ships **five inversion patterns**. Each is a tested narrative shape
that compresses a paradigm into 5–9 words.

---

## Pattern 1 — Paper-title inversion ★

```
[Subject] is all you need.
```

Echoes Vaswani et al. 2017 (*Attention Is All You Need*). The cadence alone
signals "this is a paradigm-shift claim." AI/ML reviewers recognize the
pattern in 0.5 seconds.

**Examples**:
- *"Preview is all you need."* (Preview Forge)
- *"Speed is all you need."*
- *"Latency is all you need."*

**Use when**: technical audience, AI/ML adjacent, paradigm-shift framing fits.

**Avoid when**: consumer products, non-technical viewers, claim is incremental.

---

## Pattern 2 — Stop-Start inversion

```
Stop [old-behavior]. Start [new-behavior].
```

Confrontational. Names the old behavior pejoratively, then names the new
behavior with active verbs.

**Examples**:
- *"Stop chatting with AI. Start engineering with it."* (Citadel-class)
- *"Stop drawing wireframes. Start picking pictures."*

**Use when**: opinionated framing fits, audience is sophisticated, behavior
change is the message.

---

## Pattern 3 — First reordering

```
[Thing] first.
```

Two words. Implies a new ordering of an established sequence. The audience
fills in what came before.

**Examples**:
- *"Result first."* (this plugin's F3 heading)
- *"Demo first."*
- *"Picture first."*

**Use when**: the entire pitch is about reversing an established order.

---

## Pattern 4 — Confession

```
We've been [doing it wrong].
```

Active first person. Includes the speaker in the indictment.

**Examples**:
- *"We've been lying."* (this plugin's F1 heading)
- *"We've been building backwards."*
- *"We've been wireframing too late."*

**Use when**: opening agro hook, prosecutor tone, problem-first arc.

---

## Pattern 5 — Rule of three

```
[N] [thing-A]. [N] [thing-B]. [N] [outcome].
```

Three short clauses with parallel structure. Numbers register on the
viewer's mental notepad.

**Examples**:
- *"144 personas. One plugin. Two clicks."* (Preview Forge F5)
- *"30 frames. 7 phases. 1 file."*
- *"5 minutes. 3 questions. 1 deck."*

**Use when**: the kick beat, demonstrating scale, closing a Wow.

---

## `/pitch:hero` returns five candidates

The agent `agents/writers/hero-copywriter.md` runs all five patterns over
the brief's `project_one_liner` and returns one candidate per pattern. The
user picks (or rejects all and asks for more).

---

## Anti-patterns (rejected automatically)

| Anti-pattern | Why rejected |
|---|---|
| `Introducing [X]` | Generic launch copy. No paradigm signal. |
| `[X] for [Y]` | Targeting language belongs in description, not hero. |
| `Welcome to [X]` | Hospitality opener. Fails the 0.5-second recognition test. |
| Three+ sentences | Hero must be one line. |
| Adjective stack (`fast, secure, scalable [X]`) | Marketing checkbox copy. |

---

## Hero copy placement rules (`heroDelivery`)

The hero is delivered at most twice in a video:

1. **Primary placement**: at the wow-reveal beat (F4 in `wow-first`, F4 in `problem-first`, end of Act I in `story`, F4 in `teaser`).
2. **Echo placement**: at the outro (F11 in all arcs).

If the runtime is ≥ 240s, also consider a **mid-hero rephrasing** at the act break.

---

## Voiceover delivery rules

- Read the hero copy slowly. Each syllable lands.
- *"Pre · view · is · all · you · need."* — five clicks of the tongue.
- Half-beat silence after.
- The audience exhales.
- Then the next line.

---

## Cross-run learning

Each pitch's accepted hero copy is appended to `memory/HERO_CATALOG.md`:

```yaml
- date: 2026-04-26
  project: Preview Forge
  pattern: paper-title-inversion
  hero: "Preview is all you need."
  outcome: shipped
  audience: hackathon-judges
```

Next time the user runs `/pitch:hero` on a similar project, the catalog
is consulted to avoid suggesting a near-duplicate.

---

## Cross-references

- `agents/writers/hero-copywriter.md` — the agent.
- `commands/hero.md` — the standalone command.
- `memory/HERO_CATALOG.md` — cross-run archive.
