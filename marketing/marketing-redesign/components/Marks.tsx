/**
 * Memu — Illustration system.
 *
 * Monoline hand-drawn marks for editorial moments, card decorations,
 * empty states, and hero illustrations. All take { size, color } props
 * and use `currentColor` by default — set CSS color or pass `color` to override.
 *
 * Drawn at 56–80px viewport with soft inner fills for a unified hand.
 *
 * Usage:
 *   import { MarkLens, MarkEngine, MarkPrivacy } from '@/components/Marks';
 *
 *   <MarkLens size={64} />                    // inherits color
 *   <MarkEngine size={88} color="#5054B5" />  // brand color
 */

import React from 'react';

interface MarkProps {
  size?: number;
  color?: string;
}

// Tree branch with three leaves — Outdoor / weekend / events
export function MarkWeekend({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 14 44 Q 18 36 22 30 Q 26 24 30 22 Q 36 19 42 18" />
      <path d="M 22 30 Q 19 25 16 24" />
      <path d="M 30 22 Q 28 17 25 16" />
      <path d="M 36 20 Q 35 16 33 14" />
      <path d="M 16 24 Q 14 22 13 19 Q 12 17 14 16 Q 16 17 17 19 Q 17 22 16 24 Z" fill={color} fillOpacity="0.08" />
      <path d="M 25 16 Q 23 14 22 11 Q 22 9 24 9 Q 26 9 27 11 Q 27 14 25 16 Z" fill={color} fillOpacity="0.08" />
      <path d="M 33 14 Q 32 11 32 9 Q 33 7 35 8 Q 37 9 37 11 Q 36 13 33 14 Z" fill={color} fillOpacity="0.08" />
    </svg>
  );
}

// Bowl with rising steam — Meals / cooking
export function MarkMeals({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 12 30 Q 12 42 28 42 Q 44 42 44 30 Z" fill={color} fillOpacity="0.05" />
      <line x1="10" y1="30" x2="46" y2="30" />
      <path d="M 22 22 Q 20 18 22 14 Q 24 10 22 6" />
      <path d="M 28 24 Q 30 20 28 16 Q 26 12 28 8" />
      <path d="M 34 22 Q 32 18 34 14 Q 36 10 34 6" />
    </svg>
  );
}

// Constellation of dots, one incomplete — What's missing
export function MarkMissing({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="14" cy="18" r="2.5" fill={color} />
      <circle cx="28" cy="12" r="2.5" fill={color} />
      <circle cx="42" cy="20" r="2.5" fill={color} />
      <circle cx="22" cy="34" r="2.5" fill={color} />
      <circle cx="38" cy="40" r="2.5" fill="none" strokeDasharray="2 2" />
      <line x1="14" y1="18" x2="28" y2="12" />
      <line x1="28" y1="12" x2="42" y2="20" />
      <line x1="14" y1="18" x2="22" y2="34" />
      <line x1="22" y1="34" x2="38" y2="40" strokeDasharray="2 3" opacity="0.5" />
      <line x1="42" y1="20" x2="38" y2="40" strokeDasharray="2 3" opacity="0.5" />
    </svg>
  );
}

// Shield with key — Privacy / sovereignty
export function MarkPrivacy({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 28 10 L 14 16 L 14 26 Q 14 38 28 46 Q 42 38 42 26 L 42 16 Z" fill={color} fillOpacity="0.05" />
      <circle cx="28" cy="24" r="3" />
      <path d="M 28 27 L 28 32" />
      <path d="M 26 30 L 30 30" />
    </svg>
  );
}

// Open page / book — A Space / compiled context
export function MarkSpace({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 8 14 L 8 42 L 28 38 L 48 42 L 48 14 L 28 18 Z" fill={color} fillOpacity="0.05" />
      <line x1="28" y1="18" x2="28" y2="38" />
      <path d="M 14 22 L 22 21" />
      <path d="M 14 26 L 24 25" />
      <path d="M 14 30 L 22 29" />
      <path d="M 34 21 L 42 22" />
      <path d="M 32 25 L 42 26" />
      <path d="M 34 29 L 42 30" />
    </svg>
  );
}

// Two overlapping bubbles — Conversation / chat
export function MarkConversation({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 8 16 Q 8 12 12 12 L 30 12 Q 34 12 34 16 L 34 26 Q 34 30 30 30 L 18 30 L 12 34 L 13 30 L 12 30 Q 8 30 8 26 Z" fill={color} fillOpacity="0.05" />
      <path d="M 22 30 L 22 22 Q 22 18 26 18 L 44 18 Q 48 18 48 22 L 48 34 Q 48 38 44 38 L 32 38 L 38 42 L 37 38 Q 22 38 22 34 Z" fill={color} fillOpacity="0.08" />
    </svg>
  );
}

// Clock — Time / schedule
export function MarkTime({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="28" cy="30" r="16" fill={color} fillOpacity="0.04" />
      <path d="M 28 22 L 28 30 L 34 33" />
      <path d="M 22 10 L 18 14" />
      <path d="M 34 10 L 38 14" />
      <circle cx="28" cy="30" r="1.5" fill={color} />
    </svg>
  );
}

// Open hand — Empty state, first run
export function MarkEmpty({ size = 56, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 56 56" fill="none" stroke={color} strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 12 30 Q 12 22 16 18 L 16 12 Q 16 9 19 9 Q 22 9 22 12 L 22 18 L 22 8 Q 22 5 25 5 Q 28 5 28 8 L 28 18 L 28 6 Q 28 3 31 3 Q 34 3 34 6 L 34 18 L 34 10 Q 34 7 37 7 Q 40 7 40 10 L 40 30 Q 40 42 28 46 Q 16 42 14 36 L 12 30 Z" fill={color} fillOpacity="0.04" />
    </svg>
  );
}

// Three walled chambers — Separate collectives / worlds
export function MarkWalls({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="6" y="20" width="14" height="32" rx="2" fill={color} fillOpacity="0.06" />
      <rect x="25" y="14" width="14" height="38" rx="2" fill={color} fillOpacity="0.08" />
      <rect x="44" y="22" width="14" height="30" rx="2" fill={color} fillOpacity="0.06" />
      <circle cx="13" cy="30" r="2" fill={color} />
      <circle cx="32" cy="24" r="2" fill={color} />
      <circle cx="51" cy="32" r="2" fill={color} />
      <line x1="2" y1="56" x2="62" y2="56" opacity="0.4" />
    </svg>
  );
}

// Central radiating spark — One engine
export function MarkEngine({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 32 12 L 38 32 L 32 52 L 26 32 Z" fill={color} fillOpacity="0.1" />
      <path d="M 12 32 L 32 38 L 52 32 L 32 26 Z" fill={color} fillOpacity="0.1" />
      <circle cx="32" cy="32" r="3" fill={color} />
      <path d="M 32 12 L 20 4" opacity="0.5" />
      <path d="M 32 12 L 44 4" opacity="0.5" />
      <path d="M 12 32 L 4 44" opacity="0.5" />
      <path d="M 52 32 L 60 44" opacity="0.5" />
      <path d="M 32 52 L 28 60" opacity="0.5" />
      <path d="M 32 52 L 36 60" opacity="0.5" />
    </svg>
  );
}

// Dashed line through three shapes — You are the thread
export function MarkThread({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="14" cy="20" r="9" fill={color} fillOpacity="0.06" />
      <rect x="24" y="26" width="16" height="16" rx="3" fill={color} fillOpacity="0.06" />
      <path d="M 50 50 L 56 38 L 44 38 Z" fill={color} fillOpacity="0.06" />
      <path d="M 6 12 Q 18 22 28 30 Q 38 38 52 48" strokeDasharray="2 2.5" />
      <circle cx="6" cy="12" r="2.5" fill={color} />
      <circle cx="52" cy="48" r="2.5" fill={color} />
    </svg>
  );
}

// Stacked receipts / ledger — Show the receipts
export function MarkReceipts({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 14 50 L 14 16 L 38 16 L 38 50 L 35 48 L 31 50 L 26 48 L 21 50 L 18 48 Z" fill={color} fillOpacity="0.06" />
      <path d="M 18 20 L 34 20" />
      <path d="M 18 26 L 30 26" />
      <path d="M 18 32 L 32 32" />
      <path d="M 42 50 L 42 22 L 54 22 L 54 50 L 51 48 L 47 50 Z" fill={color} fillOpacity="0.04" opacity="0.6" />
    </svg>
  );
}

// House with shield within — Sovereignty
export function MarkSovereign({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 10 30 L 32 12 L 54 30 L 54 52 L 10 52 Z" fill={color} fillOpacity="0.06" />
      <path d="M 26 52 L 26 38 L 38 38 L 38 52" />
      <path d="M 32 18 L 24 22 L 24 30 Q 24 34 32 36 Q 40 34 40 30 L 40 22 Z" fill={color} fillOpacity="0.10" />
    </svg>
  );
}

// Three figures holding hands — Family
export function MarkFamily({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="16" cy="22" r="6" fill={color} fillOpacity="0.08" />
      <circle cx="48" cy="22" r="6" fill={color} fillOpacity="0.08" />
      <circle cx="32" cy="32" r="5" fill={color} fillOpacity="0.08" />
      <path d="M 8 50 L 10 32 L 22 32 L 24 50" />
      <path d="M 40 50 L 42 32 L 54 32 L 56 50" />
      <path d="M 26 54 L 28 40 L 36 40 L 38 54" />
      <line x1="22" y1="40" x2="28" y2="42" strokeDasharray="1.5 1.5" opacity="0.5" />
      <line x1="36" y1="42" x2="42" y2="40" strokeDasharray="1.5 1.5" opacity="0.5" />
    </svg>
  );
}

// Lens with beam to three targets — Cross-life view
export function MarkLens({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="20" cy="32" r="10" fill={color} fillOpacity="0.06" />
      <circle cx="20" cy="32" r="4" fill={color} />
      <path d="M 30 32 L 56 22" opacity="0.4" />
      <path d="M 30 32 L 56 32" opacity="0.4" />
      <path d="M 30 32 L 56 42" opacity="0.4" />
      <circle cx="58" cy="22" r="2" fill={color} />
      <circle cx="58" cy="32" r="2" fill={color} />
      <circle cx="58" cy="42" r="2" fill={color} />
    </svg>
  );
}

// Plant / stem with leaves — Living understanding / growth
export function MarkGarden({ size = 64, color = 'currentColor' }: MarkProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M 32 52 L 32 18" />
      <path d="M 32 38 Q 24 36 18 28 Q 22 24 28 28 Q 30 34 32 38" fill={color} fillOpacity="0.06" />
      <path d="M 32 30 Q 40 28 46 20 Q 42 16 36 20 Q 34 26 32 30" fill={color} fillOpacity="0.06" />
      <path d="M 32 44 Q 26 42 22 36 Q 26 34 30 38 Q 31 42 32 44" fill={color} fillOpacity="0.04" />
      <line x1="20" y1="52" x2="44" y2="52" opacity="0.4" />
      <circle cx="32" cy="14" r="2.5" fill={color} />
    </svg>
  );
}
