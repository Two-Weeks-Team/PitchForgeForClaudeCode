# Methodology 06 — Animation Timing (Phase P6)

Every animated element falls into one of two engines:

## CSS engine

For elements with deterministic appearance (fade / slide / pop / glow / strikethrough). Driven by:

```html
<el data-anim="up" style="--d:.6s">...</el>
```

The shared CSS rules in `templates/deck-shell.html` interpret `data-anim` ∈ {`fade`, `up`, `right`, `pop`, `spawn`, `glow`, `strike`, `reveal`, `bloom`, `land`} with the delay coming from `--d`. Elements outside the `.slide.active` slide are forced to `opacity: 0`; activation triggers the animation.

This engine handles ~80% of frame motion.

## JS engine

For motion that depends on stateful interpolation:

| Effect | Mechanism |
|---|---|
| Counter rolling (0 → 144 with eased curve) | `requestAnimationFrame` loop, eased cubic |
| Score with intermediate stops (0 → 412 → 478 → 499) | Same loop with `data-stops` array |
| Typewriter (per-char append) | `setTimeout` per char with `data-tw-dur` total budget |
| Tile stagger (30 tiles, 30ms apart) | Sequential `setTimeout` injecting opacity transitions |
| Cursor path (off-screen → target with curve) | CSS keyframes with custom `from`/`to` positions |

Drivers live in the deck's inline `<script>` block and are invoked from the slide-change hook.

## Timing budget per frame

The default beat duration sets the upper bound. Inside that budget:

```
0.0–0.2s    : heading slide-up
0.2–1.0s    : staggered element entrances
1.0–2.0s    : feature interactions (counter, typewriter, etc.)
2.0–N.0s    : hold (most of the budget)
N-1.0–N.0s  : optional "set up next slide" easing
```

Heading first, hold last. The hold is what gives the audience time to read.

## Animation re-trigger on slide revisit

When a user navigates back to a slide that has already played, animations must restart. Mechanism in the deck's JS:

```js
slides[i].classList.remove('active');
void slides[i].offsetWidth;   // force reflow
slides[i].classList.add('active');
```

The reflow nudge is required — without it, CSS keyframes don't restart even though the class toggled.

## Cross-references

- `agents/engineers/animation-engineer.md`
- `templates/deck-shell.html` — the CSS engine implementation
