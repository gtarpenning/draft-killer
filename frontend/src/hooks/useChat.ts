/**
 * Chat hook for managing chat state and streaming.
 * 
 * Provides functions for sending messages and managing conversation state.
 */

'use client';

import { useState } from 'react';
import type { Message } from '@/types';
import { streamChat } from '@/lib/api';

interface UseChatOptions {
  conversationId?: string;
  sport?: string;
  onError?: (error: Error) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<string | undefined>(
    options.conversationId
  );
  
  async function sendMessage(content: string) {
    if (!content.trim() || isStreaming) return;
    
    // Add user message immediately
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);
    
    // Prepare assistant message that will be updated as we stream
    const assistantMessageId = crypto.randomUUID();
    let assistantContent = '';
    
    const assistantMessage: Message = {
      id: assistantMessageId,
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    
    try {
      // Prepare the message with sport context if available
      const messageWithContext = options.sport 
        ? `[Sport: ${options.sport}] ${content}`
        : content;
      
      // Stream the response
      for await (const chunk of streamChat({
        message: messageWithContext,
        conversation_id: currentConversationId,
      })) {
        if (chunk.error) {
          throw new Error(chunk.error);
        }
        
        if (chunk.conversation_id && !currentConversationId) {
          setCurrentConversationId(chunk.conversation_id);
        }
        
        if (chunk.content) {
          assistantContent += chunk.content;
          
          // Update the assistant message
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: assistantContent }
                : msg
            )
          );
        }
        
        if (chunk.done) {
          break;
        }
      }
    } catch (error) {
      console.error('Error streaming message:', error);
      
      // Remove the incomplete assistant message
      setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
      
      // Add error message
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        created_at: new Date().toISOString(),
        metadata: { error: true },
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      if (options.onError && error instanceof Error) {
        options.onError(error);
      }
    } finally {
      setIsStreaming(false);
    }
  }
  
  function clearMessages() {
    setMessages([]);
    setCurrentConversationId(undefined);
  }
  
  return {
    messages,
    isStreaming,
    conversationId: currentConversationId,
    sendMessage,
    clearMessages,
  };
}

