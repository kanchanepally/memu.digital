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
          <div><span className="token-comment"># What Claude sees:</span></div>
          <div><span className="token-string">"Can you check if Child-1's Activity-3 clashes?"</span></div>
          <br/>
          <div><span className="token-comment"># What you receive back:</span></div>
          <div><span className="token-string">"Yes, Alice's swimming at 4pm clashes with Bob's dentist appointment at 3:30pm."</span></div>
        </div>
      </div>

      <div className="card" style={{ background: 'var(--surface-low)' }}>
        <h2 style={{ marginBottom: '24px' }}>Deployment Options</h2>
        <ul>
          <li><strong>Memu Core:</strong> Cloud-safe and zero-friction. Start by messaging a WhatsApp contact, using BYOK (Bring Your Own Key) for your AI calls over Anthropic. </li>
          <li><strong>Memu OS:</strong> True data sovereignty. Run the full Matrix, Immich (photos), Ollama (local AI), and Postgres stack directly on your own Intel N100 hardware at home. For the ultimate self-hoster.</li>
        </ul>
      </div>
    </div>
  );
}
