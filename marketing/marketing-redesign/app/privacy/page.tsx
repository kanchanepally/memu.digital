import { MarkPrivacy, MarkWalls, MarkLens, MarkReceipts, MarkSovereign } from '@/components/Marks';

export const metadata = {
  title: 'Privacy | Memu',
  description: "Privacy isn't a feature here. It's the shape of the thing.",
};

const PRINCIPLES = [
  {
    mark: MarkPrivacy,
    title: 'The AI never knows who you are.',
    body: "The Digital Twin replaces every identifying detail before anything reaches an external model. Not encrypted-so-we-could-decrypt-it. Anonymised, so there's nothing to decrypt.",
  },
  {
    mark: MarkWalls,
    title: "Your worlds can't be correlated — even by us.",
    body: 'Each collective has its own separate identity map. The same real person is a different anonymous label in your household and your work. There is no master key. We couldn\'t build the complete picture if we wanted to — and not wanting to isn\'t good enough, so we made it impossible.',
  },
  {
    mark: MarkLens,
    title: 'You hold the only lens that sees across.',
    body: 'You can look across your own collectives, because you own them. Nothing else can — not another user, not an external AI, not Memu itself acting on its own. The whole-life view exists for exactly one person: you.',
  },
  {
    mark: MarkReceipts,
    title: 'You can verify all of it.',
    body: "The Privacy Ledger shows you what was sent, every time. This isn't a trust exercise. It's an audit you can run yourself.",
  },
];

export default function PrivacyPage() {
  return (
    <>
      <section className="hero">
        <div className="hero-glow" aria-hidden />
        <div className="container" style={{ position: 'relative' }}>
          <div className="eyebrow">Privacy</div>
          <h1 className="hero-title">
            Not a feature.<br />
            The <em>shape</em><br />
            of the thing.
          </h1>
          <p className="hero-subtitle">
            Most products bolt privacy on: a setting, a policy, a promise. Memu is built the other way round — the privacy is the architecture, and the architecture is what makes the product good.
          </p>
          <div className="hero-mark">
            <MarkPrivacy size={220} color="var(--brand)" />
          </div>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container">
          <div className="eyebrow">Four principles</div>
          <h2 className="section-title">
            Architecture, not <em>promise</em>.
          </h2>
          <div className="grid-4" style={{ marginTop: 56 }}>
            {PRINCIPLES.map(p => (
              <div key={p.title} className="card" style={{ padding: '36px 32px' }}>
                <div className="card-mark"><p.mark size={64} color="var(--brand)" /></div>
                <h3 className="card-title" style={{ fontSize: '1.625rem' }}>{p.title}</h3>
                <p className="card-body">{p.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section text-center">
        <div className="container-narrow">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 28 }}>
            <MarkSovereign size={88} color="var(--brand)" />
          </div>
          <h2 className="section-title" style={{ margin: '0 auto 24px' }}>
            And you can leave<br />with <em>everything</em>.
          </h2>
          <p className="prose-serif" style={{ marginBottom: 40 }}>
            Your understanding is yours. Export it, move it, take it to a new chapter of life. The AI stays behind; what it understood about you travels with you.
          </p>
          <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
            Get Early Access →
          </a>
        </div>
      </section>
    </>
  );
}
