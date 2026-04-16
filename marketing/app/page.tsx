import Link from 'next/link';

export default function Home() {
  return (
    <>
      <section className="section text-center" style={{ paddingTop: '120px' }}>
        <div className="container">
          <span className="badge">Private Beta</span>
          <h1 className="hero-title">Your family.<br/>Your network.<br/><span className="gradient-text">Your data.</span></h1>
          <p className="hero-subtitle">
            Memu means "we". Build a compounding sanctuary of knowledge where you are the atom, and the family is the emergent layer.
          </p>
          <div className="btn-group">
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Request Early Access
            </a>
            <Link href="/what" className="btn btn-secondary">
              See how it works
            </Link>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--surface-low)' }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: '64px' }}>
            <h2 className="section-title">One brain. Everywhere you need it.</h2>
            <p className="section-subtitle" style={{ margin: '0 auto' }}>
              Memu is your family's Chief of Staff. It coordinates logistics, anticipates conflicts, and remembers the details so you don't have to.
            </p>
          </div>
          
          <div className="grid-3">
            <div className="card">
              <h3>The Memu App</h3>
              <p>Your ultimate control center. View your Privacy Ledger, manage your Spaces, and ensure your sovereign boundaries are respected.</p>
            </div>
            <div className="card">
              <h3>WhatsApp Gateway</h3>
              <p>Frictionless coordination on the go. Text Memu just like any other contact. Zero new apps required for the family to get started.</p>
            </div>
            <div className="card">
              <h3>Home Dashboard</h3>
              <p>The "Skylight effect". A physical, ambient touchscreen for the kitchen counter that visualises logistics and photo memories.</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
