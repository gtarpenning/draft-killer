/**
 * Main chat interface component.
 * 
 * Combines message list and input into a complete chat UI.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useChat } from '@/hooks/useChat';
import { useAuth } from '@/hooks/useAuth';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { SportSelector, DEFAULT_SPORT, type Sport } from './SportSelector';
import styles from './ChatInterface.module.css';

export function ChatInterface() {
  const [selectedSport, setSelectedSport] = useState<Sport>(DEFAULT_SPORT);
  const { messages, isStreaming, sendMessage } = useChat({ sport: selectedSport.id });
  const { user, logout } = useAuth();
  const router = useRouter();
  
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1 className={styles.title}>Draft Killer</h1>
        <p className={styles.subtitle}>Parlay Risk Analysis</p>
        
        {user ? (
          <div className={styles.userBadge}>
            <span className={styles.userEmail}>{user.email}</span>
            <button onClick={logout} className={styles.logoutButton}>
              Logout
            </button>
          </div>
        ) : (
          <div className={styles.userBadge}>
            <button 
              onClick={() => router.push('/login')} 
              className={styles.loginButton}
            >
              Sign in to save
            </button>
          </div>
        )}
      </header>
      
      <div className={styles.selectorBar}>
        <SportSelector 
          selectedSport={selectedSport}
          onSportChange={setSelectedSport}
        />
      </div>
      
      <MessageList messages={messages} isStreaming={isStreaming} />
      
      <MessageInput
        onSend={sendMessage}
        disabled={isStreaming}
      />
    </div>
  );
}

