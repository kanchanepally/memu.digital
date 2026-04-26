import Link from 'next/link';
import { HeroCycler } from '@/components/HeroCycler';
import { TwinDemo } from '@/components/TwinDemo';

export const metadata = {
  title: 'Memu — Intelligence without surveillance',
  description: 'Your AI that knows everything about your life and nothing about your identity. It thinks for you, acts for you, and never reveals who you are.',
};

const TABLE_ROWS = [
  ['Remembers your life', 'One conversation', 'What you type in', 'Everything, automatically'],
  ['Anticipates', 'Never', 'Never', 'Every morning + throughout the day'],
  ['Protects your identity', 'No', 'N/A', 'The AI never sees your real name'],
  ['Acts on your behalf', 'No', 'No', 'Drafts, searches, reminds, plans'],
  ['Compounds over time', 'No', 'No', 'Every interaction makes it smarter'],
  ['Works for a family', 'No', 'Some', 'Individual-first, family-emergent'],
  ['Your data, your hardware', 'No', 'No', 'Self-host or use our cloud'],
];

export default function Home() {
  return (
    <>
      {/* ── Hero ── */}
      <section className="section text-center" style={{ paddingTop: '120px', paddingBottom: '80px' }}>
        <div className="container">
          <span className="badge">Private Beta</span>
          <h1 className="hero-title" style={{ marginBottom: 8 }}>
            Intelligence without<br />
            <span className="gradient-text">surveillance.</span>
          </h1>
          <div style={{ fontSize: '1.5rem', fontWeight: 600, minHeight: '2.4rem', marginBottom: 16 }}>
            <HeroCycler />
          </div>
          <p className="hero-subtitle" style={{ marginTop: 8 }}>
            Your AI that knows everything about your life — and nothing about your identity.
            It thinks for you, acts for you, and never reveals who you are. Until you say so.
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
            Built by a parent who was tired of being his family&rsquo;s middleware.
          </p>
        </div>
      </section>

      {/* ── Three panels ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div className="grid-3">
            <div className="card">
              <div className="card-ai-icon" style={{ marginBottom: 20 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: 12 }}>It learns. Silently.</h3>
              <p style={{ marginBottom: 0 }}>
                Talk about your life — plans, tasks, ideas, worries. Memu listens and builds a living
                understanding that grows richer every day. You don&rsquo;t maintain it. It maintains itself.
              </p>
            </div>
            <div className="card">
              <div className="card-ai-icon" style={{ marginBottom: 20 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: 12 }}>It thinks. Privately.</h3>
              <p style={{ marginBottom: 0 }}>
                Before anything reaches the AI, your names, places, and personal details are replaced
                with anonymous labels. The AI reasons brilliantly. It never learns who you are.
                You can see exactly what was sent — every time — in the Privacy Ledger.
              </p>
            </div>
            <div className="card">
              <div className="card-ai-icon" style={{ marginBottom: 20 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: 12 }}>It acts. On your terms.</h3>
              <p style={{ marginBottom: 0 }}>
                Memu doesn&rsquo;t wait to be asked. It nudges you about forgotten commitments, drafts
                replies for your approval, plans meals from your preferences, and searches the web
                without revealing your identity. A Chief of Staff that works while you sleep.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── TwinDemo ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 56 }}>
            <h2 className="section-title">See exactly what the AI sees.</h2>
            <p className="section-subtitle" style={{ margin: '0 auto' }}>
              And, more importantly, what it doesn&rsquo;t. Every query. Every response. Click any stage.
            </p>
          </div>
          <TwinDemo />
        </div>
      </section>

      {/* ── Expansion + Sovereignty ── */}
      <section className="section" style={{ background: 'var(--surface-low)', paddingTop: 80, paddingBottom: 80 }}>
        <div className="container">
          <div className="grid-2-cards">
            <div className="card-ai">
              <div className="card-ai-icon" style={{ marginBottom: 20 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: 16 }}>Start personal. Grow into your family.</h3>
              <p>
                Each person has their own private space. Add a partner when you&rsquo;re ready.
                Add children with age-appropriate guardrails. The family layer builds naturally
                from individual atoms. When someone leaves for university or a new chapter,
                they take their data with them. Literally — on a USB drive.
              </p>
            </div>
            <div className="card-ai">
              <div className="card-ai-icon" style={{ marginBottom: 20 }}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8m-4-4v4"/>
                </svg>
              </div>
              <h3 style={{ marginBottom: 16 }}>Your data. Your hardware. Your rules.</h3>
              <p>
                Run Memu in our cloud, on your own server, or on a box in your house. Your data
                never touches our servers unless you choose. Plug in an encrypted USB drive —
                that&rsquo;s your personal Pod. Unplug it and your context goes with you.
                The AI stays behind. Your understanding travels.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Comparison table ── */}
      <section className="section" style={{ paddingTop: 100, paddingBottom: 100 }}>
        <div className="container">
          <div className="text-center" style={{ marginBottom: 56 }}>
            <h2 className="section-title">Not a chatbot. Not a task app.</h2>
            <p className="section-subtitle" style={{ margin: '0 auto' }}>A Chief of Staff.</p>
          </div>
          <div style={{ overflowX: 'auto' }}>
            <table className="comparison-table">
              <thead>
                <tr>
                  <th></th>
                  <th>Chatbot</th>
                  <th>Task app</th>
                  <th style={{ color: 'var(--primary)' }}>Memu</th>
                </tr>
              </thead>
              <tbody>
                {TABLE_ROWS.map(([feature, chatbot, task, memu]) => (
                  <tr key={feature}>
                    <td style={{ fontWeight: 500, color: 'var(--text-main)' }}>{feature}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{chatbot}</td>
                    <td style={{ color: 'var(--text-secondary)' }}>{task}</td>
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
