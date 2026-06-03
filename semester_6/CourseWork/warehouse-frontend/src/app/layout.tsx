import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AuthShell } from "@/components/auth-shell";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Warehouse Frontend",
  description: "Warehouse operations and reports UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <AuthShell>{children}</AuthShell>
      </body>
    </html>
  );
}
