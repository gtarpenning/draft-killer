/**
 * Main chat page.
 * 
 * Default page - accessible without authentication.
 */

'use client';

import { ChatInterface } from '@/components/Chat/ChatInterface';

export default function HomePage() {
  return <ChatInterface />;
}

