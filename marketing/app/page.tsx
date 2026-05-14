import Link from 'next/link';
import { HeroCycler } from '@/components/HeroCycler';
import { TwinDemo } from '@/components/TwinDemo';

export const metadata = {
  title: 'Memu — Intelligence without surveillance',
  description: 'One private mind across every part of your life — and each part stays its own world. The whole picture, without the pile.',
};

const TABLE_ROWS = [
  ['Sees your real identity', 'Yes — that\'s how it works', 'No — never, by design'],
  ['Holds your whole life', 'In one merged profile, on their servers', 'As separate worlds, on hardware you choose'],
  ['The cross-life view', 'Their merge, permanent, theirs to keep', 'Your lens, on demand, yours alone'],
  ['Compounds over time', 'Within its limits', 'Every interaction, and it stays yours'],
  ['Keeps your contexts unmixed', 'No — one pile is the point', 'Yes — the walls are the point'],
  ['Acts on your behalf', 'Increasingly', 'Yes — and shows you everything it did'],
];

export default function Home() {
  return (
    <>
      {/* ── Hero ── */}
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '80px' }}>
        <div className="container">
          <span className="badge">Private Beta</span>
          <h1 className="hero-title" style={{ marginBottom: 8 }}>
            Your Chief of Staff.
          </h1>
          <div style={{ fontSize: '1.5rem', fontWeight: 600, minHeight: '2.4rem', marginBottom: 16 }}>
            <HeroCycler />
          </div>
          <p className="hero-subtitle" style={{ marginTop: 8 }}>
            One private mind across every part of your life — and each part stays its own world. The whole picture, without the pile.
          </p>
          <div className="btn-group">
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access
            </a>
            <Link href="/how" className="btn btn-secondary">
              See how it works
            </Link>
          </div>
          <p style={{ marginTop: 32, color: 'var(--text-secondary)', fontSize: '0.95rem', fontWeight: 500 }}>
            Memu (మేము) means &ldquo;we&rdquo; in Telugu.{' '}
            Built by a parent who got tired of being his family&rsquo;s middleware — and realised the problem was bigger than one family.
          </p>
        </div>
      </section>

      {/* ── The Problem ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              Every big assistant is racing to the same place: remember everything, anticipate, act on your behalf. It&rsquo;s genuinely useful. But there&rsquo;s a catch nobody says out loud.
            </p>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              To do it, they pile your entire life into one context, under one account, on their servers. Your work and your family and your private worries — one undifferentiated profile, theirs to hold, theirs to learn from, theirs to lose.
            </p>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              You feel the cost of this without naming it. It&rsquo;s why you&rsquo;d never put a confidential work thought in the same thread as your kid&rsquo;s schedule. Why a researcher can&rsquo;t paste interview notes into a chatbot. Why something in you hesitates before handing over the complete, annotated map of your family&rsquo;s life.
            </p>
            <p style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)' }}>
              That hesitation is correct. Memu is built around it.
            </p>
          </div>
        </div>
      </section>

      {/* ── A different shape ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 56 }}>
            <h2 className="section-title">A different shape</h2>
          </div>
          <div className="grid-3">
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>Your life isn&rsquo;t one pile. It&rsquo;s separate worlds.</h3>
              <p style={{ marginBottom: 0 }}>
                Your household. Your work. A venture. A research project. Memu calls each one a collective — and keeps them genuinely separate. Each has its own memory, its own understanding, its own boundary. They don&rsquo;t bleed into each other. They can&rsquo;t — the separation is built into the architecture, not promised in a policy.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>One engine, pointed wherever you need it.</h3>
              <p style={{ marginBottom: 0 }}>
                The same intelligence runs in every collective. Point it at family logistics and it&rsquo;s a household Chief of Staff. Point it at a research project and it organises your fieldwork. Point it at your work and it tracks what you can&rsquo;t afford to drop. You&rsquo;re not buying four apps. You&rsquo;re getting one mind that adapts to each part of your life — and keeps each part to itself.
              </p>
            </div>
            <div className="card">
              <h3 style={{ marginBottom: 12 }}>You are the thread. So you get the whole picture.</h3>
              <p style={{ marginBottom: 0 }}>
                Here&rsquo;s what makes Memu a real Chief of Staff and not just a tidy set of folders: you can look across all your collectives, because you own all of them. Ask &ldquo;what does my week actually look like&rdquo; and Memu assembles the answer from every part of your life at once. That cross-life view is yours — invoked by you, shown to you, the moment you ask. It&rsquo;s a lens you pick up, never a pile someone else keeps.
              </p>
            </div>
          </div>
          <div style={{ maxWidth: '800px', margin: '48px auto 0', textAlign: 'center' }}>
             <p style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)', fontStyle: 'italic' }}>
               The big assistants give you the whole picture by merging everything, permanently, on their side. Memu gives you the whole picture by letting you — and only you — see across walls that stay standing.
             </p>
          </div>
        </div>
      </section>

      {/* ── How it stays private ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 40 }}>
        <div className="container">
           <div className="text-center" style={{ marginBottom: 40, maxWidth: '800px', margin: '0 auto 40px' }}>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              Before anything reaches an external AI, Memu replaces your names, your family, your places, your specifics with anonymous labels. The AI reasons brilliantly over the structure of your life. It never learns whose life it is.
            </p>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6 }}>
              And you don&rsquo;t have to take that on faith. The Privacy Ledger shows you exactly what was sent — every query, every time. Most products ask you to trust them. Memu shows you the receipts.
            </p>
          </div>
        </div>
      </section>

      {/* ── TwinDemo ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingBottom: 100 }}>
        <div className="container">
          <TwinDemo />
        </div>
      </section>

      {/* ── What it actually does ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 80 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 40 }}>
            <h2 className="section-title">What it actually does</h2>
            <p className="section-subtitle" style={{ margin: '0 auto' }}>Memu doesn&rsquo;t just remember. It works.</p>
          </div>
          <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <p style={{ fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '1.5rem' }}>
              It builds a living understanding of each part of your life from the things you already tell it — no forms, no maintenance, it keeps itself current. It surfaces what you&rsquo;d otherwise forget: the commitment slipping, the deadline approaching, the thing you said three weeks ago that matters again now. It drafts, plans, and searches on your behalf — and brings it back to you to approve. It&rsquo;s proactive, but it&rsquo;s never unsupervised. Everything it does, it shows you.
            </p>
            <p style={{ fontSize: '1.2rem', fontWeight: 600, color: 'var(--text-main)', textAlign: 'center', marginTop: '2rem' }}>
              A Chief of Staff anticipates. It doesn&rsquo;t act behind your back.
            </p>
          </div>
        </div>
      </section>

      {/* ── Family & Sovereignty ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div className="grid-2-cards">
            <div className="card-ai">
              <h3 style={{ marginBottom: 16 }}>Family is where it started — not where it stops</h3>
              <p>
                Memu began as a household Chief of Staff, and that&rsquo;s still its most proven form: shared logistics that stop living in one parent&rsquo;s head, each family member with their own private space, children with age-appropriate guardrails, the family layer building naturally from individuals rather than being imposed on them.
              </p>
              <p style={{ marginTop: '1rem' }}>
                But the architecture that makes a family work — separate people, separate contexts, one owner who can see across — is the same architecture that makes a founder work. Or a researcher. Or anyone running more than one world at once. Family proved the model. The model goes further.
              </p>
            </div>
            <div className="card-ai">
              <h3 style={{ marginBottom: 16 }}>Your data. Your hardware. Your call.</h3>
              <p>
                Run Memu in our cloud, on your own server, or on a box in your home. Your data doesn&rsquo;t touch our servers unless you choose that.
              </p>
              <p style={{ marginTop: '1rem' }}>
                And it&rsquo;s yours to take. Your understanding belongs to you — when you leave, when someone in your family starts a new chapter, the context travels with the person it belongs to. The AI stays behind. The understanding goes with you.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Comparison table ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 56 }}>
            <h2 className="section-title">Not a chatbot. Not a folder. A Chief of Staff.</h2>
          </div>
          <div style={{ overflowX: 'auto', maxWidth: '900px', margin: '0 auto' }}>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th></th>
                  <th>A general AI assistant</th>
                  <th style={{ color: 'var(--primary)' }}>Memu</th>
                </tr>
              </thead>
              <tbody>
                {TABLE_ROWS.map(([feature, other, memu]) => (
                  <tr key={feature}>
                    <td style={{ fontWeight: 500, color: 'var(--text-main)' }}>{feature}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{other}</td>
                    <td style={{ color: 'var(--primary)', fontWeight: 600 }}>{memu}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="text-center" style={{ marginTop: 48 }}>
            <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              Get Early Access
            </a>
          </div>
        </div>
      </section>
    </>
  );
}
