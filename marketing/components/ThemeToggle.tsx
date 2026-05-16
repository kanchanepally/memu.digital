'use client';

import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

/**
 * Theme toggle — sun/moon button.
 *
 * Behaviour:
 * 1. First load — reads OS preference via `prefers-color-scheme`
 * 2. Once user clicks — stores their choice in localStorage
 * 3. Persists across reloads
 * 4. Listens for OS-level changes (if user hasn't made a manual choice yet)
 *
 * Drop into Masthead.tsx between nav-links and nav-cta:
 *
 *   <ThemeToggle />
 *
 * Or into the mobile menu as well.
 */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme | null>(null);

  // Initial mount — read stored preference or system default
  useEffect(() => {
    const stored = localStorage.getItem('memu-theme') as Theme | null;
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initial: Theme = stored ?? (systemDark ? 'dark' : 'light');
    setTheme(initial);
    document.documentElement.dataset.theme = initial;

    // Listen for OS changes only if user hasn't made a manual choice
    if (!stored) {
      const mq = window.matchMedia('(prefers-color-scheme: dark)');
      const onChange = (e: MediaQueryListEvent) => {
        const next: Theme = e.matches ? 'dark' : 'light';
        setTheme(next);
        document.documentElement.dataset.theme = next;
      };
      mq.addEventListener('change', onChange);
      return () => mq.removeEventListener('change', onChange);
    }
  }, []);

  const toggle = () => {
    const next: Theme = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.dataset.theme = next;
    localStorage.setItem('memu-theme', next);
  };

  // Don't render until mounted — avoids server/client mismatch flicker
  if (theme === null) {
    return <div style={{ width: 36, height: 36 }} aria-hidden />;
  }

  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggle}
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      title={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      style={{
        width: 36,
        height: 36,
        borderRadius: '50%',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--text-2)',
        transition: 'transform 0.15s ease, color 0.15s ease',
        padding: 0,
      }}
      onMouseEnter={e => (e.currentTarget.style.transform = 'translateY(-1px)')}
      onMouseLeave={e => (e.currentTarget.style.transform = 'translateY(0)')}
    >
      {isDark ? (
        // Sun
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
        </svg>
      ) : (
        // Moon
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
      )}
    </button>
  );
}

/**
 * Prevent theme flash on initial load.
 *
 * Drop this <script> into <head> in app/layout.tsx using `dangerouslySetInnerHTML`
 * BEFORE the <body> renders. It reads localStorage / OS preference synchronously
 * and sets data-theme so the page paints with the correct theme on first frame.
 *
 * Usage in layout.tsx:
 *
 *   <head>
 *     <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
 *   </head>
 */
export const THEME_INIT_SCRIPT = `
  (function() {
    try {
      var stored = localStorage.getItem('memu-theme');
      var systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      var theme = stored || (systemDark ? 'dark' : 'light');
      document.documentElement.dataset.theme = theme;
    } catch (e) {}
  })();
`;
