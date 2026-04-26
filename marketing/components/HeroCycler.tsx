"use client";
import { useState, useEffect } from 'react';

const phrases = [
  "Your personal Chief of Staff.",
  "Your family's Chief of Staff.",
  "Compound knowledge that never forgets.",
  "Privately anonymous by architecture.",
  "A morning briefing before you wake.",
  "The AI that acts while you sleep.",
];

export const HeroCycler = () => {
  const [index, setIndex] = useState(0);
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setVisible(false);
      setTimeout(() => {
        setIndex(i => (i + 1) % phrases.length);
        setVisible(true);
      }, 380);
    }, 3200);
    return () => clearInterval(timer);
  }, []);

  return (
    <span
      style={{
        display: 'block',
        opacity: visible ? 1 : 0,
        transition: 'opacity 0.38s ease',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        minHeight: '1.5em',
        fontWeight: 600,
      }}
    >
      {phrases[index]}
    </span>
  );
};
