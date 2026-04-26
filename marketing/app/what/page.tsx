export const metadata = {
  title: 'What is Memu? — Not a chatbot. Not a task app.',
  description: 'Memu is privacy-first agentic intelligence that compounds. Individual-first, family-emergent. The only product that combines genuine agency, genuine privacy, and genuine compounding intelligence.',
};

export default function WhatIsMemu() {
  return (
    <div className="container section">
      <h1 className="hero-title">Not a chatbot.<br /><span className="gradient-text">Not a task app.</span></h1>
      <p className="section-subtitle">
        Privacy-first agentic intelligence that compounds. Individual-first, family as the emergent layer.
      </p>

      <div className="grid-2-cards" style={{ marginBottom: 48 }}>
        <div className="card-ai">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/>
              <line x1="21.17" y1="8" x2="12" y2="8"/>
              <line x1="3.95" y1="6.06" x2="8.54" y2="14"/>
              <line x1="10.88" y1="21.94" x2="15.46" y2="14"/>
            </svg>
          </div>
          <h2 style={{ marginBottom: 16 }}>The Individual Atom</h2>
          <p>
            Memu starts with you — one person, one private context. Inspired by Tim Berners-Lee&rsquo;s
            Solid Pod philosophy, your data is a sovereign vault. You control it. You choose what
            to share and with whom. The family layer only emerges when you choose to connect.
          </p>
        </div>

        <div className="card-ai">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h2 style={{ marginBottom: 16 }}>The Emergent Family</h2>
          <p>
            Family emerges when sovereign individuals connect — not the other way around. As you
            grant access to shared context, the family layer coordinates scheduling, resolves conflicts,
            and holds shared commitments. Each person retains full ownership of their private sphere.
          </p>
        </div>

        <div className="card-ai" style={{ gridColumn: '1 / -1' }}>
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
            </svg>
          </div>
          <h2 style={{ marginBottom: 16, color: 'var(--primary)' }}>Compiled Synthesis — Not Search</h2>
          <p>
            Memu doesn&rsquo;t do fragile search-and-guess (RAG) on every question. It actively
            compiles its understanding of your life into structured, human-readable pages called
            Spaces — one for each person, project, routine, and commitment that matters.
          </p>
          <p style={{ marginBottom: 0 }}>
            With every interaction, Spaces evolve. Memu notices when &ldquo;Jamie has ballet on Tuesdays&rdquo;
            and updates Jamie&rsquo;s Space — without being asked. Your Chief of Staff gets richer
            and smarter every day, without degrading over time.
          </p>
        </div>
      </div>

      <div style={{
        background: 'var(--surface-low)', borderRadius: 20,
        padding: '40px 48px', textAlign: 'center',
      }}>
        <h2 style={{ marginBottom: 12 }}>Three things no one else has simultaneously.</h2>
        <p style={{ maxWidth: 680, margin: '0 auto 0 auto', marginBottom: 0 }}>
          Genuine agency (tool use, proactive behaviour, channel integration) + genuine privacy
          (deterministic anonymisation, auditable ledger, data sovereignty) + genuine compounding
          intelligence (synthesis, reflection, Spaces that grow over time). No other product in
          the landscape has all three. OpenClaw has agency but no privacy. Family organisers have
          consumer UX but no agency. Generic LLMs have reasoning but nothing else.
          Memu is the only product that combines all three.
        </p>
      </div>
    </div>
  );
}
