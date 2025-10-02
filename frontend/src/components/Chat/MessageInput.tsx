/**
 * Message input component.
 * 
 * Text area for user to type messages with send button.
 */

'use client';

import { useState, KeyboardEvent } from 'react';
import styles from './MessageInput.module.css';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Describe your parlay...',
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  
  function handleSend() {
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  }
  
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    // Send on Enter (but allow Shift+Enter for new lines)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }
  
  return (
    <div className={styles.container}>
      <textarea
        className={styles.input}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={3}
      />
      <button
        className={styles.button}
        onClick={handleSend}
        disabled={disabled || !message.trim()}
      >
        {disabled ? 'Analyzing...' : 'Analyze'}
      </button>
    </div>
  );
}

