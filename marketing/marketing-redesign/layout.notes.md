# Layout / font notes

The new design adds **Newsreader** and **JetBrains Mono** to the existing **Inter**. Manrope can be retired.

## Option A — Keep using Google Fonts via CSS @import

The `globals.css` in this folder already imports the three fonts. No change to `app/layout.tsx` needed.

## Option B — Use `next/font` (recommended for production)

In `app/layout.tsx`:

```tsx
import { Inter, Newsreader, JetBrains_Mono } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
});

const newsreader = Newsreader({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  style: ['normal', 'italic'],
  variable: '--font-newsreader',
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jetbrains',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${newsreader.variable} ${jetbrains.variable}`}>
      <body>
        <Masthead />
        {children}
        <Footer />
      </body>
    </html>
  );
}
```

Then in `globals.css`, replace the `@import` line at the top with the CSS variables:

```css
:root {
  --font-ui: var(--font-inter), 'Inter', -apple-system, sans-serif;
  --font-serif: var(--font-newsreader), 'Newsreader', Georgia, serif;
  --font-mono: var(--font-jetbrains), 'JetBrains Mono', ui-monospace, monospace;
}
```

This avoids the FOUC and is faster.
