---
version: alpha
name: OpenCode Configger Design Spec
colors:
  primary: "#26FF8C"
  secondary: "#2A2A2A"
  success: "#26FF8C"
  info: "#00E0FF"
  warning: "#FFD600"
  danger: "#FF2D55"
  background: "#050505"
  surface: "#0D0D0D"
  error: "#FF2D55"
  banner: "#26FF8C"
  on-primary: "#050505"
  on-background: "#F2F2F2"
  on-surface: "#F2F2F2"
  text-primary: "#F2F2F2"
  text-secondary: "#888888"
  text-muted: "#555555"
  border: "#2A2A2A"
  node-provider: "#00E0FF"
  node-agent: "#26FF8C"
  node-tool: "#FFD600"
  node-command: "#B366FF"
  node-formatter: "#FF2D55"
  node-mcp: "#00E0FF"
  node-lsp: "#6610F2"
typography:
  headline-lg:
    fontFamily: sans-serif
    fontSize: 18px
    fontWeight: 200
    lineHeight: 1.1
  body-md:
    fontFamily: sans-serif
    fontSize: 12px
    fontWeight: 300
    lineHeight: 1.5
  body-sm:
    fontFamily: sans-serif
    fontSize: 11px
    fontWeight: 300
    lineHeight: 1.5
  label-md:
    fontFamily: sans-serif
    fontSize: 12px
    fontWeight: 400
  code:
    fontFamily: monospace
    fontSize: 12px
spacing:
  xs: 6px
  md: 10px
  lg: 16px
  xl: 24px
rounded:
  sm: 0px
  md: 0px
  lg: 0px
  full: 9999px
shadow:
  glow-green: "0 0 8px #26FF8C"
  glow-red: "0 0 8px #FF2D55"
  glow-cyan: "0 0 8px #00E0FF"
---

# Cinematic Neon Design System

## Philosophy
OpenCode Configger is an immersive cockpit for configuration engineering. The aesthetic is **Obsidian Cinematic**: a dark-room HUD environment that prioritizes depth, high-contrast neon accents, and razor-sharp typography. It rejects soft, generic "modern" interfaces in favor of a brutalist, high-fidelity technical workspace.

## Color Palette: The Obsidian Spectrum
The interface is anchored in near-total darkness, allowing semantic data to "glow" with neon intensity.

### Core Tones
- **Obsidian (#050505):** The void. Used for the primary background to minimize eye strain and maximize cinematic depth.
- **Ebonized Surface (#0D0D0D):** Used for elevated containers, input backgrounds, and distinct UI regions.
- **Krypton Accent (#26FF8C):** A piercing neon green used for primary actions, active states, and success indicators.
- **Mist White (#F2F2F2):** High-contrast text for critical readability.

### Semantic Glow
- **Danger/Error (#FF2D55):** A vibrant cherry-red for destructive actions and validation failures.
- **Warning (#FFD600):** Sharp yellow for high-attention alerts.
- **Info (#00E0FF):** Cyan glow for auxiliary data and passive information.

### Architecture Graph Semantics
The graph uses a highly saturated, glowing palette against the obsidian background:
- **Provider:** Cyan (#00E0FF)
- **Agent:** Krypton (#26FF8C)
- **Tool:** Warning (#FFD600)
- **Command:** Ultraviolet (#B366FF)
- **Formatter:** Cherry (#FF2D55)

## Typography: Razor-Thin Precision
The system leverages ultra-light weights to create a "technical blueprint" feel.

- **Headlines:** `headline-lg` (18px, Ultra-Light/200) - Used for major navigational anchors.
- **Labels:** `label-md` (12px, Regular/400) - Tight, focused labels for configuration keys.
- **Body:** `body-md` (12px, Light/300) - Spaced out for maximum legibility in complex views.
- **Code:** `monospace` (12px) - Razor-sharp monospaced type for raw data editing.

## Layout: Brutalist Structure
A strict grid system with zero-radius corners to emphasize the industrial, technical nature of the tool.

- **Zero Rounding:** All buttons, inputs, and frames use sharp, 90-degree corners (`rounded: 0px`).
- **Negative Space:** Generous spacing (`lg: 16px`) between logical groups to prevent visual clutter in dense configurations.
- **Vertical Rhythm:** Fixed label widths (180px) ensure a mechanical, organized flow of data.

## Component Execution

### HUD Panels (Collapsible Sections)
Containers that feel like panels in a cockpit. 
- **Header:** Mist White text on a thin Charcoal border.
- **Toggle:** A simple `+` or `-` in Krypton green.

### Inputs: The Glass Buffer
- **Background:** Ebonized (#0D0D0D).
- **Border:** Transparent by default, glowing Krypton (#26FF8C) when focused.
- **Validation:** When invalid, the entire entry frame glows with a Cherry-Red (#FF2D55) shadow/border.

### Architecture Canvas
A dark-on-dark visualization. Nodes are glowing rings with 1px strokes, connected by faint, translucent lines.

## Do's and Don'ts
- **Do** use high-contrast text against obsidian backgrounds.
- **Do** maintain sharp 0px corners on all interactive elements.
- **Don't** use gradients, shadows, or rounded corners.
- **Don't** use desaturated "grey" backgrounds; stay within the Obsidian/Ebonized spectrum.

## Implementation Tokens
These CSS-variable-style tokens map directly to the color palette above and should be used consistently across all UI code:

| Token | Value | Usage |
|-------|-------|-------|
| `--color-background` | `#050505` | Root window background |
| `--color-surface` | `#0D0D0D` | Card/panel backgrounds |
| `--color-border` | `#2A2A2A` | Subtle borders |
| `--color-primary` | `#26FF8C` | Primary actions, focus rings |
| `--color-danger` | `#FF2D55` | Error states, destructive actions |
| `--color-warning` | `#FFD600` | Warnings |
| `--color-info` | `#00E0FF` | Info labels, links |
| `--color-text-primary` | `#F2F2F2` | Primary text |
| `--color-text-secondary` | `#888888` | Secondary/muted text |
| `--color-text-muted` | `#555555` | Placeholder text |

**Glow effects**: Use `shadow: glow-green` for focused inputs, `shadow: glow-red` for error borders. In tkinter, apply via `highlightbackground` with corresponding glow colors.

