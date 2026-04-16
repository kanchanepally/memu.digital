export default function WhyDifferent() {
  return (
    <div className="container section">
      <h1 className="hero-title">Why it's different</h1>
      <p className="section-subtitle">
        Privacy is a promise. Sovereignty is an architecture. 
      </p>

      <div className="grid-3" style={{ marginTop: '64px' }}>
        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Structural Privacy</h3>
          <p>
            A policy says "we won't look." Structural privacy says "even if we want to, we can't." Your data stays on your device, and the external AI only sees the anonymized Digital Twin. Even if a data breach occurs at the API provider, your personal details are computationally absent.
          </p>
        </div>
        
        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Show Your Work</h3>
          <p>
            We don't just say we anonymize it. We prove it. Inside the Memu Mobile App, you can open the <strong>Privacy Ledger</strong> at any time. It shows you the exact prompt, exactly as Claude saw it, proving exactly what didn't leave your house.
          </p>
        </div>

        <div className="card">
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          </div>
          <h3 style={{ color: 'var(--primary)', marginBottom: '16px' }}>Child Safety by Design</h3>
          <p>
            Current AI solutions oscillate between full restriction or dangerous blind access for children. Memu provides age-appropriate AI access while giving parents transparent context via the Ledger. It’s digital parenting through visibility, not aggressive policing.
          </p>
        </div>
      </div>
    </div>
  );
}
