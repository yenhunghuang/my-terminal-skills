---
name: ui-ux-pro-max
description: Help choose or refine UI visual direction, typography, layout, and interaction design when the task needs design judgment. Use the existing product stack and design system when present.
---

# UI/UX Design

Start from the user's visual references, product goals, and existing components and tokens. Make design decisions at the scope of the requested change; a component fix does not require generating a new design system.

Use the model's design judgment directly. This portable skill does not bundle a working search script or design database. Do not call `scripts/search.py` or require a database search. If database-backed recommendations are explicitly requested, locate a working installation or explain that the resource is missing.

- Follow the existing stack and visual language. For new work, select a suitable approach from the task constraints rather than imposing a framework.
- Treat palette, spacing, typography, icon style, and animation as design choices rather than universal constants. Respect supplied branding and avoid generating persistent design-system documents unless they help the requested deliverable.
- Preserve accessible semantics, keyboard and focus behavior, readable contrast, and reduced-motion support in affected interactions.
- Inspect the rendered result at relevant viewport sizes and exercise changed interactions. Fix clipping, layout shifts, overflow, and unusable states; verify themes only when the product supports them.

Report the delivered design and meaningful verification. Additional searches or iterations should resolve a specific design uncertainty.
