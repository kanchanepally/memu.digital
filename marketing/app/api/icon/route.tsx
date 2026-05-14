import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const size = parseInt(searchParams.get('size') || '192', 10);

  return new ImageResponse(
    (
      <div
        style={{
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0d1117',
        }}
      >
        <svg width={size * 0.75} height={size * 0.75} viewBox="0 0 100 100">
          <defs>
            <linearGradient id="memuGradient1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#667eea" stopOpacity="1" />
              <stop offset="100%" stopColor="#764ba2" stopOpacity="1" />
            </linearGradient>
          </defs>
          <circle cx="40" cy="65" r="28" fill="url(#memuGradient1)" opacity="0.9" />
          <circle cx="60" cy="65" r="28" fill="url(#memuGradient1)" opacity="0.85" />
          <circle cx="50" cy="45" r="28" fill="url(#memuGradient1)" />
        </svg>
      </div>
    ),
    {
      width: size,
      height: size,
    }
  );
}
