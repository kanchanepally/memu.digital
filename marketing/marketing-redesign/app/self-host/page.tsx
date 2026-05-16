import { MarkSovereign, MarkLens, MarkEngine, MarkThread } from '@/components/Marks';

export const metadata = {
  title: 'Self-host | Memu',
  description: 'Run it on your cloud, your server, or a box in your house.',
};

const OPTIONS = [
  { mark: MarkLens, title: 'Our cloud', subtitle: 'The simplest start', body: 'Anonymised by the Digital Twin before anything reaches an external model. Every exchange in your Privacy Ledger.' },
  { mark: MarkEngine, title: 'Your own server', subtitle: 'Hardware you control', body: 'Run the whole thing on hardware you control. Your data never reaches us. The architecture is identical; the location is yours.' },
  { mark: MarkSovereign, title: 'A box in your home', subtitle: 'The fullest form of ownership', body: "Your context lives in your house. Memu has been running this way, daily, in its founder's home for months — this isn't a someday plan." },
];

export default function SelfHostPage() {
  return (
    <>
      <section className="hero">
        <div className="hero-glow" aria-hidden />
        <div className="container" style={{ position: 'relative' }}>
          <div className="eyebrow">Self-host</div>
          <h1 className="hero-title">
            Run it on your cloud,<br />
            your server, or<br />
            <em>a box in your house</em>.
          </h1>
          <p className="hero-subtitle">
            Memu doesn&rsquo;t require our infrastructure. It&rsquo;s designed to run where you decide.
          </p>
          <div className="hero-mark">
            <MarkSovereign size={220} color="var(--brand)" />
          </div>
        </div>
      </section>

      <section className="section section-tint">
        <div className="container">
          <div className="eyebrow">Three ways to run it</div>
          <h2 className="section-title">
            Same engine.<br />Your <em>choice</em> of soil.
          </h2>
          <div className="grid-3" style={{ marginTop: 56 }}>
            {OPTIONS.map(o => (
              <div key={o.title} className="card">
                <div className="card-mark"><o.mark size={64} color="var(--brand)" /></div>
                <div className="eyebrow" style={{ marginBottom: 8 }}>{o.subtitle}</div>
                <h3 className="card-title">{o.title}</h3>
                <p className="card-body">{o.body}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section text-center">
        <div className="container-narrow">
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 28 }}>
            <MarkThread size={88} color="var(--brand)" />
          </div>
          <div className="eyebrow" style={{ justifyContent: 'center' }}>The principle</div>
          <h2 className="section-title" style={{ margin: '0 auto 24px' }}>
            <em>Portability</em><br />is the point.
          </h2>
          <p className="prose-serif" style={{ marginBottom: 40 }}>
            Wherever it runs, your understanding belongs to you and travels with you. When a family member starts a new chapter, their context goes with the person it belongs to. The intelligence is the engine; <strong>you own the understanding it built</strong>.
          </p>
          <a href="https://tally.so/r/ODDZvA" target="_blank" rel="noopener noreferrer" className="btn btn-primary">
            Get Early Access →
          </a>
        </div>
      </section>
    </>
  );
}
