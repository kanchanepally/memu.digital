import { Logo } from './Logo';

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-brand">
        <Logo size={20} showRing={false} />
        <span className="footer-brand-text">memu</span>
      </div>
      <div>Private intelligence · Solid-compliant · Open architecture</div>
      <div className="footer-telugu">మేము — &ldquo;we&rdquo; in Telugu</div>
    </footer>
  );
}
