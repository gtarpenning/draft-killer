/**
 * Chat hook for managing chat state and streaming.
 * 
 * Provides functions for sending messages and managing conversation state.
 */

'use client';

import { useState } from 'react';
import type { Message, StreamChunk } from '@/types';
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
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  
  async function sendMessage(content: string) {
    if (!content.trim() || isStreaming) return;
    
    // Create new abort controller for this request
    const controller = new AbortController();
    setAbortController(controller);
    
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
        signal: controller.signal,
      })) {
        if (chunk.error) {
          throw new Error(chunk.error);
        }
        
        if (chunk.conversation_id && !currentConversationId) {
          setCurrentConversationId(chunk.conversation_id);
        }
        
        // Handle different event types
        if (chunk.event.type === 'content') {
          assistantContent += chunk.event.data;
          
          // Update the assistant message
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { ...msg, content: assistantContent }
                : msg
            )
          );
        } else if (chunk.event.type === 'tool_call') {
          // Add tool call indicator to message
          const toolName = chunk.event.data.tool_name;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessageId
                ? { 
                    ...msg, 
                    metadata: { 
                      ...msg.metadata, 
                      tool_calls: [...(msg.metadata?.tool_calls || []), toolName]
                    }
                  }
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
      
      // Check if this was an abort (cancellation)
      if (error instanceof Error && error.name === 'AbortError') {
        // Remove the incomplete assistant message
        setMessages(prev => prev.filter(msg => msg.id !== assistantMessageId));
        // Don't add error message for cancellation
        return;
      }
      
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
      setAbortController(null);
    }
  }
  
  function cancelMessage() {
    if (abortController) {
      abortController.abort();
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
    cancelMessage,
    clearMessages,
  };
}

