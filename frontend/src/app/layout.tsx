/**
 * Root layout component.
 * 
 * Wraps the entire application and provides:
 * - Global styles
 * - CSS variables from theme
 * - Authentication context
 */

import type { Metadata } from 'next';
import { AuthProvider } from '@/hooks/useAuth';
import { getCSSVariables } from '@/styles/theme';
import '@/styles/globals.css';

export const metadata: Metadata = {
  title: 'Draft Killer - Parlay Risk Analysis',
  description: 'Analyze the risks of your sports betting parlays with AI-powered insights',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <style dangerouslySetInnerHTML={{ __html: getCSSVariables() }} />
        <link
          href="https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

