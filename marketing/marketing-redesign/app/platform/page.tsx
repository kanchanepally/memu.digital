import Link from 'next/link';
import { MarkEngine, MarkFamily, MarkGarden, MarkSpace, MarkLens } from '@/components/Marks';

export const metadata = {
  title: 'Platform | Memu',
  description: 'One engine. As many worlds as your life has.',
};

const WORLDS: { title: string; body: string; mark: React.ComponentType<{ size?: number; color?: string }> }[] = [
  { title: 'Your household', body: "Shared logistics, each member's private space, children with guardrails. The most proven form.", mark: MarkFamily },
  { title: 'Your work', body: "What you're tracking, what you can't drop, the thinking you don't want sitting in a general chatbot under your name.", mark: MarkEngine },
  { title: 'A venture', body: "A company you're building, with its own projects inside it.", mark: MarkGarden },
  { title: 'A research project', body: "Fieldwork, interviews, analysis, with participant identities protected by architecture, not by promise.", mark: MarkSpace },
];

export default function PlatformPage() {
  return (
    <>
      <section className="hero">
        <div className="hero-glow" aria-hidden />
        <div className="container" style={{ position: 'relative' }}>
          <div className="eyebrow">Platform</div>
          <h1 className="hero-title">
            One engine.<br />
            <em>As many worlds</em><br />
            as your life has.
          </h1>
          <p className="hero-subtitle">
            Most tools make you choose: an app for the family, another for work. Each one a separate pile, none aware they&rsquo;re all you.
          </p>
          <p className="hero-subtitle" style={{ marginTop: 0 }}>
            Memu is <em className="dim">one engine</em> you point at every part of your life.
          </p>
          <div className="hero-mark">
            <MarkEngine size={220} color="var(--brand)" />
          </div>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container-narrow">
          <div className="eyebrow">What a collective is</div>
          <h2 className="section-title">
            A single, <em>walled</em> world.
          </h2>
          <p className="prose-serif">
            A collective holds its own people, its own routines, its own commitments, its own compiled understanding — and it <strong>cannot see</strong>, and is never mixed with, any of your others.
          </p>
          <p className="prose-serif">
            The same real person can appear in two of your collectives and Memu treats them as unconnected, on purpose. That&rsquo;s not a limitation. <strong>That&rsquo;s the product.</strong>
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="eyebrow">What you can point it at</div>
          <h2 className="section-title">
            Four worlds.<br />One <em>mind</em>.
          </h2>
          <div className="grid-2" style={{ marginTop: 56 }}>
            {WORLDS.map(w => (
              <div key={w.title} className="card" style={{ flexDirection: 'row', gap: 24, alignItems: 'flex-start', padding: '36px 36px' }}>
                <div style={{ color: 'var(--brand)', flexShrink: 0 }}>
                  <w.mark size={72} color="var(--brand)" />
                </div>
                <div>
                  <h3 className="card-title" style={{ marginBottom: 10 }}>{w.title}</h3>
                  <p className="card-body">{w.body}</p>
                </div>
              </div>
            ))}
          </div>
          <div style={{ maxWidth: 720, margin: '60px auto 0', textAlign: 'center' }}>
            <p className="prose-serif" style={{ fontSize: '1.375rem', fontStyle: 'italic', color: 'var(--text)' }}>
              A collective isn&rsquo;t a folder. A folder nests files. A collective bounds memory, identity, and understanding — and keeps them from ever touching your other worlds.
            </p>
          </div>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container">
          <div className="grid-2" style={{ gap: 60, alignItems: 'center' }}>
            <div style={{ textAlign: 'center' }}>
              <MarkLens size={200} color="var(--brand)" />
            </div>
            <div>
              <div className="eyebrow">Across all of them</div>
              <h2 className="section-title">
                And <em>you</em> — across all of them.
              </h2>
              <p className="prose-serif" style={{ fontSize: '1.1875rem' }}>
                You own every collective, so you — and only you — can ask Memu to look across them. Your true whole-life view, assembled the moment you ask, shown to you, never merged into a permanent pile and never visible to anyone else.
              </p>
              <p className="prose-serif" style={{ fontSize: '1.375rem', color: 'var(--text)' }}>
                One engine. Many worlds. <em>One owner who sees the whole.</em>
              </p>
              <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ marginTop: 16 }}>
                Get Early Access →
              </a>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
