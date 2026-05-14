import Link from 'next/link';

export const metadata = {
  title: 'Platform | Memu',
  description: 'One engine. As many worlds as your life has.',
};

export default function PlatformPage() {
  return (
    <>
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '80px' }}>
        <div className="container">
          <h1 className="hero-title" style={{ marginBottom: 24 }}>
            One engine.<br />
            <span className="gradient-text">As many worlds as your life has.</span>
          </h1>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p className="hero-subtitle">
              Most tools make you choose: an app for the family, another for work, another for the project. Each one a separate pile of your data, none of them aware they&rsquo;re all you.
            </p>
            <p className="hero-subtitle" style={{ marginTop: '1rem' }}>
              Memu is one engine you point at every part of your life. Each part is a collective — bounded, private, with its own memory and its own understanding. The intelligence is the same in all of them. The separation between them is absolute.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <h2 className="section-title text-center" style={{ marginBottom: 40 }}>What a collective is</h2>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
              A collective is a single, walled world. It holds its own people, its own routines, its own commitments, its own compiled understanding — and it cannot see, and is never mixed with, any of your others. The same real person can appear in two of your collectives and Memu treats them as unconnected, on purpose. That&rsquo;s not a limitation. That&rsquo;s the product.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <h2 className="section-title text-center" style={{ marginBottom: 56 }}>What you can point it at</h2>
          <div className="grid-2-cards">
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Your household</h3>
              <p style={{ marginBottom: 0 }}>
                Shared logistics, each member&rsquo;s private space, children with guardrails. The most proven form.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Your work</h3>
              <p style={{ marginBottom: 0 }}>
                What you&rsquo;re tracking, what you can&rsquo;t drop, the thinking you don&rsquo;t want sitting in a general chatbot under your name.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>A venture</h3>
              <p style={{ marginBottom: 0 }}>
                A company you&rsquo;re building, with its own projects inside it.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>A research project</h3>
              <p style={{ marginBottom: 0 }}>
                Fieldwork, interviews, analysis, with participant identities protected by architecture, not by promise.
              </p>
            </div>
          </div>
          <div style={{ maxWidth: '800px', margin: '48px auto 0', textAlign: 'center' }}>
            <p style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)', fontStyle: 'italic' }}>
              A collective isn&rsquo;t a folder. A folder nests files. A collective bounds memory, identity, and understanding — and keeps them from ever touching your other worlds.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 100 }}>
        <div className="container text-center">
          <h2 className="section-title" style={{ marginBottom: 40 }}>And you, across all of them</h2>
          <div style={{ maxWidth: '800px', margin: '0 auto 48px' }}>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              You own every collective, so you — and only you — can ask Memu to look across them. Your true whole-life view, assembled the moment you ask, shown to you, never merged into a permanent pile and never visible to anyone else.
            </p>
            <p style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)' }}>
              One engine. Many worlds. One owner who sees the whole.
            </p>
          </div>
          <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
            Get Early Access
          </a>
        </div>
      </section>
    </>
  );
}
