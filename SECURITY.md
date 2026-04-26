# Security Policy

## Supported versions

PitchForge is currently in pre-release. Once v1.0.0 ships, this section will
list the supported version range.

| Version | Supported |
|---|---|
| 0.x.x   | best-effort during pre-release |
| 1.0.x   | (not yet released) |

## Reporting a vulnerability

Email security disclosures to **app.2weeks@gmail.com** with the subject
`[PitchForge security]`. Do not open public issues for security concerns.

We commit to:

- Acknowledging receipt within 7 days.
- Initial assessment within 14 days.
- Remediating critical issues within 30 days.

## Threat model (pre-release)

PitchForge runs entirely inside Claude Code on the user's local machine. The
generated decks are HTML files opened in the user's browser. Concerns we
explicitly track:

| Surface | Concern | Mitigation |
|---|---|---|
| User-supplied brief content | XSS injection into generated HTML | All template substitutions HTML-escape user content; a Layer-0 hook validates no raw `<script>` tags reach the deck |
| Recording mode keyboard handler | Cmd/Ctrl/Alt browser shortcuts being hijacked | `cmd-modifier-guard` hook fails the build if the handler doesn't early-return on modifier presence |
| File system writes | Run output paths escaping the workspace | All `runs/<id>/` paths go through a sanitizer that rejects `..` and absolute paths |
| External CDN dependency | Pulling in untrusted scripts | Templates ship with zero external CDN references; the `no-external-cdn` hook validates this before publish |
| Font / image assets | Tracking pixels in third-party assets | The `oklch-warm-gold` palette uses pure CSS; no image assets ship with the plugin |

## Out of scope

- The browser used to render the deck. (User responsibility.)
- The screen-capture tool used for recording. (OBS, Loom, QuickTime — user choice.)
- Voice-over audio recorded externally. (Not part of PitchForge.)
