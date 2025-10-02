/**
 * Login form component.
 */

'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { isValidEmail } from '@/lib/utils';
import styles from './AuthForm.module.css';

export function LoginForm() {
  const { login, loading, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [validationError, setValidationError] = useState('');
  
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setValidationError('');
    clearError();
    
    // Validation
    if (!email || !password) {
      setValidationError('Please fill in all fields');
      return;
    }
    
    if (!isValidEmail(email)) {
      setValidationError('Please enter a valid email address');
      return;
    }
    
    try {
      await login({ email, password });
    } catch (err) {
      // Error is handled by the auth context
    }
  }
  
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Draft Killer</h1>
        <p className={styles.subtitle}>Parlay Risk Analysis</p>
        
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="email" className={styles.label}>
              Email
            </label>
            <input
              id="email"
              type="email"
              className={styles.input}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
            />
          </div>
          
          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              Password
            </label>
            <input
              id="password"
              type="password"
              className={styles.input}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="current-password"
            />
          </div>
          
          {(error || validationError) && (
            <div className={styles.error}>
              {error || validationError}
            </div>
          )}
          
          <button
            type="submit"
            className={styles.button}
            disabled={loading}
          >
            {loading ? 'Logging in...' : 'Log In'}
          </button>
        </form>
        
        <p className={styles.footer}>
          Don't have an account?{' '}
          <Link href="/register" className={styles.link}>
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}

