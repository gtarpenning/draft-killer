/**
 * Message list component.
 * 
 * Displays all messages in a conversation with auto-scrolling.
 */

'use client';

import { useEffect, useRef } from 'react';
import type { Message as MessageType } from '@/types';
import { Message } from './Message';
import styles from './MessageList.module.css';

interface MessageListProps {
  messages: MessageType[];
  isStreaming?: boolean;
}

export function MessageList({ messages, isStreaming = false }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  if (messages.length === 0) {
    return (
      <div className={styles.empty}>
        <p>Describe your parlay below to get started.</p>
        <p className={styles.hint}>
          Include details about the teams, betting lines, and odds for the best analysis.
        </p>
      </div>
    );
  }
  
  return (
    <div className={styles.container}>
      <div className={styles.messages}>
        {messages.map((message, index) => {
          // Only apply typewriter to the last assistant message while streaming
          const isLastMessage = index === messages.length - 1;
          const showTypewriter = isLastMessage && message.role === 'assistant';
          
          return (
            <Message
              key={message.id}
              message={message}
              showTypewriter={showTypewriter}
            />
          );
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

