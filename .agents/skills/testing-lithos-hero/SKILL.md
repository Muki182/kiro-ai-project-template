---
name: testing-lithos-hero
description: Test the Lithos hero section (Vite + React + Tailwind) end-to-end, especially the cursor spotlight reveal. Use when verifying the Lithos hero UI or any cursor-driven canvas-mask reveal feature.
---

# Testing the Lithos hero

The Lithos hero is a single-route Vite + React + TS + Tailwind page (`src/App.tsx` -> `src/components/Hero.tsx`). No auth, no backend, no secrets.

## Run it locally
```bash
npm install        # already in blueprint maintenance
npm run dev        # serves http://localhost:5173
npm run build      # tsc -b && vite build
npm run lint       # eslint
```

## Devin Secrets Needed
None — frontend-only, runs entirely on localhost.

## What to verify (primary flow)
1. **Initial render**: nav pill (Course active + Field Guides/Geology/Plans/Live Tour), Sign Up, Playfair-italic title "Layers hold / tales of time", two corner paragraphs, orange "Start Digging" button — all over the dark base image.
2. **Cursor spotlight reveal (core)**: move the mouse over the hero. A soft-edged circle under the cursor should reveal a *different* image (a green mossy / wildflower terrain) over the dark base image, and the circle must *follow* the cursor (with easing) — the place you left returns to the base image. If both images look identical or the circle doesn't move, the canvas mask (`RevealLayer`, `toDataURL` -> `maskImage`) is broken.
3. **CTA hover**: hovering "Start Digging" adds an orange glow/shadow and a slight scale-up.
4. **Responsive**: below `md` (768px) the center pill + desktop Sign Up hide and a hamburger (lucide `Menu`) appears; below `sm` (640px) the bottom-left paragraph hides and the bottom-right block goes full width.

## Environment gotchas (Windows + computer tool)
- **The `type` action drops the `:` character** in this Windows GUI environment. Typing a URL like `http://localhost:5173` ends up as `httplocalhost5173` and fails. Workaround: type the host (`localhost`), then send the colon with a `key` action `shift+semicolon`, then type the rest (`5173/`). This likely applies to any colon you need to type in the browser.
- Chrome is already running and maximized; just use the address bar. The desktop may have the Start menu open on first screenshot — press Escape / click the page to dismiss.
- For responsive checks, DevTools device mode (`Ctrl+Shift+M`) is a clean way to set an exact mobile width (e.g. 400px). Toggle DevTools with `F12`.
- The spotlight follows the cursor with smooth easing via `requestAnimationFrame`; nudge the mouse 1-2px and wait a beat before screenshotting so the eased position settles.

## Evidence
Record the spotlight following the cursor (two cursor positions) — that single before/after is the highest-signal proof the feature works.
