import type { Metadata } from "next";
import { JetBrains_Mono, Schibsted_Grotesk, Syne } from "next/font/google";
import { SITE } from "@/lib/site";
import { buildCopy } from "@/lib/copy";
import run from "@/data/run.json";
import "./globals.css";

const display = Syne({
  subsets: ["latin"],
  weight: ["600", "700", "800"],
  variable: "--font-display",
  display: "swap",
});

const body = Schibsted_Grotesk({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

// Siden er tospråklig og bytter uten omlasting, så <html lang> står på norsk
// som standard og settes om av klienten når man bytter. Metadataen under er
// engelsk, for det er den som havner i delinger og søk utenfor Norge.
const COPY = buildCopy(run);
export const metadata: Metadata = {
  metadataBase: new URL(SITE.url),
  title: COPY.en.meta.title,
  description: COPY.en.meta.description,
  alternates: { canonical: SITE.url },
  openGraph: {
    type: "website",
    url: SITE.url,
    title: COPY.en.meta.title,
    description: COPY.en.meta.description,
    siteName: SITE.name,
  },
  twitter: {
    card: "summary_large_image",
    title: COPY.en.meta.title,
    description: COPY.en.meta.description,
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="no" className={`${display.variable} ${body.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
