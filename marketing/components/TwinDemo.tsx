"use client";
import { useState, useEffect, useCallback } from 'react';

const STAGE_MS = 4500;

type SegmentKind = 'plain' | 'real' | 'token';
interface Seg { t: SegmentKind; v: string; }

interface StageContent {
  title: string;
  badge: string;
  badgeKind: 'green' | 'amber' | 'purple';
  segments?: Seg[];
  shimmer?: boolean;
  note?: string;
  noteGreen?: boolean;
}

const CONTENTS: StageContent[] = [
  {
    title: "Your message",
    badge: "Real names — your eyes only",
    badgeKind: "green",
    segments: [
      { t: "plain", v: "Does " }, { t: "real", v: "Jamie's" },
      { t: "plain", v: " swimming on Thursday at 4pm clash with my " },
      { t: "real", v: "dentist" }, { t: "plain", v: " appointment?" },
    ],
  },
  {
    title: "Anonymised query — sent to AI",
    badge: "No identity leaves your device",
    badgeKind: "amber",
    segments: [
      { t: "plain", v: "Does " }, { t: "token", v: "Child-1's" },
      { t: "plain", v: " " }, { t: "token", v: "Activity-2" },
      { t: "plain", v: " on " }, { t: "token", v: "Day-4" },
      { t: "plain", v: " at " }, { t: "token", v: "Time-3" },
      { t: "plain", v: " clash with " }, { t: "token", v: "Adult-1's" },
      { t: "plain", v: " " }, { t: "token", v: "Appointment-1" },
      { t: "plain", v: "?" },
    ],
    note: "Jamie → Child-1 · swimming → Activity-2 · dentist → Appointment-1",
  },
  {
    title: "AI response (tokens only)",
    badge: "Brilliant reasoning — zero identity",
    badgeKind: "purple",
    segments: [
      { t: "plain", v: "Yes — " }, { t: "token", v: "Child-1's" },
      { t: "plain", v: " " }, { t: "token", v: "Activity-2" },
      { t: "plain", v: " at 16:00 overlaps with " }, { t: "token", v: "Adult-1's" },
      { t: "plain", v: " " }, { t: "token", v: "Appointment-1" },
      { t: "plain", v: " at 15:30. 30-minute gap." },
    ],
    note: "The AI never learned who Child-1 or Adult-1 are.",
  },
  {
    title: "Translating tokens → real names",
    badge: "Happening locally on your device",
    badgeKind: "amber",
    shimmer: true,
  },
  {
    title: "Your private, personalised answer",
    badge: "Personalised · Private · Complete",
    badgeKind: "green",
    segments: [
      { t: "plain", v: "Yes — " }, { t: "real", v: "Jamie's" },
      { t: "plain", v: " swimming at " }, { t: "real", v: "4pm" },
      { t: "plain", v: " overlaps with your " }, { t: "real", v: "dentist" },
      { t: "plain", v: " at " }, { t: "real", v: "3:30pm" },
      { t: "plain", v: ". 30-minute gap." },
    ],
    note: "Stored in Jamie's Space ✓",
    noteGreen: true,
  },
];

const NODES = [
  { label: "You", sublabel: "send" },
  { label: "Digital Twin", sublabel: "anonymise" },
  { label: "AI Cloud", sublabel: "reason" },
  { label: "Digital Twin", sublabel: "translate" },
  { label: "You", sublabel: "receive" },
];

const NodeIcon = ({ index, active, past }: { index: number; active: boolean; past: boolean }) => {
  const color = active ? '#fff' : past ? 'var(--primary)' : 'var(--text-secondary)';
  if (index === 0 || index === 4) return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
    </svg>
  );
  if (index === 1 || index === 3) return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  );
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <path d="M12 8v4l3 3"/>
    </svg>
  );
};

const badgeStyles: Record<string, React.CSSProperties> = {
  green: { background: 'rgba(34, 197, 94, 0.12)', color: '#15803d', border: '1px solid rgba(34,197,94,0.25)' },
  amber: { background: 'rgba(245, 158, 11, 0.12)', color: '#92400e', border: '1px solid rgba(245,158,11,0.25)' },
  purple: { background: 'rgba(118, 75, 162, 0.12)', color: '#6b21a8', border: '1px solid rgba(118,75,162,0.25)' },
};

const segColor: Record<SegmentKind, string> = {
  plain: 'var(--text-main)',
  real: 'var(--primary)',
  token: '#b45309',
};

export const TwinDemo = () => {
  const [stage, setStage] = useState(0);
  const [fills, setFills] = useState([0, 0, 0, 0]);
  const [contentVisible, setContentVisible] = useState(true);

  const goTo = useCallback((next: number) => {
    setContentVisible(false);
    setTimeout(() => {
      setStage(next);
      setFills(prev => {
        const f = [...prev];
        for (let i = 0; i < next; i++) f[i] = 100;
        if (next < 5) f[next] = 0; // connector ahead not filled
        return f;
      });
      setContentVisible(true);
    }, 260);
  }, []);

  useEffect(() => {
    const tick = setInterval(() => {
      setStage(s => {
        const next = (s + 1) % 5;
        // animate connector fill
        if (s < 4) {
          setFills(prev => {
            const f = [...prev];
            f[s] = 100;
            return f;
          });
        }
        setContentVisible(false);
        setTimeout(() => {
          setFills(prev => {
            const f = [...prev];
            // reset all then fill up to next
            for (let i = 0; i < 4; i++) f[i] = i < next ? 100 : 0;
            return f;
          });
          setContentVisible(true);
        }, 260);
        return next;
      });
    }, STAGE_MS);
    return () => clearInterval(tick);
  }, []);

  const content = CONTENTS[stage];

  return (
    <div style={{ maxWidth: 820, margin: '0 auto' }}>
      {/* Pipeline */}
      <div style={{ overflowX: 'auto', paddingBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', minWidth: 560, padding: '0 16px' }}>
          {NODES.map((node, i) => {
            const active = i === stage;
            const past = i < stage;
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', flex: i < 4 ? '1 1 0' : 'none' }}>
                {/* Node */}
                <button
                  onClick={() => goTo(i)}
                  title={`Jump to: ${node.label}`}
                  style={{
                    display: 'flex', flexDirection: 'column', alignItems: 'center',
                    gap: 8, background: 'none', border: 'none', cursor: 'pointer',
                    flexShrink: 0,
                  }}
                >
                  <div style={{
                    width: 52, height: 52, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: active
                      ? 'linear-gradient(135deg, #667eea, #764ba2)'
                      : past ? 'rgba(80,84,181,0.1)' : 'var(--surface-lowest)',
                    border: active
                      ? '2px solid transparent'
                      : past ? '2px solid var(--primary)' : '2px solid rgba(46,51,54,0.1)',
                    boxShadow: active ? '0 0 0 4px rgba(102,126,234,0.2)' : 'none',
                    transition: 'all 0.4s ease',
                  }}>
                    <NodeIcon index={i} active={active} past={past} />
                  </div>
                  <div style={{ textAlign: 'center', lineHeight: 1.3 }}>
                    <div style={{
                      fontFamily: 'Manrope, sans-serif', fontWeight: 700,
                      fontSize: '0.78rem', color: active ? 'var(--primary)' : 'var(--text-main)',
                      transition: 'color 0.3s',
                    }}>{node.label}</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{node.sublabel}</div>
                  </div>
                </button>

                {/* Connector */}
                {i < 4 && (
                  <div style={{
                    flex: 1, height: 3, borderRadius: 2,
                    background: 'var(--surface-hover)',
                    margin: '0 4px', marginBottom: 36,
                    position: 'relative', overflow: 'hidden',
                  }}>
                    <div style={{
                      position: 'absolute', top: 0, left: 0, height: '100%',
                      width: `${fills[i]}%`,
                      background: 'linear-gradient(90deg, #667eea, #764ba2)',
                      transition: 'width 0.4s ease',
                      borderRadius: 2,
                    }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Content Panel */}
      <div style={{
        marginTop: 24, borderRadius: 20,
        background: 'var(--surface-lowest)',
        border: '1px solid rgba(46,51,54,0.07)',
        boxShadow: '0 4px 24px rgba(46,51,54,0.06)',
        padding: '28px 32px',
        minHeight: 180,
        opacity: contentVisible ? 1 : 0,
        transition: 'opacity 0.25s ease',
      }}>
        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
          <span style={{
            fontFamily: 'Manrope, sans-serif', fontWeight: 700,
            fontSize: '0.95rem', color: 'var(--text-main)',
          }}>{content.title}</span>
          <span style={{
            fontSize: '0.78rem', fontWeight: 600, padding: '4px 12px',
            borderRadius: 9999, ...badgeStyles[content.badgeKind],
          }}>{content.badge}</span>
        </div>

        {/* Message */}
        {content.shimmer ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {[100, 75, 50].map((w, i) => (
              <div key={i} style={{
                height: 18, borderRadius: 6,
                background: 'linear-gradient(90deg, var(--surface-low) 25%, var(--surface-hover) 50%, var(--surface-low) 75%)',
                backgroundSize: '200% 100%',
                animation: 'shimmerAnim 1.4s ease infinite',
                width: `${w}%`,
                animationDelay: `${i * 0.15}s`,
              }} />
            ))}
          </div>
        ) : (
          <p style={{ fontSize: '1.08rem', lineHeight: 1.7, color: 'var(--text-main)', marginBottom: content.note ? 16 : 0 }}>
            {content.segments?.map((seg, i) => (
              <span key={i} style={{
                color: segColor[seg.t],
                fontWeight: seg.t !== 'plain' ? 600 : 400,
                background: seg.t === 'real' ? 'rgba(80,84,181,0.08)' : seg.t === 'token' ? 'rgba(180,93,9,0.08)' : 'none',
                borderRadius: seg.t !== 'plain' ? 4 : 0,
                padding: seg.t !== 'plain' ? '1px 4px' : 0,
              }}>{seg.v}</span>
            ))}
          </p>
        )}

        {/* Note */}
        {content.note && (
          <p style={{
            fontSize: '0.82rem', color: content.noteGreen ? '#15803d' : 'var(--text-secondary)',
            fontWeight: content.noteGreen ? 600 : 400, marginBottom: 0,
            background: content.noteGreen ? 'rgba(34,197,94,0.08)' : 'transparent',
            padding: content.noteGreen ? '6px 12px' : 0,
            borderRadius: content.noteGreen ? 8 : 0,
            display: 'inline-block',
          }}>{content.note}</p>
        )}
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16, marginTop: 20 }}>
        <button
          onClick={() => goTo((stage - 1 + 5) % 5)}
          style={{
            padding: '8px 20px', borderRadius: 9999, border: '1px solid rgba(46,51,54,0.12)',
            background: 'var(--surface-lowest)', cursor: 'pointer',
            fontFamily: 'Inter, sans-serif', fontWeight: 500, fontSize: '0.9rem',
            color: 'var(--text-secondary)', transition: 'all 0.15s ease',
          }}
        >← Prev</button>
        <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
          Stage {stage + 1} of 5
        </span>
        <button
          onClick={() => goTo((stage + 1) % 5)}
          style={{
            padding: '8px 20px', borderRadius: 9999, border: '1px solid rgba(46,51,54,0.12)',
            background: 'var(--surface-lowest)', cursor: 'pointer',
            fontFamily: 'Inter, sans-serif', fontWeight: 500, fontSize: '0.9rem',
            color: 'var(--text-secondary)', transition: 'all 0.15s ease',
          }}
        >Next →</button>
      </div>

      <style>{`
        @keyframes shimmerAnim {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  );
};
