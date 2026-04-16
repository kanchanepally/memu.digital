export default function WhatIsMemu() {
  return (
    <div className="container section">
      <h1 className="hero-title">What is Memu?</h1>
      <p className="section-subtitle">
        We are building Family Intelligence Infrastructure. Not a chatbot, not a shared calendar—a proactive operating layer for your family's life.
      </p>

      <div className="grid-2-cards">
        <div className="card-ai">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle><line x1="21.17" y1="8" x2="12" y2="8"></line><line x1="3.95" y1="6.06" x2="8.54" y2="14"></line><line x1="10.88" y1="21.94" x2="15.46" y2="14"></line></svg>
          </div>
          <h2 style={{ marginBottom: '16px' }}>The Individual Atom</h2>
          <p>
            Every system starts with the individual. Inspired by Tim Berners-Lee's <strong>Solid Pod</strong> philosophy, Memu treats your personal data as a sovereign vault. You control your data; you choose what to expose.
          </p>
        </div>
        
        <div className="card-ai">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </div>
          <h2 style={{ marginBottom: '16px' }}>The Emergent Family</h2>
          <p>
            Family emerges when sovereign individuals connect. As you grant access to shared context—like calendars, routines, and chats—the family layer coordinates scheduling and resolves conflicts seamlessly across the household.
          </p>
        </div>

        <div className="card-ai" style={{ gridColumn: '1 / -1' }}>
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
          </div>
          <h2 style={{ marginBottom: '16px', color: 'var(--primary)' }}>Compounding Knowledge (LLM Wiki)</h2>
          <p>
            Memu builds a persistent, compounding knowledge graph modeled after the <strong>LLM Wiki</strong> concept. Instead of doing fragile search-and-guess (RAG) on every question, the AI actively compiles its understanding of you and your family into structured, human-readable markdown files called "Spaces". 
          </p>
          <p style={{ marginBottom: 0 }}>
            With every interaction, these Spaces evolve. It doesn't forget. Your Chief of Staff gets richer and smarter with every passing day, seamlessly tracking context over years without degrading.
          </p>
        </div>
      </div>
    </div>
  );
}
