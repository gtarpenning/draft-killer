/**
 * Typewriter text component.
 * 
 * Displays text with a typewriter animation effect.
 */

'use client';

import { useTypewriter } from '@/hooks/useTypewriter';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import styles from './TypewriterText.module.css';
import 'katex/dist/katex.min.css';

interface TypewriterTextProps {
  text: string;
}

export function TypewriterText({ text }: TypewriterTextProps) {
  const { displayedText, isTyping } = useTypewriter(text);
  
  return (
    <div className={styles.container}>
      <span className={styles.text}>
        <ReactMarkdown
          remarkPlugins={[remarkMath, remarkGfm]}
          rehypePlugins={[rehypeKatex]}
        >
          {displayedText}
        </ReactMarkdown>
      </span>
      {isTyping && <span className={styles.cursor}>│</span>}
    </div>
  );
}

