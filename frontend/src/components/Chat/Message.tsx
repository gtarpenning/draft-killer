/**
 * Message component for displaying individual chat messages.
 */

'use client';

import type { Message as MessageType } from '@/types';
import { TypewriterText } from './TypewriterText';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import styles from './Message.module.css';
import 'katex/dist/katex.min.css';

interface MessageProps {
  message: MessageType;
  showTypewriter?: boolean;
}

export function Message({ message, showTypewriter = false }: MessageProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`${styles.message} ${isUser ? styles.user : styles.assistant}`}>
      <div className={styles.role}>
        {isUser ? 'You' : 'Draft Killer'}
      </div>
      <div className={styles.content}>
        {showTypewriter && !isUser ? (
          <TypewriterText text={message.content} />
        ) : (
          <div className={styles.text}>
            <ReactMarkdown
              remarkPlugins={[remarkMath, remarkGfm]}
              rehypePlugins={[rehypeKatex]}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

