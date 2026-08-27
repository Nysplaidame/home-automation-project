# Troubleshooting Dashboard Design Contract

## Direction

- Product type: read-only operational diagnosis workspace.
- Primary audience: the system owner diagnosing an incident without specialist
  infrastructure knowledge.
- Workflow density: compact enough to compare signals, with one symptom and one
  ordered diagnostic sequence in focus.
- Voice and tone: calm, factual and explicit about uncertainty.
- The UI must not become a generic status-page card grid, a command runner, or
  an automatic remediation console.

## Stack

- Framework: dependency-free HTML and ES modules.
- Styling: app-local CSS with semantic custom properties.
- Component library: native HTML controls.
- Icon library: none; controls use text labels and status marks.
- Fonts: system UI stack; system monospace for commands and technical values.

## Tokens

- Canvas: `#0b1015`.
- Surface: `#111922`.
- Elevated surface: `#17222d`.
- Border: `#2a3947`.
- Text primary: `#edf4f7`.
- Text secondary: `#b8c5cd`.
- Muted text: `#82939e`.
- Accent: `#67d5c2`.
- Success: `#65d68a`.
- Warning: `#f2bd5b`.
- Danger: `#ff7d78`.
- Focus ring: `#8edff4`.

## Typography and layout

- UI font: system sans-serif.
- Technical/value font: `ui-monospace`, SFMono-Regular, Consolas, monospace.
- Base spacing unit: 4px.
- Desktop grid: 280px symptom rail, flexible investigation, 320px evidence.
- Mobile: one column; symptom controls become a compact horizontal list.
- Values and check counts use tabular numerals.

## Components

- Buttons and file inputs use visible hover, pressed and focus states.
- Status is always conveyed by label and mark, never colour alone.
- Panels are top-level workspace regions; avoid cards nested inside cards.
- Diagnostic steps are bordered rows with stage, command, expected result and
  failure interpretation.
- Empty/error states explain which evidence is missing and how to obtain it.

## Accessibility and verification

- Target: WCAG 2.2 AA.
- All interactions are native keyboard controls with visible focus rings.
- Status changes use a polite live region; import failures use an alert region.
- Required viewports: 1440x1000 desktop and 390x844 mobile.
- Respect reduced motion and do not animate diagnostic state changes.
