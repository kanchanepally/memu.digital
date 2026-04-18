import Link from 'next/link';

export default function ArchitectureTiers() {
  return (
    <div className="container section">
      <div className="text-center" style={{ marginBottom: '80px' }}>
        <h1 className="hero-title">Three Deployment Tiers</h1>
        <p className="hero-subtitle">
          Memu scales from frictionless cloud access to absolute physical data sovereignty. Choose the deployment model that fits your family's privacy baseline.
        </p>
      </div>

      <div className="grid-3" style={{ marginBottom: '80px' }}>
        {/* Tier 1 */}
        <div className="card-ai">
          <div className="card-ai-icon" style={{ background: 'var(--surface)', color: 'var(--text-main)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 12A10 10 0 0 0 12 2v10z"></path><path d="M12 22A10 10 0 1 1 22 12h-10z"></path></svg>
          </div>
          <h3 style={{ marginBottom: '8px' }}>Tier 1: Cloud Native</h3>
          <div style={{ color: 'var(--primary)', fontWeight: 'bold', marginBottom: '16px', fontSize: '0.9rem', textTransform: 'uppercase' }}>Frictionless Access</div>
          <p>
            Hosted entirely by Memu. You connect your family WhatsApp group, and the AI acts as your Chief of Staff immediately. 
          </p>
          <ul style={{ fontSize: '1rem' }}>
            <li>Zero hardware to buy or maintain</li>
            <li>Guaranteed 'Anonymous Twin' proxy layer</li>
            <li>Cloud APIs (Gemini/Claude) powered</li>
          </ul>
        </div>

        {/* Tier 2 */}
        <div className="card-ai" style={{ border: '2px solid var(--primary)', transform: 'translateY(-8px)', boxShadow: '0 24px 48px rgba(102, 126, 234, 0.15)' }}>
          <div className="card-ai-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
          </div>
          <h3 style={{ marginBottom: '8px' }}>Tier 2: Hybrid Sovereign</h3>
          <div style={{ color: 'var(--primary)', fontWeight: 'bold', marginBottom: '16px', fontSize: '0.9rem', textTransform: 'uppercase' }}>The Sweet Spot</div>
          <p>
            Your context, your hardware. You run the Memu Database and Photo backups (Immich) on an Intel N100 in your living room.
          </p>
          <ul style={{ fontSize: '1rem' }}>
            <li>Database lives physically in your house</li>
            <li>Physical LUKS USB Pod Modularity supported</li>
            <li>Uses Cloud APIs precisely, only after Twin anonymization</li>
          </ul>
        </div>

        {/* Tier 3 */}
        <div className="card-ai">
          <div className="card-ai-icon" style={{ background: '#1E1E1E' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
          </div>
          <h3 style={{ marginBottom: '8px' }}>Tier 3: Absolute Airgap</h3>
          <div style={{ color: 'var(--primary)', fontWeight: 'bold', marginBottom: '16px', fontSize: '0.9rem', textTransform: 'uppercase' }}>Total Paranoia</div>
          <p>
            Everything runs locally. You don't trust Meta, so you use Matrix. You don't trust Cloud LLMs, so you perform inference locally.
          </p>
          <ul style={{ fontSize: '1rem' }}>
            <li>Matrix Synapse local communication</li>
            <li>Ollama (`llama3`) strictly local intelligence</li>
            <li>Absolute unyielding data sovereignty</li>
          </ul>
        </div>
      </div>

      <div className="text-center">
        <Link href="/explore" className="btn btn-primary" style={{ marginRight: '16px' }}>See Features</Link>
        <Link href="/how" className="btn btn-secondary">How the AI Context works</Link>
      </div>
    </div>
  );
}
