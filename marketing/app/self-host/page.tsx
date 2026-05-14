import Link from 'next/link';

export const metadata = {
  title: 'Self-host | Memu',
  description: 'Run it on your cloud, your server, or a box in your house.',
};

export default function SelfHostPage() {
  return (
    <>
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '80px' }}>
        <div className="container">
          <h1 className="hero-title" style={{ marginBottom: 24 }}>
            Run it on your cloud, your server, or<br />
            <span className="gradient-text">a box in your house.</span>
          </h1>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p className="hero-subtitle">
              Memu doesn&rsquo;t require our infrastructure. It&rsquo;s designed to run where you decide.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 100, paddingBottom: 80 }}>
        <div className="container">
          <div className="grid-3">
            <div className="card">
              <h3 style={{ marginBottom: 16 }}>Our cloud</h3>
              <p style={{ marginBottom: 0 }}>
                The simplest start. Anonymised by the Digital Twin before anything reaches an external model, every exchange in your Privacy Ledger.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 16 }}>Your own server</h3>
              <p style={{ marginBottom: 0 }}>
                Run the whole thing on hardware you control. Your data never reaches us. The architecture is identical; the location is yours.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 16 }}>A box in your home</h3>
              <p style={{ marginBottom: 0 }}>
                The fullest form of ownership. Your context lives in your house. Memu has been running this way, daily, in its founder&rsquo;s home for months — this isn&rsquo;t a someday plan.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 80, paddingBottom: 100 }}>
        <div className="container text-center">
          <h2 className="section-title" style={{ marginBottom: 24 }}>Portability is the point</h2>
          <div style={{ maxWidth: '800px', margin: '0 auto 48px' }}>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
              Wherever it runs, your understanding belongs to you and travels with you. When a family member starts a new chapter, their context goes with the person it belongs to. The intelligence is the engine; you own the understanding it built.
            </p>
          </div>
          <div className="btn-group" style={{ justifyContent: 'center' }}>
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access
            </a>
            {/* The brief said link to technical docs if they exist. Leaving it out as none exist. */}
          </div>
        </div>
      </section>
    </>
  );
}
