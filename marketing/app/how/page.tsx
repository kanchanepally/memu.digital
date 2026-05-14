import Link from 'next/link';
import { TwinDemo } from '@/components/TwinDemo';

export const metadata = {
  title: 'How it works | Memu',
  description: 'See exactly what the AI sees. And what it doesn\'t.',
};

export default function HowPage() {
  return (
    <>
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '60px' }}>
        <div className="container">
          <h1 className="hero-title" style={{ marginBottom: 24 }}>
            See exactly what the AI sees.<br />
            <span className="gradient-text">And what it doesn&rsquo;t.</span>
          </h1>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p className="hero-subtitle">
              Memu&rsquo;s intelligence runs on external AI models — but those models never learn whose life they&rsquo;re reasoning about.
            </p>
          </div>
        </div>
      </section>

      {/* ── TwinDemo section ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 40, maxWidth: '800px', margin: '0 auto 56px' }}>
            <h2 className="section-title">The Digital Twin</h2>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem', textAlign: 'left' }}>
              Before anything leaves Memu, a layer called the Digital Twin replaces every identifying detail — names, family members, places, specifics — with stable anonymous labels. &ldquo;Does Jamie&rsquo;s swimming on Thursday clash with my dentist?&rdquo; becomes a question about [Child-1] and [Appointment-2]. The AI reasons over the shape of the problem. It never sees the people.
            </p>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, textAlign: 'left' }}>
              When the answer comes back, the Twin translates the labels back to the real thing — for your eyes only.
            </p>
          </div>
          
          <TwinDemo />
        </div>
      </section>

      {/* ── Details ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="grid-3">
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>The Privacy Ledger</h3>
              <p style={{ marginBottom: 0 }}>
                Every one of those exchanges is logged where you can see it. Every query. Every response. Exactly what was sent, exactly what wasn&rsquo;t. Other products ask for your trust. Memu hands you the evidence and lets you check.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>It compiles, it doesn&rsquo;t just retrieve</h3>
              <p style={{ marginBottom: 0 }}>
                Memu doesn&rsquo;t keep a pile of your messages and search it when you ask. It actively compiles what it learns into living pages of understanding — one for each person, routine, project, and commitment that matters — and keeps them current as your life moves. Ask a question and it&rsquo;s drawing on understanding it has already built, not guessing from fragments.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>It&rsquo;s proactive — never unsupervised</h3>
              <p style={{ marginBottom: 0 }}>
                Memu surfaces what&rsquo;s slipping, drafts what you need, plans from what it knows. Then it brings it to you. Everything it does, it shows you. A Chief of Staff anticipates; it doesn&rsquo;t act behind your back.
              </p>
            </div>
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
