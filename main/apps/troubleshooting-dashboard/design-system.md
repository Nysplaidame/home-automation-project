# Troubleshooting Dashboard Design Contract

## Direction

- Product type: read-only operational diagnosis workspace.
- Primary audience: the system owner diagnosing an incident without specialist
  infrastructure knowledge.
- Workflow density: reading-first, with a numbered journey and one expanded
  diagnostic check initially.
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
- Border: `#354856`.
- Text primary: `#edf4f7`.
- Text secondary: `#c2ced5`.
- Muted text: `#a5b6c1`.
- Accent: `#67d5c2`.
- Success: `#65d68a`.
- Warning: `#f2bd5b`.
- Danger: `#ff7d78`.
- Focus ring: `#8edff4`.

## Typography and layout

- UI font: system sans-serif.
- Technical/value font: `ui-monospace`, SFMono-Regular, Consolas, monospace.
- Base spacing unit: 4px.
- Body and instruction text: 18px with 1.6 line height; supporting copy and
  commands at least 16px; small status/index labels at least 14.4px.
- Desktop: 300px problem rail and a wide investigation; recorded evidence below
  the investigation, not in a competing third column. Maximum width 1500px.
- Mobile: one column with searchable problem choices grouped by area. Selecting a problem
  moves to evidence collection; commands wrap and controls are at least 48px.
- Numbered sections: choose a problem, add evidence, follow checks, review results.
- Put collection instructions beside upload, explain missing/old evidence, and
  expose expected results and execution host inside each expandable check.
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
