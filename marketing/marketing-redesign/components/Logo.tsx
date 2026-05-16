/**
 * Memu Logo — Venn concept with framing lens-ring.
 *
 * Three circles in triangular formation (referencing "memu" — "we" in Telugu)
 * wrapped in a delicate lens-ring suggesting focus / observation.
 * The Venn uses mix-blend-mode: multiply so overlaps naturally darken.
 *
 * Use:
 *   <Logo size={28} />                  // standard masthead size
 *   <Logo size={64} />                  // hero size
 *   <Logo size={20} showRing={false} /> // compact (favicon, footer)
 */

import React from 'react';

interface LogoProps {
  size?: number;
  color1?: string;
  color2?: string;
  showRing?: boolean;
}

export function Logo({
  size = 28,
  color1 = '#5054B5',
  color2 = '#9094FA',
  showRing = true,
}: LogoProps) {
  const gradId = `memu-logo-grad-${size}`;
  return (
    <svg width={size} height={size} viewBox="0 0 80 80" style={{ display: 'block' }} aria-label="Memu">
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={color1} />
          <stop offset="1" stopColor={color2} />
        </linearGradient>
      </defs>
      {showRing && (
        <circle
          cx="40"
          cy="40"
          r="37"
          fill="none"
          stroke={`url(#${gradId})`}
          strokeWidth="1"
          opacity="0.3"
        />
      )}
      <g style={{ mixBlendMode: 'multiply' }}>
        <circle cx="30" cy="50" r="17" fill={`url(#${gradId})`} opacity="0.85" />
        <circle cx="50" cy="50" r="17" fill={`url(#${gradId})`} opacity="0.85" />
        <circle cx="40" cy="32" r="17" fill={`url(#${gradId})`} opacity="0.85" />
      </g>
    </svg>
  );
}

/**
 * Logo lockup — mark + wordmark.
 * Use in masthead, footer, hero, and anywhere the brand presents itself.
 */
export function LogoLockup({ size = 28 }: { size?: number }) {
  return (
    <span className="brand-lockup">
      <Logo size={size} />
      <span className="brand-wordmark" style={{ fontSize: size * 0.78 }}>
        memu
      </span>
    </span>
  );
}
