import React from 'react';

export const Logo = ({ scale = 0.35 }: { scale?: number }) => {
  return (
    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px' }}>
      <svg width={400 * scale} height={120 * scale} viewBox="0 0 400 120" style={{ display: 'block' }}>
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
          fontFamily="Manrope, -apple-system, sans-serif"
          fontSize="48"
          fontWeight="800"
          letterSpacing="-0.04em"
          fill="url(#memuGradient1)"
        >
          memu
        </text>

        {/* Telugu accent */}
        <text
          x="260"
          y="70"
          fontFamily="sans-serif"
          fontSize="24"
          fontWeight="400"
          fill="#667eea"
          opacity="0.6"
        >
          మేము
        </text>
      </svg>
    </div>
  );
};
