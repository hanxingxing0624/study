# UI Redesign: Refined Minimal + Accent

## Goal

Replace the current Material-style UI with a refined minimal aesthetic — zinc/gray monochrome foundation, single electric blue accent, generous whitespace, and subtle interactive details.

## Scope

**In scope:**
- Rebuild CSS variable system (colors only — layout vars unchanged)
- Overhaul all component styles: cards, buttons, badges, forms, sidebar nav, stats
- Polish all 8 template pages to match
- Refine knowledge graph SVG colors
- Add refined micro-interactions (hover, focus, transitions)

**Out of scope:**
- New pages or features
- Template structure changes (same HTML, different classes/colors)
- Dark mode
- JavaScript behavior changes

## Design System

### Color Palette

```
Background:     #fafafa
Surface:        #ffffff
Border:         #f4f4f5  (hairline, currently #e8eaed)
Text-primary:   #18181b  (zinc-900)
Text-secondary: #71717a  (zinc-500)
Text-muted:     #a1a1aa  (zinc-400)
Accent:         #2563eb  (electric blue)
Accent-hover:   #1d4ed8
Danger:         #ef4444
Success:        #16a34a
```

### Component Changes

**Cards:**
- Border: #f4f4f5 (barely visible)
- Hover: border darkens to #e4e4ed, subtle shadow
- Remove current #d2d5d8 hover border

**Buttons:**
- Primary: near-black (#18181b) bg, white text. Hover: #3f3f46
- Secondary: #f4f4f5 bg, #3f3f46 text. Hover: #e4e4ed
- Danger: keep red, toned down
- Remove current blue primary button

**Badges (status):**
- All badges: unified gray bg (#f4f4f5), dark text (#3f3f46)
- Hover state or active badge: blue bg (#eff6ff), blue text (#2563eb)
- Remove the colored badge system (orange/blue/green)

**Stats cards:**
- Remove colored icon backgrounds
- Use monochrome icons + top accent border on "active" stat only
- Stat numbers: tighter, larger, bolder

**Sidebar:**
- Pure white bg, no shadow
- Logo: dark gradient monochrome square
- Nav items: 5px dot indicators replace emoji icons
- Active state: gray bg + dark text (not blue)
- Section labels: smaller, wider letter-spacing

**Forms:**
- Softer focus ring (2px #2563eb, reduced opacity)
- Wider padding on inputs
- Cleaner select dropdown styling

### Template-Specific Changes

1. **Dashboard (index.html):** "Good morning" greeting, refined stat cards, cleaner panels
2. **Note view (note_view.html):** Tighter sidebar link lists, monochrome review info card
3. **Note edit (note_edit.html):** Cleaner editor wrapper border, refined form layout
4. **Folders (folders.html):** Lighter tree indentation lines, monochrome folder icons
5. **Tags (tags.html):** Refined tag cloud, cleaner inline edit forms
6. **Review (review.html):** Review buttons: grayscale gradient with blue top
7. **Graph (graph.html):** Node colors match new palette, lighter edge lines
8. **Search (search.html):** Cleaner search bar, refined result cards

### Micro-interactions

- Card hover: 150ms border + shadow transition
- Button hover: 150ms bg transition
- Nav item hover: 120ms bg transition
- Page loads: no artificial transition (SSR, instant)

## Implementation Approach

**Single-file dominant change:** ~80% of the work is rewriting `static/css/style.css`. The templates need minor class adjustments.

**File impact:**
- `static/css/style.css` — full rewrite of color values, component styles
- `templates/base.html` — sidebar markup (icons → dots)
- `templates/index.html` — greeting text, minor class tweaks
- `templates/graph.html` — D3 color values
- All other templates — minimal changes (badge classes, color references)

## Success Criteria

- Visual consistency across all 8 pages
- No layout breakage at responsive breakpoints
- All interactive elements have visible hover/active states
- Sidebar navigation equally usable (dot indicators must be clear)
