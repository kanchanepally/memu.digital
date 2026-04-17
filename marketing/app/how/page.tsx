export default function HowItWorks() {
  return (
    <div className="container section">
      <h1 className="hero-title">How it works</h1>
      <p className="section-subtitle">
        Behind the scenes, Memu translates your reality into an anonymous digital twin before the AI ever sees it.
      </p>

      <div className="grid-2" style={{ marginBottom: '64px' }}>
        <div>
          <h2 style={{ marginBottom: '24px' }}>The Anonymous Digital Twin</h2>
          <p>
            Before your query reaches the cloud, Memu's local gateway strips out your defining identity. 
            Real names, schools, addresses, and friends are mapped to persistent anonymous labels.
          </p>
          <p>
            <strong>"Alice has swimming at Central Pool"</strong> becomes <strong>"Child-1 has Activity-3 at Location-2"</strong>.
          </p>
          <p>
            The artificial intelligence provides a brilliant, context-rich answer using those labels. Memu translates it back. Your family sees real names. The AI saw nothing but anonymous tokens.
          </p>
        </div>
        <div className="code-block">
          <div><span className="token-comment"># What you send:</span></div>
          <div><span className="token-string">"Can you check if Alice's swimming clashes?"</span></div>
          <br/>
          <div><span className="token-comment"># What the AI sees:</span></div>
          <div><span className="token-string">"Can you check if Child-1's Activity-3 clashes?"</span></div>
          <br/>
          <div><span className="token-comment"># What you receive back:</span></div>
          <div><span className="token-string">"Yes, Alice's swimming at 4pm clashes with Bob's dentist appointment at 3:30pm."</span></div>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '64px' }}>
        <div className="code-block" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ color: 'var(--primary)', textAlign: 'center' }}>
            <div><svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg></div>
            <div style={{ marginTop: '16px', fontWeight: 500 }}>Chat + Calendar + Email + Photos</div>
          </div>
        </div>
        <div>
          <h2 style={{ marginBottom: '24px' }}>The Context Engine</h2>
          <p>
            An AI is only as smart as what it remembers. Memu passively observes your life across four distinct silos — your family WhatsApp group, Google Calendar, school emails, and photo metadata (via Immich). 
          </p>
          <p>
            It unifies these inputs into a single, searchable memory graph. When you ask a question, Memu doesn't just guess; it retrieves the exact intersecting context from across your digital life before asking the AI to reason about it.
          </p>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '80px' }}>
        <div>
          <h2 style={{ marginBottom: '24px' }}>Compiled Synthesis ("Spaces")</h2>
          <p>
            Memu doesn't just store an endlessly growing pile of raw messages. It actively distills chaos into structured understanding.
          </p>
          <p>
            When you mention "Alice has ballet on Tuesdays" in a casual chat, Memu automatically updates Alice's dedicated Markdown profile ("Space") behind the scenes. Your scattered conversations are continuously compiled into readable, highly accurate profile pages for every family member, routine, and commitment.
          </p>
        </div>
        <div className="code-block">
          <div><span className="token-comment"># Generated Profile: Child-1 (Alice)</span></div>
          <div><span className="token-string">- Routine: Ballet on Tuesdays (4pm-5pm)</span></div>
          <div><span className="token-string">- Routine: Swimming on Thursdays</span></div>
          <br/>
          <div><span className="token-comment"># Active Commitments</span></div>
          <div><span className="token-string">- Need to buy new ballet shoes by Oct 12th</span></div>
        </div>
      </div>

      <div className="card" style={{ background: 'var(--surface-low)' }}>
        <h2 style={{ marginBottom: '24px' }}>Deployment Options</h2>
        <ul>
          <li><strong>Memu Core (Tier 1 Cloud Engine):</strong> The frictionless tier powered by enterprise cloud intelligence (Gemini/Cloud APIs) paired with the local anonymisation proxy. Accessible via WhatsApp today.</li>
          <li><strong>Memu OS (Tier 2/3 Self-Hosted):</strong> True data sovereignty. The full hardware orchestration layer running Matrix, Immich (photos), Ollama (local execution), and Postgres directly on your own Intel N100 hardware at home.</li>
        </ul>
      </div>
    </div>
  );
}
