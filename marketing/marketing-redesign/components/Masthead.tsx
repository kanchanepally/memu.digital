'use client';

import Link from 'next/link';
import { useState } from 'react';
import { LogoLockup } from './Logo';

export function Masthead() {
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { href: '/platform', label: 'Platform' },
    { href: '/how', label: 'How it works' },
    { href: '/privacy', label: 'Privacy' },
    { href: '/self-host', label: 'Self-host' },
  ];

  return (
    <header className="masthead">
      <div className="masthead-inner">
        <Link href="/" onClick={() => setIsOpen(false)}>
          <LogoLockup size={28} />
        </Link>

        <nav className="nav-links">
          {links.map(l => (
            <Link key={l.href} href={l.href} className="nav-link">
              {l.label}
            </Link>
          ))}
        </nav>

        <button
          className="mobile-menu-btn"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {isOpen ? (
              <>
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </>
            ) : (
              <>
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </>
            )}
          </svg>
        </button>

        <a
          href="https://tally.so/r/ODDZvA"
          target="_blank"
          rel="noopener noreferrer"
          className="nav-cta"
          style={{ display: typeof window !== 'undefined' && window.innerWidth < 720 ? 'none' : 'inline-flex' }}
        >
          Early Access
        </a>
      </div>

      {isOpen && (
        <div className="mobile-menu">
          {links.map(l => (
            <Link
              key={l.href}
              href={l.href}
              className="nav-link-mobile"
              onClick={() => setIsOpen(false)}
            >
              {l.label}
            </Link>
          ))}
          <a
            href="https://tally.so/r/ODDZvA"
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary"
            style={{ marginTop: 16 }}
            onClick={() => setIsOpen(false)}
          >
            Early Access
          </a>
        </div>
      )}
    </header>
  );
}
