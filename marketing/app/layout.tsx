import type { Metadata } from "next";
import "./globals.css";
import { Masthead } from "@/components/Masthead";
import { Footer } from "@/components/Footer";

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
    <html lang="en">
      <body>
        <Masthead />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}
