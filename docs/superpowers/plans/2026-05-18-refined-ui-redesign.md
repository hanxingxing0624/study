# UI Redesign: Refined Minimal + Accent

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Material-style UI with refined minimal zinc/gray monochrome + electric blue accent design system.

**Architecture:** Single CSS variable rebuild drives all component changes. `style.css` absorbs ~80% of work; templates get minor class/markup adjustments. No JS changes, no new pages, no dark mode.

**Tech Stack:** Vanilla CSS (CSS custom properties), Jinja2 templates, D3.js (graph colors only)

---

### Task 1: Rebuild CSS Variables & Base

**Files:**
- Modify: `static/css/style.css:1-36`

- [ ] **Step 1: Replace `:root` variable block**

Replace current `:root` block (lines 2-24) with the new color palette:

```css
:root {
    --bg: #fafafa;
    --surface: #ffffff;
    --border: #f4f4f5;
    --border-hover: #e4e4ed;
    --text: #18181b;
    --text-secondary: #71717a;
    --text-muted: #a1a1aa;
    --accent: #2563eb;
    --accent-hover: #1d4ed8;
    --accent-light: #eff6ff;
    --danger: #ef4444;
    --danger-hover: #dc2626;
    --success: #16a34a;
    --radius: 8px;
    --radius-sm: 6px;
    --shadow-sm: 0 1px 2px rgba(0,0,0,0.03);
    --shadow: 0 1px 3px rgba(0,0,0,0.05);
    --shadow-lg: 0 4px 12px rgba(0,0,0,0.06);
    --sidebar-width: 220px;
}
```

- [ ] **Step 2: Update `body` font and color**

Replace the body rule (lines 29-37):

```css
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans SC", "Microsoft YaHei", "Inter", sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
    display: flex;
    min-height: 100vh;
    -webkit-font-smoothing: antialiased;
    letter-spacing: -0.01em;
}
```

- [ ] **Step 3: Update heading styles**

Replace `h2` and `h4` rules (lines 41-44):

```css
h2 { font-size: 1.2rem; margin-bottom: 1.25rem; color: var(--text); font-weight: 700; letter-spacing: -0.02em; }
h3 { font-size: 1rem; margin-bottom: 0.5rem; font-weight: 600; }
h4 { font-size: 0.72rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.6rem; font-weight: 600; }
```

- [ ] **Step 4: Verify the variable changes**

Start the dev server and confirm no broken styles:

```bash
cd d:\aiTools\aicode\study && uvicorn main:app --reload --port 8000 &
```
Open `http://localhost:8000` — colors should look different but layout intact.

---

### Task 2: Rebuild Sidebar Navigation

**Files:**
- Modify: `static/css/style.css:47-174` (sidebar section)
- Modify: `templates/base.html:19-57` (nav markup)

- [ ] **Step 1: Replace all sidebar CSS rules**

Replace lines 47-174 in style.css:

```css
nav.sidebar {
    width: var(--sidebar-width);
    background: var(--surface);
    border-right: 1px solid var(--border);
    padding: 0;
    display: flex;
    flex-direction: column;
    position: fixed;
    top: 0; left: 0; bottom: 0;
    z-index: 100;
    overflow-y: auto;
}

nav.sidebar .sidebar-header {
    padding: 1.25rem 1rem 0.75rem;
}

nav.sidebar .sidebar-header h1 {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--text);
    letter-spacing: -0.01em;
}

nav.sidebar .sidebar-header h1 a {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: var(--text);
    text-decoration: none;
}

nav.sidebar .sidebar-header .logo-icon {
    width: 24px; height: 24px;
    background: linear-gradient(135deg, #18181b, #3f3f46);
    border-radius: 5px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 0.7rem;
    font-weight: 800;
}

nav.sidebar .sidebar-search {
    padding: 0 0.75rem;
    margin-bottom: 0.5rem;
}

nav.sidebar .sidebar-search input {
    width: 100%;
    padding: 0.35rem 0.5rem 0.35rem 1.8rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.78rem;
    background: var(--bg) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' fill='%23a1a1aa' viewBox='0 0 16 16'%3E%3Cpath d='M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001c.03.04.062.078.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1.007 1.007 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0z'%3E%3C/path%3E%3C/svg%3E") 0.5rem center no-repeat;
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
}

nav.sidebar .sidebar-search input:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(37,99,235,0.1);
}

nav.sidebar .sidebar-nav {
    padding: 0.5rem 0.6rem;
    flex: 1;
}

nav.sidebar .nav-group {
    margin-bottom: 1rem;
}

nav.sidebar .nav-label {
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    letter-spacing: 0.07em;
    padding: 0 0.5rem;
    margin-bottom: 0.25rem;
}

nav.sidebar .nav-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0.5rem;
    border-radius: 5px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.82rem;
    font-weight: 450;
    transition: background 0.12s, color 0.12s;
    cursor: pointer;
}

nav.sidebar .nav-item:hover {
    background: #f4f4f5;
    color: var(--text);
    text-decoration: none;
}

nav.sidebar .nav-item .nav-dot {
    width: 5px; height: 5px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.35;
    flex-shrink: 0;
}

nav.sidebar .nav-item.active {
    background: #f4f4f5;
    color: var(--text);
    font-weight: 550;
}

nav.sidebar .nav-item.active .nav-dot {
    opacity: 1;
    background: var(--accent);
}

nav.sidebar .sidebar-footer {
    padding: 0.5rem 0.75rem;
    border-top: 1px solid var(--border);
    font-size: 0.6rem;
    color: var(--text-muted);
}
```

- [ ] **Step 2: Replace sidebar nav HTML in base.html**

Replace lines 19-57 in `templates/base.html` — change emoji icons to dot indicators:

```html
    <nav class="sidebar">
        <div class="sidebar-header">
            <h1>
                <a href="/">
                    <span class="logo-icon">N</span>
                    Notes
                </a>
            </h1>
        </div>
        <div class="sidebar-search">
            <form action="/search" method="get">
                <input type="search" name="q" placeholder="Search notes...">
            </form>
        </div>
        <div class="sidebar-nav">
            <div class="nav-group">
                <div class="nav-label">Workspace</div>
                <a href="/" class="nav-item">
                    <span class="nav-dot"></span> Dashboard
                </a>
                <a href="/notes/new" class="nav-item">
                    <span class="nav-dot"></span> New Note
                </a>
            </div>
            <div class="nav-group">
                <div class="nav-label">Browse</div>
                <a href="/folders" class="nav-item">
                    <span class="nav-dot"></span> Folders
                </a>
                <a href="/tags" class="nav-item">
                    <span class="nav-dot"></span> Tags
                </a>
                <a href="/review" class="nav-item">
                    <span class="nav-dot"></span> Review
                </a>
                <a href="/graph" class="nav-item">
                    <span class="nav-dot"></span> Knowledge Graph
                </a>
            </div>
        </div>
        <div class="sidebar-footer">v0.1.0</div>
    </nav>
```

- [ ] **Step 3: Verify sidebar**

Refresh `http://localhost:8000` — sidebar should show dot indicators, monochrome logo, cleaner layout.

---

### Task 3: Rebuild Button Styles

**Files:**
- Modify: `static/css/style.css:200-238` (button section)

- [ ] **Step 1: Replace all button CSS rules**

Replace lines 200-238:

```css
.btn {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.4rem 0.85rem;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    font-weight: 500;
    text-align: center;
    text-decoration: none;
    background: #18181b;
    color: #fff;
    transition: background 0.15s, box-shadow 0.15s;
    white-space: nowrap;
    line-height: 1.4;
    letter-spacing: -0.01em;
}
.btn:hover { background: #3f3f46; text-decoration: none; color: #fff; }
.btn:active { transform: scale(0.98); }

.btn-secondary {
    background: #f4f4f5;
    color: #3f3f46;
}
.btn-secondary:hover { background: #e4e4ed; color: #18181b; }

.btn-danger { background: var(--danger); }
.btn-danger:hover { background: var(--danger-hover); }

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
    padding: 0.25rem 0.4rem;
}
.btn-ghost:hover { background: #f4f4f5; color: var(--text); box-shadow: none; }

.btn-sm { padding: 0.2rem 0.5rem; font-size: 0.75rem; }
.btn-lg { padding: 0.5rem 1rem; font-size: 0.85rem; }
```

- [ ] **Step 2: Verify buttons**

Refresh browser, check `/notes/new` page — Save button should be near-black, Cancel button should be gray.

---

### Task 4: Rebuild Cards, Badges & Stats

**Files:**
- Modify: `static/css/style.css:240-340` (cards, stats, badges sections)

- [ ] **Step 1: Replace card styles**

Replace lines 240-280:

```css
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.9rem 1rem;
    margin-bottom: 0.5rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.card:hover {
    border-color: var(--border-hover);
    box-shadow: var(--shadow-sm);
}

.card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 0.5rem;
}

.card-title {
    font-size: 0.9rem;
    font-weight: 550;
    color: var(--text);
    margin-bottom: 0.15rem;
    letter-spacing: -0.01em;
}

.card-title a { color: var(--text); }
.card-title a:hover { color: var(--accent); text-decoration: none; }

.card-meta {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    font-size: 0.73rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
}

.card-meta span { display: inline-flex; align-items: center; gap: 0.15rem; }
```

- [ ] **Step 2: Replace stats grid styles**

Replace the stats-grid and stat-card rules (lines 285-326):

```css
.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.85rem;
    transition: border-color 0.15s, box-shadow 0.15s;
}
.stat-card:hover { border-color: var(--border-hover); box-shadow: var(--shadow-sm); }
.stat-card.featured { border-top: 2px solid var(--accent); }
.stat-card.featured .stat-label { color: var(--accent); }

.stat-icon {
    width: 38px; height: 38px;
    border-radius: 8px;
    background: #f4f4f5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    color: var(--text-secondary);
}
.stat-card.featured .stat-icon {
    background: var(--accent-light);
    color: var(--accent);
}

.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1.1;
    letter-spacing: -0.03em;
}

.stat-label {
    font-size: 0.73rem;
    color: var(--text-muted);
    font-weight: 500;
}
```

- [ ] **Step 3: Replace badge styles**

Replace lines 328-353:

```css
.badge {
    display: inline-block;
    padding: 0.1rem 0.45rem;
    border-radius: 10px;
    font-size: 0.68rem;
    font-weight: 550;
    background: #f4f4f5;
    color: #3f3f46;
}

.badge-tag {
    display: inline-flex;
    align-items: center;
    background: #f4f4f5;
    color: var(--text-secondary);
    padding: 0.15rem 0.5rem;
    border-radius: 10px;
    font-size: 0.75rem;
    font-weight: 500;
    transition: background 0.15s, color 0.15s;
}
.badge-tag:hover { background: var(--accent-light); color: var(--accent); text-decoration: none; }
```

- [ ] **Step 4: Remove old badge status color classes**

Delete lines 338-341 (the `.badge-planning`, `.badge-in-progress`, `.badge-completed` rules). They are no longer needed — all badges use the unified gray style.

---

### Task 5: Rebuild Form Styles

**Files:**
- Modify: `static/css/style.css:355-398`

- [ ] **Step 1: Replace form styles**

```css
.form-group { margin-bottom: 0.85rem; }

.form-group label {
    display: block;
    font-weight: 550;
    margin-bottom: 0.25rem;
    font-size: 0.78rem;
    color: var(--text-secondary);
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 0.5rem 0.6rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.85rem;
    font-family: inherit;
    color: var(--text);
    background: var(--surface);
    transition: border-color 0.15s, box-shadow 0.15s;
    outline: none;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(37,99,235,0.08);
}

.form-group input::placeholder,
.form-group textarea::placeholder { color: var(--text-muted); }

.form-group textarea { resize: vertical; min-height: 120px; }

.form-row { display: flex; gap: 1rem; align-items: flex-end; }
.form-row .form-group { flex: 1; }
.form-row .form-group.flex-none { flex: none; }

select { cursor: pointer; appearance: none; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%23a1a1aa' viewBox='0 0 16 16'%3E%3Cpath d='M8 11L3 6h10z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 0.5rem center; padding-right: 1.75rem; }
```

---

### Task 6: Rebuild Remaining CSS Sections

**Files:**
- Modify: `static/css/style.css` (markdown, editor, tables, flash, folders, tags, graph, review, empty, responsive, utilities)

- [ ] **Step 1: Replace markdown content styles**

Replace lines 427-479:

```css
.markdown-body { line-height: 1.8; color: var(--text); }

.markdown-body h1, .markdown-body h2, .markdown-body h3,
.markdown-body h4, .markdown-body h5 {
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--text);
}
.markdown-body h1 { font-size: 1.5rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }
.markdown-body h2 { font-size: 1.2rem; }
.markdown-body h3 { font-size: 1.05rem; }

.markdown-body p { margin-bottom: 0.75rem; }

.markdown-body pre {
    background: #18181b;
    color: #e4e4e7;
    padding: 0.9rem 1rem;
    border-radius: var(--radius);
    overflow-x: auto;
    font-size: 0.8rem;
    line-height: 1.55;
    margin: 0.75rem 0;
}

.markdown-body code {
    font-family: "JetBrains Mono", "Fira Code", "Cascadia Code", monospace;
    font-size: 0.84em;
}

.markdown-body :not(pre) > code {
    background: #f4f4f5;
    color: #18181b;
    padding: 0.1rem 0.3rem;
    border-radius: 4px;
    font-weight: 500;
}

.markdown-body blockquote {
    border-left: 2px solid var(--accent);
    padding: 0.25rem 0 0.25rem 0.85rem;
    color: var(--text-secondary);
    margin: 0.75rem 0;
    background: #fafafa;
    border-radius: 0 4px 4px 0;
}

.markdown-body table { margin: 0.75rem 0; }
.markdown-body th, .markdown-body td { padding: 0.4rem 0.65rem; font-size: 0.82rem; }
.markdown-body img { max-width: 100%; border-radius: var(--radius); }
.markdown-body ul, .markdown-body ol { padding-left: 1.5rem; margin-bottom: 0.75rem; }
.markdown-body li { margin-bottom: 0.15rem; }
.markdown-body hr { border: none; border-top: 1px solid var(--border); margin: 1.25rem 0; }
```

- [ ] **Step 2: Replace editor wrapper & table styles**

Replace editor styles (lines 481-505):

```css
.editor-wrapper {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 0.75rem;
}

.toastui-editor-defaultUI {
    border: none !important;
    border-radius: 0 !important;
}

.toastui-editor-defaultUI-toolbar {
    background: #fafafa !important;
    border-bottom: 1px solid var(--border) !important;
}

.toastui-editor-defaultUI .toastui-editor-md-container {
    background: var(--surface) !important;
}

.toastui-editor-defaultUI .toastui-editor-ww-container {
    background: var(--surface) !important;
}
```

Replace table styles (lines 413-424):

```css
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.5rem 0.65rem; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.84rem; }
th {
    font-size: 0.7rem;
    text-transform: uppercase;
    color: var(--text-muted);
    font-weight: 600;
    letter-spacing: 0.05em;
    background: #fafafa;
}
tr:hover td { background: #fafafa; }
```

- [ ] **Step 3: Replace folder tree styles**

Replace lines 601-625:

```css
.folder-tree { margin-top: 0.5rem; }

.folder-tree-item {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0.4rem;
    border-radius: var(--radius-sm);
    font-size: 0.85rem;
    transition: background 0.12s;
    color: var(--text-secondary);
}
.folder-tree-item:hover { background: #f4f4f5; }

.folder-tree-item a { color: var(--text); flex: 1; font-weight: 450; }
.folder-tree-item a:hover { color: var(--accent); text-decoration: none; }

.folder-tree-item .folder-icon { color: var(--text-muted); font-size: 0.8rem; }

.folder-tree-children {
    padding-left: 1.2rem;
    border-left: 1px solid var(--border);
    margin-left: 0.6rem;
}
```

- [ ] **Step 4: Replace tag cloud styles**

Replace lines 566-600:

```css
.tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.5rem;
}

.tag-cloud-item {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.3rem 0.6rem;
    background: #f4f4f5;
    border: 1px solid transparent;
    border-radius: 8px;
    font-size: 0.82rem;
    color: var(--text-secondary);
    text-decoration: none;
    transition: all 0.15s;
}
.tag-cloud-item:hover {
    background: var(--accent-light);
    border-color: rgba(37,99,235,0.2);
    color: var(--accent);
    text-decoration: none;
}
.tag-cloud-item .tag-count {
    font-size: 0.68rem;
    color: var(--text-muted);
    background: rgba(0,0,0,0.04);
    padding: 0.08rem 0.4rem;
    border-radius: 8px;
}
```

- [ ] **Step 5: Replace review button styles**

Replace lines 654-683:

```css
.review-buttons {
    display: flex;
    gap: 0.4rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
}

.review-btn {
    flex: 1;
    min-width: 60px;
    padding: 0.55rem 0.35rem;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.75rem;
    font-weight: 550;
    text-align: center;
    transition: all 0.15s;
    color: #fff;
}
.review-btn:hover { transform: translateY(-1px); box-shadow: var(--shadow); }

.review-btn-0 { background: #f4f4f5; color: #a1a1aa; }
.review-btn-1 { background: #e4e4e7; color: #71717a; }
.review-btn-2 { background: #d4d4d8; color: #3f3f46; }
.review-btn-3 { background: #a1a1aa; color: #fff; }
.review-btn-4 { background: #52525b; color: #fff; }
.review-btn-5 { background: #2563eb; color: #fff; }
```

- [ ] **Step 6: Replace empty state, graph, flash, note sidebar, responsive, and utilities**

Replace empty state (lines 637-653):

```css
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: var(--text-muted);
}

.empty-state .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
    opacity: 0.3;
}

.empty-state p {
    font-size: 0.85rem;
    margin-bottom: 0.75rem;
}
```

Replace graph container (lines 626-635):

```css
.graph-container {
    width: 100%;
    height: 70vh;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    background: var(--surface);
    overflow: hidden;
}
```

Replace flash messages (lines 399-412):

```css
.flash {
    padding: 0.6rem 0.85rem;
    border-radius: 6px;
    margin-bottom: 0.85rem;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.flash-success { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
.flash-error { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
.flash-info { background: var(--accent-light); color: var(--accent); border: 1px solid #bfdbfe; }
```

Replace note sidebar (lines 528-565):

```css
.note-layout {
    display: flex;
    gap: 1.5rem;
}

.note-main {
    flex: 1;
    min-width: 0;
}

.note-sidebar {
    width: 220px;
    flex-shrink: 0;
}

.note-sidebar h4 {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
    font-weight: 600;
}

.note-sidebar .link-list {
    list-style: none;
    padding: 0;
}

.note-sidebar .link-list li {
    padding: 0.2rem 0;
    font-size: 0.82rem;
}

.note-sidebar .link-list li a {
    color: var(--text-secondary);
    text-decoration: none;
}
.note-sidebar .link-list li a:hover {
    color: var(--accent);
}
```

Replace responsive (lines 686-710):

```css
@media (max-width: 768px) {
    nav.sidebar {
        width: 100%;
        position: relative;
        height: auto;
        border-right: none;
        border-bottom: 1px solid var(--border);
        flex-direction: row;
        flex-wrap: wrap;
        padding: 0.5rem;
        gap: 0.25rem;
    }
    nav.sidebar .sidebar-nav { display: flex; gap: 0.25rem; flex-wrap: wrap; padding: 0; }
    nav.sidebar .nav-label { display: none; }
    nav.sidebar .nav-item { font-size: 0.75rem; padding: 0.25rem 0.4rem; }

    main.content { margin-left: 0; padding: 1rem; }

    .stats-grid { grid-template-columns: 1fr; }
    .split-grid { grid-template-columns: 1fr; }
    .note-layout { flex-direction: column; }
    .note-sidebar { width: 100%; }
    .edit-layout { grid-template-columns: 1fr; }
    .form-row { flex-direction: column; }
}
```

Replace utilities and loading (lines 712-724):

```css
.muted { color: var(--text-muted); font-size: 0.82rem; }
.mt-1 { margin-top: 0.4rem; }
.mt-2 { margin-top: 0.85rem; }
.mt-3 { margin-top: 1.25rem; }
.mb-2 { margin-bottom: 0.85rem; }
.mb-3 { margin-bottom: 1.25rem; }
.flex-center { display: flex; align-items: center; gap: 0.4rem; }

.htmx-indicator { opacity: 0; transition: opacity 0.2s; }
.htmx-request .htmx-indicator { opacity: 1; }
.htmx-request.htmx-indicator { opacity: 1; }
```

---

### Task 7: Update Dashboard Template

**Files:**
- Modify: `templates/index.html`

- [ ] **Step 1: Add greeting and update stat card classes**

Replace the index.html content with refined markup:

```html
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block content %}
<div class="page-header">
    <div>
        <h2 style="margin-bottom:0.15rem;">Good morning</h2>
        <p class="muted" style="margin-bottom:0;">{{ stats.due_reviews }} item(s) due for review</p>
    </div>
    <a href="/notes/new" class="btn">New Note</a>
</div>

<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-icon">&#x1f4c4;</div>
        <div>
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">Total Notes</div>
        </div>
    </div>
    <div class="stat-card featured">
        <div class="stat-icon">&#x1f4dd;</div>
        <div>
            <div class="stat-value">{{ stats.in_progress }}</div>
            <div class="stat-label">In Progress</div>
        </div>
    </div>
    <div class="stat-card">
        <div class="stat-icon">&#x1f504;</div>
        <div>
            <div class="stat-value">{{ stats.due_reviews }}</div>
            <div class="stat-label">Due for Review</div>
        </div>
    </div>
</div>

<div class="split-grid">
    <div>
        <h4>Recent Notes</h4>
        {% if recent_notes %}
        {% for note in recent_notes %}
        <div class="card">
            <div class="card-title">
                <a href="/notes/{{ note.id }}">{{ note.title }}</a>
            </div>
            <div class="card-meta">
                <span class="badge">{{ note.status }}</span>
                {% if note.folder %}<span>&#x1f4c1; {{ note.folder.name }}</span>{% endif %}
                <span>{{ note.updated_at.strftime('%Y-%m-%d') }}</span>
            </div>
        </div>
        {% endfor %}
        {% else %}
        <div class="empty-state">
            <div class="empty-icon">&#x1f4dd;</div>
            <p>No notes yet</p>
            <a href="/notes/new" class="btn">Create Your First Note</a>
        </div>
        {% endif %}
    </div>
    <div>
        <h4>Due for Review</h4>
        {% if due_reviews %}
        {% for review in due_reviews %}
        <div class="card">
            <div class="card-title">
                <a href="/notes/{{ review.note.id }}">{{ review.note.title }}</a>
            </div>
            <div class="card-meta">
                <span>Next: {{ review.next_review_at.strftime('%Y-%m-%d') }}</span>
                <span>{{ review.interval }}d interval</span>
            </div>
            <a href="/review/{{ review.note.id }}" class="btn btn-secondary btn-sm mt-1">Review</a>
        </div>
        {% endfor %}
        {% else %}
        <div class="empty-state">
            <div class="empty-icon">&#x2705;</div>
            <p>All caught up</p>
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

---

### Task 8: Update Note Templates & Remaining Templates

**Files:**
- Modify: `templates/note_view.html`
- Modify: `templates/note_edit.html`
- Modify: `templates/graph.html`
- Modify: `templates/folders.html`
- Modify: `templates/tags.html`
- Modify: `templates/review.html`
- Modify: `templates/search.html`

- [ ] **Step 1: Update note_view.html — badge classes**

In `templates/note_view.html`, change line 16:

Old: `<span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>`

New: `<span class="badge">{{ note.status }}</span>`

Also in the sidebar review info card (lines 59-67), change the `h4` color from accent to muted:

Old: `<h4>Review Info</h4>`

Keep as-is but verify it renders with muted text per new CSS.

- [ ] **Step 2: Update note_edit.html — status select badges**

No structural changes needed — the badge class changes in CSS handle the styling. Verify the editor toolbar styling matches by refreshing the page.

- [ ] **Step 3: Update graph.html — D3 colors**

Replace lines 28-31 in `templates/graph.html`:

```javascript
const color = d3.scaleOrdinal()
    .domain(["planning", "in_progress", "completed"])
    .range(["#a1a1aa", "#2563eb", "#16a34a"]);
```

Also change the link stroke from `#ccc` to `#e4e4e7` on line 41:

```javascript
.attr("stroke", "#e4e4e7")
```

And change node text fill from `var(--text)` to `#3f3f46` on line 71:

```javascript
.attr("fill", "#3f3f46");
```

- [ ] **Step 4: Update folders.html — badge classes**

Change line 69:

Old: `<span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>`

New: `<span class="badge">{{ note.status }}</span>`

- [ ] **Step 5: Update review.html — badge classes**

No badge classes to change (review page uses review cards, not status badges). Verify the review grading buttons render with new grayscale gradient.

- [ ] **Step 6: Update search.html — badge classes**

Change line 27:

Old: `<span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>`

New: `<span class="badge">{{ note.status }}</span>`

Also update the search input focus style to use inline styles matching the new accent:

Old (lines 12-13):
```
onfocus="this.style.borderColor='var(--primary)';this.style.boxShadow='0 0 0 2px rgba(26,115,232,0.15)'"
onblur="this.style.borderColor='var(--border)';this.style.boxShadow='none'"
```

New:
```
onfocus="this.style.borderColor='#2563eb';this.style.boxShadow='0 0 0 2px rgba(37,99,235,0.08)'"
onblur="this.style.borderColor='var(--border)';this.style.boxShadow='none'"
```

- [ ] **Step 7: Update tags.html — badge classes**

Change line 17 (in tag detail view):

Old: `<span class="badge badge-{{ note.status.replace('_','-') }}">{{ note.status }}</span>`

New: `<span class="badge">{{ note.status }}</span>`

---

### Task 9: Final Verification

- [ ] **Step 1: Start the server and check all pages**

```bash
cd d:\aiTools\aicode\study && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 2: Verify each page visually**

Open each URL and confirm:
- `/` — Dashboard: greeting text, stat cards with featured blue top border
- `/notes/new` — Editor page: near-black Save button, gray Cancel
- `/notes/1` — Note view (create a note first if needed)
- `/folders` — Folder tree with lighter borders
- `/tags` — Tag cloud with gray chips
- `/review` — Review panel with grayscale buttons
- `/graph` — Graph with new node colors
- `/search?q=test` — Search with new badge style

- [ ] **Step 3: Verify responsive layout**

Resize browser to < 768px width. Confirm:
- Sidebar collapses to horizontal bar
- Stats grid stacks to single column
- Split grid and note layout stack vertically

- [ ] **Step 4: Verify hover states**

Hover over:
- Sidebar nav items (gray bg appears)
- Cards (border darkens to #e4e4ed)
- Buttons (bg changes)
- Tag chips (blue bg appears)

- [ ] **Step 5: Commit**

```bash
git add static/css/style.css templates/
git commit -m "feat: redesign UI with refined minimal zinc/accent style"
```
