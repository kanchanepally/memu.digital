export const metadata = {
  title: "Why Memu is different — Privacy is architecture, not policy",
  description: "We don't ask you to trust our word. We show you. The Privacy Ledger shows every query, every anonymisation, every response.",
};

export default function WhyDifferent() {
  return (
    <div className="container-wide section">
      <h1 className="hero-title">Why it&rsquo;s different</h1>
      <p className="section-subtitle">
        We don&rsquo;t ask you to trust our word. We show you.
      </p>

      <div className="grid-4" style={{ marginTop: '64px' }}>
        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Structural Privacy</h3>
          <p>
            A policy says &ldquo;we won&rsquo;t look.&rdquo; Structural privacy says &ldquo;even if we want to,
            we can&rsquo;t.&rdquo; Before anything reaches the AI, your names, locations, and personal details
            are replaced with anonymous labels by the Digital Twin. The AI reasons brilliantly
            over your life — and mathematically cannot identify you. Even a breach at the API
            provider exposes nothing personal.
          </p>
        </div>

        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>The Privacy Ledger</h3>
          <p>
            Not because regulations require it — because you should never have to trust
            anyone&rsquo;s word about what happened to your data. Including ours. The Privacy
            Ledger shows every query, every anonymisation, every response. Exactly what the AI
            saw. Exactly what it didn&rsquo;t. Open it any time from the Memu app.
          </p>
        </div>

        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Child Safety by Design</h3>
          <p>
            Current AI oscillates between full restriction and dangerous blind access for children.
            Memu provides age-appropriate AI access with parental visibility through the Ledger.
            Children interact naturally. Parents see what the AI saw. No aggressive policing —
            transparency instead.
          </p>
        </div>

        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 3v18"/><path d="M3 10v7a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M12 3L3 10"/><path d="M12 3l9 7"/>
            </svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Equal Sovereignty</h3>
          <p>
            Every adult in the household has equal control over their own data. If the family
            changes, any member can leave with their data instantly. Unplug the Pod. Walk away.
            No permissions needed from anyone else.
          </p>
        </div>
      </div>
    </div>
  );
}
