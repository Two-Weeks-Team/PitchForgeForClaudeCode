# Recording Playbook

> Audience: **video-production team** receiving a PitchForge recording kit.
> You did not author the deck. You record it.
>
> If you have a `recording-kit.tar.gz` in front of you, this document tells
> you exactly what to do with it.

---

## What you received

A recording kit is a tarball produced by `scripts/build-recording-kit.py`.
Extract it and you will see:

```
<project-name>-<runtime>-recording-kit/
├── deck-cinematic.html       # the recording source — open in a browser
├── voiceover-script.md       # frame-by-frame VO + delivery notes
├── recording-checklist.md    # per-take pre-flight checklist
├── take-log.csv              # tracking template — one row per take
├── obs-profile.json          # OBS Studio scene profile (optional import)
├── README.md                 # this file (run-specific copy)
└── meta.json                 # run id, runtime, arc, hero, key visuals
```

Open `deck-cinematic.html` once before reading further.
**Press F11 for fullscreen, then press `O`** — that gives you the opening
sequence (~25–35s depending on arc). If anything looks broken in that
sequence, stop here and report back to the producer; do not start
recording.

---

## Why this protocol exists

PitchForge decks are designed so a single browser tab can serve as the
entire production environment. There is no separate slideshow software,
no separate animation engine, no separate teleprompter. The deck *is*
all of it. That works only if you treat the keyboard as the cue track.

Three layered modes coexist on the same page:

| Mode | Trigger | What's visible | When to use |
|---|---|---|---|
| **Review** | (default) | Top bar + canvas + voiceover script + control panel | First playback. Read the script. |
| **Recording** | `R` key | Canvas only — chrome hidden, dark border, floating ● timer | Take management between cinematics. |
| **Cinematic** | `O` (opening) or `F` (full) | Recording mode + on-canvas VO subtitles also hidden + auto-advance + 3-2-1-GO countdown | The actual capture. |

`Cinematic` is what OBS / Loom / your screen capture is pointed at.
After the `O` or `F` keypress the deck runs autonomously to completion,
shows an `END` overlay, then idles on the last slide. The recorder
stops the capture at that moment.

---

## Pre-flight checklist

> Run through this **once per session**, not per take. Record the
> answers in `recording-checklist.md` (or its take-log column).

### Hardware

- [ ] Mic: condenser or shotgun · pop filter on · spaced 6–8 inches from mouth
- [ ] Mic level: peaks under −6 dBFS, RMS around −18 dBFS
- [ ] Headphones (closed-back, monitoring through OBS)
- [ ] Display: 1920×1080 minimum; 2560×1440 or 4K preferred
- [ ] Display: dark mode forced (no toggle to white background mid-take)
- [ ] No notification banners (mute Slack / iMessage / mail / calendar / focus mode on)
- [ ] Keyboard backlight off (clicks register as ASMR otherwise)

### Software — browser

- [ ] Chrome 113+, Safari 17+, or Firefox 113+ (OKLCH support required)
- [ ] Cache cleared, no extensions enabled (Vimium, password managers
      can intercept keys → break the keymap)
- [ ] Bookmarks bar hidden
- [ ] Zoom level 100%
- [ ] Open `deck-cinematic.html` via `file://` not via dev server

### Software — OBS Studio

Suggested scene profile is in `obs-profile.json`. If you import it:

- Window capture targeting the browser
- 1920×1080 base canvas, 30 fps
- Output: H.264, two-pass, 12,000 kbps video / 256 kbps AAC audio
- Mic/Aux source pointed at your interface
- Recording format: `mkv` (safer against crashes); remux to `mp4` later

If you import manually:
1. Sources → Window Capture → pick the browser window
2. Resize the source to fit 1920×1080
3. Audio Mixer → Mic/Aux → ensure metering shows green
4. Settings → Output → Output Mode = Advanced
   - Recording → Type = Standard
   - Recording Format = mkv
   - Encoder = x264 (or hardware h264 if available)
   - Rate Control = CBR · Bitrate = 12000 Kbps
5. Settings → Video → Base Resolution 1920×1080 · Output 1920×1080 · FPS 30

### Software — environment

- [ ] Mouse/trackpad disabled or pushed off-screen (no accidental clicks)
- [ ] Caps Lock off (modifier confusion)
- [ ] No shell session foregrounded (browser must own the input focus)

---

## Recording session flow

The deck supports two range presets:

| Key | Range | Typical runtime | Use case |
|---|---|---|---|
| `O` | Opening only (wow → first thrill beat) | 25–35 s | Social-media teaser, hero loop |
| `F` | Full demo (wow → outro) | 45–300 s depending on arc | Submission video, marketplace listing |

A custom range can be triggered from the JS console with
`playRange(<start_position>, <end_position>, '<label>')` — frame
positions are 1-indexed and visible in the deck overview (`Esc` key).

### Per-take procedure

```
1. Open deck-cinematic.html. Press F11 → fullscreen.
2. Read voiceover-script.md once silently. Visualize the cadence.
3. Click OBS → Start Recording. Wait 2 seconds.
4. Switch focus to the browser. Press O (or F).
   ↓
   3-2-1-GO countdown overlays the screen for 4 seconds.
   This is your prep window — settle into the chair, draw breath.
   ↓
   Cinematic playback begins. Read the VO line for each beat as it appears.
   Hold the hero copy. Each. Syllable.
   ↓
   END overlay appears. Hold silence for 1–2 seconds.
5. Click OBS → Stop Recording.
6. Log this take in take-log.csv (take number, range, outcome).
```

**Total user input during the take: one keypress (`O` or `F`).**

### Re-take without leaving the page

If a take goes wrong mid-cinematic:

- Press `P` to replay the *current* slide cleanly. Use this when the
  voiceover stumbles on a single beat — drop the take, replay, do it
  again.
- Press `R` to exit recording mode, do whatever needs doing
  (browser refresh, debug panel), then `R` again to re-enter.
- Press `Esc` to open the slide overview, click any tile to jump.

### Take rule of thumb

**5 takes minimum. Keep best of 5.** First take is always rusty. Take 3
or 4 usually lands. Take 5 is the safety net. Beyond 5, fatigue wins —
break for water.

---

## Voiceover delivery rules

These are mechanical. The `voiceover-script.md` file in your kit
already encodes them per beat, but the principles are:

### Doumont staccato

Replace commas with periods. Each fragment is a breath.

> *Tests pass and specs are locked but the product is still wrong, every single time.*

becomes

> *Tests pass. Specs lock. Product wrong. Every. Single. Time.*

The period is not punctuation. It's a breath instruction. **Read the
period.** Each fragment is its own beat.

### Em-dash held breath

When you see `—` in the script, that's a 0.4–0.6 s held breath. Not a
comma (smaller beat). Not a period (full closure). The em-dash is
suspense.

> *"The harness self-corrects — until it earns the score."*

Pause on the em-dash. Let the audience lean in.

### Hero copy slow-down

The hero copy is the single highest-leverage line in the deck. It
appears at the wow beat (typically F4) and echoes at the outro
(typically F11). Read it slowly. **Each. Syllable. Lands.**

> *"Pre · view · is · all · you · need."*

After the hero, hold half a beat of silence. The audience exhales.
*Then* the next line.

### Three acts

| Act | Tone |
|---|---|
| **Act A — agro** | Prosecutor opening. Cold. Confront, do not describe. No smile. |
| **Act B — drop** | Keynote reveal. Steve Jobs slow drop. Then go quiet. |
| **Act C — thrill** | Maker showing peers their workshop. Casual. Confident. |

The voiceover-script tags each beat with its act so you know which
mode to be in.

### NEVER list (auto-rejected by the tone auditor)

If you find yourself saying any of these, cut the take. The script
should already have these scrubbed, but watch your improvisation:

- *"as you can see"* → tutorial filler
- *"in this video we'll see"* → narration self-reference
- *"let me show you"* → hospitality opener
- *"thanks for watching"* → YouTube boilerplate
- Uptalk on declaratives (insecurity tone)
- *"like, um, basically"* (any disfluency)
- Adverb chains (*"really very actually fast"* → pick one word)

---

## Trouble­shooting

### The countdown didn't start when I pressed `O`

You probably pressed `Cmd+O` or `Ctrl+O` accidentally — the deck's
keyboard handler intentionally early-returns on modifier keys so the
browser's open-file dialog gets through. Press `O` alone (no modifier).

### The deck advanced before I finished my line

Each beat has a fixed duration encoded in `frame-spec.json`. The
duration is the **maximum** time the audience holds the visual; you
should land your VO **inside** that budget. If you genuinely need more
time on a beat, ask the producer to regenerate the deck with a longer
duration for that frame — do not stretch your delivery to fill it.

### The hero gallery on F4 has obvious frame drops

Disable hardware acceleration in the browser (Settings → System), close
Chrome's other tabs, and check that you're not running the deck inside
an OBS browser source (use the actual Chrome window with OBS Window
Capture pointed at it).

### The recording timer (●) is visible in my capture

It shouldn't be — `body.cinematic #rec-timer { display: none !important }`
is in the deck's CSS. If you see it, you're in **Recording mode**, not
**Cinematic mode**. Press `O` or `F` to enter cinematic; `R` toggles
plain recording mode and *does* show the timer.

### The voiceover overlay ribbon is showing in my capture

Same diagnosis as above. In cinematic mode, `body.cinematic .vo-overlay`
is hidden. If you see it, you're in plain recording mode.

### Cmd+F or Cmd+R or any browser shortcut got intercepted

It shouldn't — this is a Layer-0 guarantee (lesson L1 in
`memory/LESSONS.md`). The keydown handler early-returns on metaKey,
ctrlKey, and altKey. If a browser shortcut got eaten, the deck is
non-conformant; report it.

---

## What to deliver back

For each accepted take, the producer expects:

- The raw `mkv` (or `mp4`) file
- The take number from `take-log.csv` plus a one-line outcome note
- Your loudness reading (LUFS, peak)
- A 30-second muted clip from the take's wow beat (F4) for sanity
  preview without sharing the whole video

Do not transcode, color-correct, or trim. The producer handles editing
based on raw takes.

---

## Cross-references

For curious operators:

- `methodology/03-tone-energy.md` — full delivery ruleset
- `methodology/06-animation-timing.md` — what's animating when
- `methodology/07-recording-protocol.md` — keymap + mode CSS spec
- `memory/LESSONS.md` — historical failure modes (L1 modifier keys, L2
  grid rows, L3 hero hold, L4 reorder reflow, L5 cinematic timer leak)

You don't need to read these to record. They explain *why* the deck
behaves the way it does if you ever wonder.
