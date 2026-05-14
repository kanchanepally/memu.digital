"use client";
import { useState, useEffect } from 'react';

const phrases = [
  "for your family",
  "for your work",
  "for your ventures",
  "for your research",
  "for your thinking",
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
      }, 500);
    }, 3000);
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
