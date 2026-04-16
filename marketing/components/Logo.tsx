import React from 'react';

export const Logo = ({ scale = 0.35 }: { scale?: number }) => {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
      <svg width={500 * scale} height={120 * scale} viewBox="0 0 500 120" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="memuGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#667eea" stopOpacity="1" />
            <stop offset="100%" stopColor="#764ba2" stopOpacity="1" />
          </linearGradient>
        </defs>

        {/* Icon: Three overlapping circles (Venn) */}
        <circle cx="35" cy="60" r="22" fill="url(#memuGradient1)" opacity="0.9" />
        <circle cx="55" cy="60" r="22" fill="url(#memuGradient1)" opacity="0.85" />
        <circle cx="45" cy="42" r="22" fill="url(#memuGradient1)" />

        {/* Wordmark */}
        <text
          x="95"
          y="75"
          fontFamily="Inter, sans-serif"
          fontSize="48"
          fontWeight="600"
          letterSpacing="3px"
          fill="url(#memuGradient1)"
        >
          memu
        </text>

        {/* Telugu accent */}
        <text
          x="280"
          y="78"
          fontFamily="Noto Sans Telugu, sans-serif"
          fontSize="56"
          fontWeight="600"
          fill="url(#memuGradient1)"
          opacity="0.9"
        >
          మేము
        </text>
      </svg>
    </div>
  );
};
