/**
 * TypeScript type definitions for the application.
 * 
 * These types ensure type safety across the frontend and match
 * the backend API schemas.
 */

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
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
  username: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface StreamEvent {
  type: 'tool_call' | 'tool_output' | 'content' | 'agent_update' | 'error' | 'done';
  data: any;
}

export interface StreamChunk {
  event: StreamEvent;
  done: boolean;
  conversation_id?: string;
  error?: string;
}

export interface ToolCall {
  tool_name: string;
  arguments: string;
}

export interface ToolOutput {
  tool_name: string;
  output: string;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export interface TableInfo {
  name: string;
  row_count: number;
}

export interface TableData {
  table_name: string;
  columns: string[];
  rows: Record<string, any>[];
  total_rows: number;
}

export interface UsageStats {
  type: 'authenticated' | 'anonymous';
  user_id?: string;
  email?: string;
  is_active?: boolean;
  session_id?: string;
  request_count: number;
  last_request?: string;
  user_agent?: string;
}


