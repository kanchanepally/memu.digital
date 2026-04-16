import Link from 'next/link';
import { Logo } from './Logo';

export const Masthead = () => {
  return (
    <header className="masthead">
      <div className="container masthead-inner">
        <Link href="/">
          <Logo scale={0.3} />
        </Link>
        <nav className="nav-links">
          <Link href="/explore" className="nav-link">Features</Link>
          <Link href="/what" className="nav-link">What it is</Link>
          <Link href="/how" className="nav-link">How it works</Link>
          <Link href="/why" className="nav-link">Why it's different</Link>
        </nav>
        <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="nav-btn">
          Early Access
        </a>
      </div>
    </header>
  );
};
