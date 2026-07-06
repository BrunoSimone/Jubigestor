import type { Metadata } from "next";
import { Atkinson_Hyperlegible } from "next/font/google";
import "./globals.css";

// Atkinson Hyperlegible: a typeface designed for low vision. Key for our audience.
const atkinson = Atkinson_Hyperlegible({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-atkinson",
});

export const metadata: Metadata = {
  title: "JubiGestor",
  description:
    "Asistente orientativo para trámites jubilatorios argentinos (ANSES).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`${atkinson.variable} h-full antialiased`}>
      <body className="min-h-full">{children}</body>
    </html>
  );
}
