/**
 * TypeScript type definitions for the application.
 * 
 * These types ensure type safety across the frontend and match
 * the backend API schemas.
 */

export interface User {
  id: string;
  email: string;
  created_at: string;
  last_login: string | null;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: Record<string, any>;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  messages: Message[];
}

export interface ConversationListItem {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface StreamChunk {
  content: string;
  done: boolean;
  conversation_id?: string;
  error?: string;
}

export interface ApiError {
  detail: string;
  code?: string;
}


