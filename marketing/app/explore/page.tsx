export default function ExploreFeatures() {
  return (
    <div className="container section">
      <div className="text-center" style={{ marginBottom: '80px' }}>
        <h1 className="hero-title">Explore Memu</h1>
        <p className="hero-subtitle">
          All your family's plans, tasks, memories, and routines — organized by AI, running on your hardware. Everything Nori, Cozi, or FamilyWall can do, but with zero data harvesting.
        </p>
      </div>

      <div style={{ marginBottom: '80px' }}>
        <h2 className="section-title">The Table Stakes. Done Better.</h2>
        <div className="grid-3">
          <div className="card">
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>Smart Shopping Lists</h3>
            <p>
              Just say "We're out of milk and pasta" in the family WhatsApp. Memu categorizes it, adds it to the shared list, and reminds you when you're near the shops. Use `/showlist` or check the Dashboard to see it anytime.
            </p>
          </div>
          <div className="card">
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>Calendar & Logistics</h3>
            <p>
              Seamless syncing across family schedules. Memu doesn't just display events; it anticipates conflicts. "Heads up, Alice's swimming at 4pm clashes with Bob's dentist appointment."
            </p>
          </div>
          <div className="card">
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>Cross-Channel Access</h3>
            <p>
              Don't force your family to download another app. Memu lives where you already are: WhatsApp today, with Matrix, SMS and Email coming soon. Text Memu just like you'd text a partner.
            </p>
          </div>
        </div>
      </div>

      <div style={{ marginBottom: '80px' }}>
        <h2 className="section-title">Beyond Basic Organizers</h2>
        <div className="grid-2-cards">
          <div className="card-ai">
            <div className="card-ai-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            </div>
            <h3 style={{ marginBottom: '16px' }}>Cross-Silo Context</h3>
            <p>
              "What photos do we have from Dad's birthday?" Memu merges 4 data silos in parallel: family group chats, shared calendars, school emails, and photo metadata — giving the AI a complete picture of your real world.
            </p>
          </div>
          <div className="card-ai">
            <div className="card-ai-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
            </div>
            <h3 style={{ marginBottom: '16px' }}>Automatic "Spaces" Creation</h3>
            <p>
              Instead of fragile "search and guess" across old messages, the AI actively translates your casual WhatsApp chats into durable Markdown profiles. It automatically creates highly accurate pages for family members, travel plans, and routines that get richer over time.
            </p>
          </div>
          <div className="card-ai">
            <div className="card-ai-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            </div>
            <h3 style={{ marginBottom: '16px' }}>The Reflection Loop</h3>
            <p>
              Memu actively sweeps for inconsistencies. "Wait, Alice has ballet on Tuesdays now, but her old routine says swimming." It flags these contradictions and unaddressed commitments directly to your morning group chat.
            </p>
          </div>
          <div className="card-ai">
            <div className="card-ai-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>
            </div>
            <h3 style={{ marginBottom: '16px' }}>The Privacy Ledger</h3>
            <p>
              Total transparency. Open the Memu Mobile App to verify exactly what anonymous strings were sent to the cloud. You don't have to trust our privacy policy; you can audit the cryptographically guaranteed ledger yourself.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
