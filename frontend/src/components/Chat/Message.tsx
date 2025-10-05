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

function ToolCallIndicator({ toolName }: { toolName: string }) {
  return (
    <div className={styles.toolCall}>
      <span className={styles.toolIcon}>🔧</span>
      <span className={styles.toolText}>Using {toolName}</span>
    </div>
  );
}

export function Message({ message, showTypewriter = false }: MessageProps) {
  const isUser = message.role === 'user';
  const toolCalls = message.metadata?.tool_calls || [];
  
  return (
    <div className={`${styles.message} ${isUser ? styles.user : styles.assistant}`}>
      <div className={styles.role}>
        {isUser ? 'You' : 'Draft Killer'}
      </div>
      
      {toolCalls.length > 0 && (
        <div className={styles.toolCalls}>
          {toolCalls.map((toolName: string, index: number) => (
            <ToolCallIndicator key={index} toolName={toolName} />
          ))}
        </div>
      )}
      
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

