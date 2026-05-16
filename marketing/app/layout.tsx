import type { Metadata } from "next";
import { Inter, Newsreader, JetBrains_Mono } from 'next/font/google';
import "./globals.css";
import { Masthead } from "@/components/Masthead";
import { Footer } from "@/components/Footer";
import Script from "next/script";
import { THEME_INIT_SCRIPT } from "@/components/ThemeToggle";

const inter = Inter({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-inter',
});

const newsreader = Newsreader({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  style: ['normal', 'italic'],
  variable: '--font-newsreader',
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600'],
  variable: '--font-jetbrains',
});

export const metadata: Metadata = {
  title: "Memu | Your family, your network.",
  description: "The operating system for your family's intelligence. Protect your data with an anonymous digital twin.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${newsreader.variable} ${jetbrains.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: THEME_INIT_SCRIPT }} />
      </head>
      <body>
        <Masthead />
        <main>{children}</main>
        <Footer />
        <Script id="sw" strategy="afterInteractive">
          {`
            if ('serviceWorker' in navigator) {
              window.addEventListener('load', function() {
                navigator.serviceWorker.register('/sw.js').catch(function(err) {
                  console.log('Service Worker registration failed: ', err);
                });
              });
            }
          `}
        </Script>
      </body>
    </html>
  );
}
