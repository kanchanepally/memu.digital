# Memu Marketing — Redesign Handoff

A drop-in refresh for the existing `marketing/` Next.js site, applying the illustration-led editorial design system from `Memu Marketing Site.html`.

## What's in this folder

```
marketing-redesign/
├── README.md                              ← you are here
├── globals.css                            ← REPLACES marketing/app/globals.css
├── components/
│   ├── Logo.tsx                           ← REPLACES marketing/components/Logo.tsx
│   ├── Marks.tsx                          ← NEW (illustration system)
│   ├── Masthead.tsx                       ← REPLACES marketing/components/Masthead.tsx
│   └── Footer.tsx                         ← REPLACES marketing/components/Footer.tsx
├── app/
│   ├── page.tsx                           ← REPLACES marketing/app/page.tsx (home)
│   ├── platform/page.tsx                  ← REPLACES marketing/app/platform/page.tsx
│   ├── how/page.tsx                       ← REPLACES marketing/app/how/page.tsx
│   ├── privacy/page.tsx                   ← REPLACES marketing/app/privacy/page.tsx
│   └── self-host/page.tsx                 ← REPLACES marketing/app/self-host/page.tsx
└── layout.notes.md                        ← notes for layout.tsx font additions
```

## Design system summary

**Type**
- Display + reading: **Newsreader** (serif, italic-friendly, editorial)
- UI + body: **Inter** (already in use)
- Numerals + code chips: **JetBrains Mono** (new)

**Color**
- Brand: `#5054B5` indigo (unchanged)
- Surfaces refined to warm-cool off-white `#FAF9FB`, sidebar tint `#F4F2F8`
- Dark mode supported via `data-theme="dark"` on `<html>` (full token map in globals.css)

**Illustrations**
- 14 custom hand-drawn monoline marks (`components/Marks.tsx`) — Weekend, Meals, Missing, Privacy, Space, Conversation, Time, Empty, Walls, Engine, Thread, Receipts, Sovereign, Family, Lens, Garden
- All take `{ size, color }` props
- Drawn at 56–80px viewport with soft inner fills

**Animations**
- Subtle button lift on hover (defined in globals.css)
- Card lift on hover for `.card`
- Pulse animation on status dots (`.pulse-dot`)

## Porting steps (Claude Code / Gemini)

1. **Add fonts to `app/layout.tsx`**
   - Replace the existing Inter + Manrope `@import` in globals.css with the line below
   - Or use `next/font` (recommended). See `layout.notes.md` for the `next/font` snippet
2. **Replace** `app/globals.css` with `globals.css` from this folder. Review and merge any custom rules.
3. **Replace** the 4 components in `components/` (`Logo.tsx`, `Masthead.tsx`, `Footer.tsx`, plus add the new `Marks.tsx`)
4. **Replace** the 5 page files in `app/` with the versions in this folder
5. (Optional) The `TwinDemo` component is referenced by the new `/how` page. The redesign includes its own inline before/after demo card, but if you want to keep the live `TwinDemo` component, swap the inline demo for `<TwinDemo />`
6. (Optional) The `HeroCycler` component is referenced by the new home page. If you keep it, drop it under the new serif hero — the redesign omits it but supports it

## Light/dark mode

The CSS uses `[data-theme="dark"]` on the `<html>` element. You can either:
- Always-light: do nothing (default)
- Add a theme toggle: read `prefers-color-scheme` or persist user choice → set `document.documentElement.dataset.theme`

## Notes for refining

- Hero illustrations are absolutely positioned `top-right` — at small viewports they may need to hide. The CSS has a `@media (max-width: 720px)` rule that hides `.hero-mark` on mobile
- Comparison table on the home page uses a different markup than the existing one — review `app/page.tsx` and decide whether to keep your `TABLE_ROWS` array or use the inline version
- Some pages use `<em>` inline for the italic-serif accent. Style is in `.serif-accent` class — `<span className="serif-accent">` works the same
