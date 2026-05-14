import Link from 'next/link';

export const metadata = {
  title: 'Privacy | Memu',
  description: 'Privacy isn\'t a feature here. It\'s the shape of the thing.',
};

export default function PrivacyPage() {
  return (
    <>
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '80px' }}>
        <div className="container">
          <h1 className="hero-title" style={{ marginBottom: 24 }}>
            Privacy isn&rsquo;t a feature here.<br />
            <span className="gradient-text">It&rsquo;s the shape of the thing.</span>
          </h1>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p className="hero-subtitle">
              Most products bolt privacy on: a setting, a policy, a promise. Memu is built the other way round — the privacy is the architecture, and the architecture is what makes the product good.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="grid-2-cards">
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>The AI never knows who you are</h3>
              <p style={{ marginBottom: 0 }}>
                The Digital Twin replaces every identifying detail before anything reaches an external model. Not encrypted-so-we-could-decrypt-it. Anonymised, so there&rsquo;s nothing to decrypt. The intelligence works on the structure of your life, never the identity behind it.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Your worlds can&rsquo;t be correlated — even by us</h3>
              <p style={{ marginBottom: 0 }}>
                Each workspace has its own separate identity map. The same real person is a different anonymous label in your household and in your work. There is no master key that joins them. We couldn&rsquo;t build the complete picture of you if we wanted to — and not wanting to isn&rsquo;t good enough, so we made it impossible.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>You hold the only lens that sees across</h3>
              <p style={{ marginBottom: 0 }}>
                You can look across your own workspaces, because you own them. Nothing and no one else can — not another user, not an external AI, not Memu itself acting on its own. The whole-life view exists for exactly one person: you.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>You can verify all of it</h3>
              <p style={{ marginBottom: 0 }}>
                The Privacy Ledger shows you what was sent, every time. This isn&rsquo;t a trust exercise. It&rsquo;s an audit you can run yourself.
              </p>
            </div>
          </div>
          
          <div className="card" style={{ maxWidth: '800px', margin: '40px auto 0', textAlign: 'center', background: 'transparent', border: '1px solid var(--border)', padding: '40px' }}>
             <h3 style={{ marginBottom: 12 }}>And you can leave with everything</h3>
             <p style={{ marginBottom: 0, fontSize: '1.1rem' }}>
                Your understanding is yours. Export it, move it, take it to a new chapter of life. The AI stays behind; what it understood about you travels with you.
             </p>
          </div>
          
          <div className="text-center" style={{ marginTop: 64 }}>
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
