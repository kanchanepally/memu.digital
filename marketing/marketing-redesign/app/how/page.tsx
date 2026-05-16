import Link from 'next/link';
import { MarkLens, MarkReceipts, MarkSpace, MarkEngine } from '@/components/Marks';

export const metadata = {
  title: 'How it works | Memu',
  description: "See exactly what the AI sees. And what it doesn't.",
};

export default function HowPage() {
  return (
    <>
      {/* Hero */}
      <section className="hero">
        <div className="hero-glow" aria-hidden />
        <div className="container" style={{ position: 'relative' }}>
          <div className="eyebrow">How it works</div>
          <h1 className="hero-title">
            See exactly what the AI sees.<br />
            <em>And what it doesn&rsquo;t.</em>
          </h1>
          <p className="hero-subtitle">
            Memu&rsquo;s intelligence runs on external AI models — but those models never learn whose life they&rsquo;re reasoning about.
          </p>
          <div className="hero-mark">
            <MarkLens size={220} color="var(--brand)" />
          </div>
        </div>
      </section>

      {/* Digital Twin */}
      <section className="section section-tint">
        <div className="container">
          <div className="grid-2" style={{ gap: 60, alignItems: 'center' }}>
            <div>
              <div className="eyebrow">The Digital Twin</div>
              <h2 className="section-title">
                Anonymised before<br />anything <em>leaves</em>.
              </h2>
              <p className="prose-serif" style={{ fontSize: '1.1875rem' }}>
                Before anything leaves Memu, a layer called the <strong>Digital Twin</strong> replaces every identifying detail — names, family members, places, specifics — with stable anonymous labels.
              </p>
              <p className="prose-serif" style={{ fontSize: '1.1875rem' }}>
                &ldquo;Does Jamie&rsquo;s swimming on Thursday clash with my dentist?&rdquo; becomes a question about{' '}
                <span className="mono" style={{ padding: '1px 7px', borderRadius: 4, background: 'var(--brand-soft)', color: 'var(--brand)', fontSize: '0.9em' }}>[Child-1]</span> and{' '}
                <span className="mono" style={{ padding: '1px 7px', borderRadius: 4, background: 'var(--brand-soft)', color: 'var(--brand)', fontSize: '0.9em' }}>[Appointment-2]</span>. The AI reasons over the shape of the problem.
              </p>
            </div>
            <div style={{ padding: 40, background: 'var(--surface)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-card)' }}>
              <div className="eyebrow" style={{ marginBottom: 12 }}>Your query</div>
              <div style={{ padding: '14px 16px', background: 'var(--bg)', borderRadius: 10, fontSize: 15, color: 'var(--text)', lineHeight: 1.5, marginBottom: 18, border: '1px solid var(--border-soft)' }}>
                Does Jamie&rsquo;s swimming on Thursday clash with my dentist appointment?
              </div>
              <div className="mono" style={{ marginBottom: 18, color: 'var(--text-3)', fontSize: 12, display: 'flex', alignItems: 'center', gap: 10 }}>
                <svg width={14} height={14} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.8} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
                Anonymised
              </div>
              <div className="eyebrow" style={{ marginBottom: 12 }}>What the AI sees</div>
              <div className="mono" style={{ padding: '14px 16px', background: 'var(--brand-soft)', borderRadius: 10, fontSize: 14, color: 'var(--brand)', lineHeight: 1.6, border: '1px solid rgba(80,84,181,0.2)' }}>
                Does <span className="token-chip">[Child-1]</span>&rsquo;s <span className="token-chip">[Activity-3]</span> on <span className="token-chip">[Day-Th]</span> clash with <span className="token-chip">[Appointment-2]</span>?
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Three things */}
      <section className="section">
        <div className="container">
          <div className="eyebrow">Three things to know</div>
          <h2 className="section-title">
            Not just remembering.<br /><em>Working</em>.
          </h2>
          <div className="grid-3" style={{ marginTop: 56 }}>
            <div className="card">
              <div className="card-mark"><MarkReceipts size={56} color="var(--brand)" /></div>
              <h3 className="card-title">The Privacy Ledger</h3>
              <p className="card-body">
                Every exchange is logged where you can see it. Every query, every response, exactly what was sent. Other products ask for trust. Memu hands you the receipts.
              </p>
            </div>
            <div className="card">
              <div className="card-mark"><MarkSpace size={56} color="var(--brand)" /></div>
              <h3 className="card-title">It compiles — doesn&rsquo;t retrieve.</h3>
              <p className="card-body">
                Memu doesn&rsquo;t keep a pile of your messages and search it. It compiles living pages of understanding — one per person, routine, project — and keeps them current as your life moves.
              </p>
            </div>
            <div className="card">
              <div className="card-mark"><MarkEngine size={56} color="var(--brand)" /></div>
              <h3 className="card-title">Proactive — never unsupervised.</h3>
              <p className="card-body">
                It surfaces what&rsquo;s slipping, drafts what you need, plans from what it knows. Everything it does, it shows you. A chief of staff anticipates; it doesn&rsquo;t act behind your back.
              </p>
            </div>
          </div>
          <div className="text-center" style={{ marginTop: 64 }}>
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access →
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
