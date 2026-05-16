import Link from 'next/link';
import {
  MarkLens,
  MarkWalls,
  MarkEngine,
  MarkThread,
  MarkPrivacy,
  MarkReceipts,
  MarkFamily,
  MarkSovereign,
  MarkGarden,
} from '@/components/Marks';

export const metadata = {
  title: 'Memu — Intelligence without surveillance',
  description: 'One private mind across every part of your life — and each part stays its own world. The whole picture, without the pile.',
};

const TABLE_ROWS: [string, string, string][] = [
  ['Sees your real identity', "Yes — that's how it works", 'No — never, by design'],
  ['Holds your whole life', 'In one merged profile, on their servers', 'As separate worlds, on hardware you choose'],
  ['The cross-life view', 'Their merge, permanent, theirs to keep', 'Your lens, on demand, yours alone'],
  ['Compounds over time', 'Within its limits', 'Every interaction, and it stays yours'],
  ['Keeps your contexts unmixed', 'No — one pile is the point', 'Yes — the walls are the point'],
  ['Acts on your behalf', 'Increasingly', 'Yes — and shows you everything it did'],
];

export default function Home() {
  return (
    <>
      {/* ─── Hero ─── */}
      <section className="hero">
        <div className="hero-glow" aria-hidden />
        <div className="container" style={{ position: 'relative' }}>
          <span className="badge">
            <span className="badge-dot pulse-dot" />
            Private Beta
          </span>
          <h1 className="hero-title">
            Your private<br />
            <em>chief of staff</em>.
          </h1>
          <p className="hero-subtitle">
            One private mind across every part of your life — and each part stays its own world.
          </p>
          <div className="btn-group">
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access →
            </a>
            <Link href="/how" className="btn btn-secondary">
              See how it works
            </Link>
          </div>
          <p className="prose-serif" style={{ fontSize: 15, fontStyle: 'italic', marginTop: 36, color: 'var(--text-3)', maxWidth: 560 }}>
            Memu (మేము) means <em className="dim" style={{ color: 'var(--text-2)', fontWeight: 500 }}>&ldquo;we&rdquo;</em> in Telugu.
            Built by a parent who got tired of being his family&rsquo;s middleware — and realised the problem was bigger than one family.
          </p>

          <div className="hero-mark">
            <MarkLens size={220} color="var(--brand)" />
          </div>
        </div>
      </section>

      {/* ─── The problem ─── */}
      <section className="section section-tint">
        <div className="container-narrow">
          <div className="eyebrow">The problem</div>
          <p className="prose-serif">
            Every big assistant is racing to the same place: <strong>remember everything, anticipate, act on your behalf.</strong> It&rsquo;s genuinely useful. But there&rsquo;s a catch nobody says out loud.
          </p>
          <p className="prose-serif">
            To do it, they pile your entire life into one context, under one account, on their servers. Your work and your family and your private worries — one undifferentiated profile, <strong>theirs to hold, theirs to learn from, theirs to lose.</strong>
          </p>
          <p className="prose-serif">
            You feel the cost of this without naming it. It&rsquo;s why you&rsquo;d never put a confidential work thought in the same thread as your kid&rsquo;s schedule. Why a researcher can&rsquo;t paste interview notes into a chatbot. Why something in you hesitates before handing over the complete, annotated map of your family&rsquo;s life.
          </p>
          <div className="pull-quote">
            That hesitation is correct.<br />
            Memu is built around it.
          </div>
        </div>
      </section>

      {/* ─── A different shape — 3 cards ─── */}
      <section className="section">
        <div className="container">
          <div style={{ marginBottom: 56, maxWidth: 640 }}>
            <div className="eyebrow">A different shape</div>
            <h2 className="section-title">
              Your life isn&rsquo;t<br />one pile.
            </h2>
            <p className="section-lede">
              It&rsquo;s separate worlds. Memu treats them that way — and gives you a lens to see across.
            </p>
          </div>

          <div className="grid-3">
            <div className="card">
              <div className="card-mark"><MarkWalls size={64} color="var(--brand)" /></div>
              <h3 className="card-title">Separate worlds.</h3>
              <p className="card-body">
                Each collective — household, work, a venture, a research project — has its own memory and its own boundary. They can&rsquo;t bleed into each other. The separation is built into the architecture, not promised in a policy.
              </p>
            </div>
            <div className="card">
              <div className="card-mark"><MarkEngine size={64} color="var(--brand)" /></div>
              <h3 className="card-title">One engine, pointed wherever you need it.</h3>
              <p className="card-body">
                The same intelligence runs in every collective. Point it at family logistics, fieldwork, or quarterly portfolio. You&rsquo;re not buying four apps — you&rsquo;re getting one mind that adapts to each part of your life, and keeps each part to itself.
              </p>
            </div>
            <div className="card">
              <div className="card-mark"><MarkThread size={64} color="var(--brand)" /></div>
              <h3 className="card-title">You are the thread.</h3>
              <p className="card-body">
                You can look across all your collectives, because you own all of them. Ask &ldquo;what does my week actually look like&rdquo; and Memu assembles the answer. A lens you pick up — never a pile someone else keeps.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Privacy split ─── */}
      <section className="section section-tint">
        <div className="container">
          <div className="grid-2" style={{ alignItems: 'center', gap: 60 }}>
            <div>
              <div className="eyebrow">How it stays private</div>
              <h2 className="section-title">
                Show your work.<br />Don&rsquo;t show <em>yours</em>.
              </h2>
              <p className="prose-serif" style={{ fontSize: '1.125rem' }}>
                Before anything reaches an external AI, Memu replaces your names, your family, your places, your specifics with anonymous labels. The AI reasons brilliantly over the structure of your life. <strong>It never learns whose life it is.</strong>
              </p>
              <p className="prose-serif" style={{ fontSize: '1.125rem' }}>
                And you don&rsquo;t have to take that on faith. The <strong>Privacy Ledger</strong> shows you exactly what was sent — every query, every time. Most products ask you to trust them. Memu shows you the receipts.
              </p>
            </div>
            <div style={{ padding: 32, background: 'var(--surface)', borderRadius: 'var(--radius-xl)', border: '1px solid var(--border)', boxShadow: 'var(--shadow-card)', position: 'relative' }}>
              <div style={{ position: 'relative', width: '100%', minHeight: 240, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div style={{ position: 'absolute', top: 0, left: 0 }}><MarkPrivacy size={140} color="var(--brand)" /></div>
                <div style={{ position: 'absolute', bottom: 0, right: 0 }}><MarkReceipts size={120} color="var(--brand)" /></div>
                <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle at center, var(--brand-glow), transparent 70%)', pointerEvents: 'none' }} />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Family & Sovereignty — 2 cards ─── */}
      <section className="section">
        <div className="container">
          <div style={{ marginBottom: 56, maxWidth: 640 }}>
            <div className="eyebrow">Family · Sovereignty</div>
            <h2 className="section-title">
              Started at home.<br />Belongs to <em>you</em>.
            </h2>
          </div>

          <div className="grid-2">
            <div className="card" style={{ padding: '44px 40px' }}>
              <div className="card-mark"><MarkFamily size={72} color="var(--brand)" /></div>
              <h3 className="card-title" style={{ fontSize: '1.875rem' }}>
                Family is where it started — not where it stops.
              </h3>
              <p className="card-body">
                Memu began as a household chief of staff. Shared logistics that stop living in one parent&rsquo;s head. Each family member with their own private space. Children with age-appropriate guardrails. The family layer building naturally from individuals rather than imposed on them.
              </p>
              <p className="card-body">
                But the architecture that makes a family work is the same that makes a founder work. Or a researcher. Or anyone running more than one world at once.
              </p>
            </div>
            <div className="card" style={{ padding: '44px 40px' }}>
              <div className="card-mark"><MarkSovereign size={72} color="var(--brand)" /></div>
              <h3 className="card-title" style={{ fontSize: '1.875rem' }}>
                Your data. Your hardware. Your call.
              </h3>
              <p className="card-body">
                Run Memu in our cloud, on your own server, or on a box in your home. Your data doesn&rsquo;t touch our servers unless you choose that.
              </p>
              <p className="card-body">
                And it&rsquo;s yours to take. When you leave, when someone in your family starts a new chapter, the context travels with the person it belongs to. The AI stays behind. The understanding goes with you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ─── Comparison ─── */}
      <section className="section section-tint">
        <div className="container">
          <div style={{ marginBottom: 48, maxWidth: 720 }}>
            <div className="eyebrow">The difference</div>
            <h2 className="section-title">
              Not a chatbot.<br />Not a folder.
            </h2>
            <p className="section-lede">
              A chief of staff that anticipates, never acts behind your back, and never owns your context.
            </p>
          </div>

          <div className="comparison-table-wrap">
            <table className="comparison-table">
              <thead>
                <tr>
                  <th></th>
                  <th>A general AI assistant</th>
                  <th className="memu-col">Memu</th>
                </tr>
              </thead>
              <tbody>
                {TABLE_ROWS.map(([f, o, m]) => (
                  <tr key={f}>
                    <td className="row-label">{f}</td>
                    <td>{o}</td>
                    <td className="memu-col">{m}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ─── Final CTA ─── */}
      <section className="section text-center" style={{ background: 'var(--surface)', borderTop: '1px solid var(--border-soft)', borderBottom: '1px solid var(--border-soft)' }}>
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 32 }}>
            <MarkGarden size={88} color="var(--brand)" />
          </div>
          <h2 className="section-title" style={{ fontSize: 'clamp(2.5rem, 6vw, 4rem)', margin: '0 auto 18px', maxWidth: 720 }}>
            The whole picture.<br />Without the <em>pile</em>.
          </h2>
          <p className="section-lede" style={{ margin: '0 auto 36px' }}>
            A private chief of staff that earns trust by showing its work — every query, every action, every time.
          </p>
          <div className="btn-group" style={{ justifyContent: 'center' }}>
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access →
            </a>
            <Link href="/platform" className="btn btn-secondary">
              See the platform
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
