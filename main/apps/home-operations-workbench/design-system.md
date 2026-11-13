# Home Operations Workbench design system

## Direction

The workbench is a compact, read-only evidence surface for a homeowner or
operator who needs to decide what to inspect next. It should feel like a calm
field notebook for household operations, not a general household portal or a
control console. A visible evidence timestamp, source label, and uncertainty
state remain in view while people move between tasks, incidents, recovery,
food, and commissioning.

The product is a local proof of concept. It does not connect to a live source,
so unknown, stale, and planned-offline states must remain explicit rather than
being styled as a failure or a pass.

## Stack

- Static HTML, local CSS, and browser-native ES modules.
- No component library, remote font, third-party script, or network request.
- `models.js` normalizes schema 1.0 evidence before rendering it.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| Canvas | `#0b1015` | Page background and subtle technical grid |
| Surface | `#111922` | Cards and controls |
| Raised surface | `#17222d` | Interactive controls |
| Border | `#2a3947` | Structural boundaries |
| Main text | `#edf4f7` | Primary reading text |
| Secondary text | `#b8c5cd` | Supporting explanation |
| Muted text | `#82939e` | Timestamps and incomplete evidence |
| Accent | `#67d5c2` | Navigation and trusted links |
| Healthy | `#65d68a` | Positive evidence only |
| Warning | `#f2bd5b` | Review or incomplete recovery evidence |
| Danger | `#ff7d78` | Failed evidence only |
| Focus | `#8edff4` | Keyboard focus ring |

System sans-serif text keeps dense records readable; monospace is reserved for
compact status marks and operational metadata. Card radius is 14px and the
base spacing unit is 8px.

## Interaction and accessibility

- The five section buttons use the tab pattern with arrow, Home, and End key
  navigation.
- Every imported status is represented by text as well as colour.
- The file input has a visible label; all actions retain text labels.
- Safe links open in a separate tab with `noopener noreferrer`.
- The layout is verified at 1440 × 1000 and 390 × 844. On narrow screens,
  cards and evidence cells collapse to one column without horizontal overflow.
- Motion is reduced when the system requests reduced motion.

## Guardrails

Do not add controls that can run remediation, send a command, persist an edit,
or imply a live connection unless the relevant source repository, credentials,
and deployment contract have been reviewed first.
