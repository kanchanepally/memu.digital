"use client";

import Link from 'next/link';
import { useState } from 'react';
import { Logo } from './Logo';

export const Masthead = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <header className="masthead">
      <div className="container masthead-inner">
        <Link href="/" onClick={() => setIsOpen(false)}>
          <Logo scale={0.45} />
        </Link>
        
        {/* Desktop Navigation */}
        <nav className="nav-links">
          <Link href="/platform" className="nav-link">Platform</Link>
          <Link href="/how" className="nav-link">How it works</Link>
          <Link href="/privacy" className="nav-link">Privacy</Link>
          <Link href="/self-host" className="nav-link">Self-host</Link>
        </nav>
        
        {/* Mobile Hamburger Icon */}
        <button 
          className="mobile-menu-btn" 
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle Navigation"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {isOpen ? (
              <>
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </>
            ) : (
              <>
                <line x1="3" y1="12" x2="21" y2="12"></line>
                <line x1="3" y1="6" x2="21" y2="6"></line>
                <line x1="3" y1="18" x2="21" y2="18"></line>
              </>
            )}
          </svg>
        </button>

        <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="nav-btn desktop-only">
          Early Access
        </a>
      </div>

      {/* Mobile Dropdown */}
      {isOpen && (
        <div className="mobile-menu">
          <Link href="/platform" className="nav-link-mobile" onClick={() => setIsOpen(false)}>Platform</Link>
          <Link href="/how" className="nav-link-mobile" onClick={() => setIsOpen(false)}>How it works</Link>
          <Link href="/privacy" className="nav-link-mobile" onClick={() => setIsOpen(false)}>Privacy</Link>
          <Link href="/self-host" className="nav-link-mobile" onClick={() => setIsOpen(false)}>Self-host</Link>
          <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="nav-btn-mobile" onClick={() => setIsOpen(false)}>
            Early Access
          </a>
        </div>
      )}
    </header>
  );
};
