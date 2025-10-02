/**
 * Registration form component.
 */

'use client';

import { useState, FormEvent } from 'react';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { isValidEmail, validatePassword } from '@/lib/utils';
import styles from './AuthForm.module.css';

export function RegisterForm() {
  const { register, loading, error, clearError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setValidationErrors([]);
    clearError();
    
    const errors: string[] = [];
    
    // Validation
    if (!email || !password || !confirmPassword) {
      errors.push('Please fill in all fields');
    }
    
    if (email && !isValidEmail(email)) {
      errors.push('Please enter a valid email address');
    }
    
    if (password !== confirmPassword) {
      errors.push('Passwords do not match');
    }
    
    if (password) {
      const passwordValidation = validatePassword(password);
      if (!passwordValidation.valid) {
        errors.push(...passwordValidation.errors);
      }
    }
    
    if (errors.length > 0) {
      setValidationErrors(errors);
      return;
    }
    
    try {
      await register({ email, password });
    } catch (err) {
      // Error is handled by the auth context
    }
  }
  
  const allErrors = [...validationErrors, ...(error ? [error] : [])];
  
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1 className={styles.title}>Draft Killer</h1>
        <p className={styles.subtitle}>Create your account</p>
        
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
              autoComplete="new-password"
            />
          </div>
          
          <div className={styles.field}>
            <label htmlFor="confirm-password" className={styles.label}>
              Confirm Password
            </label>
            <input
              id="confirm-password"
              type="password"
              className={styles.input}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />
          </div>
          
          {allErrors.length > 0 && (
            <div className={styles.errorList}>
              {allErrors.map((err, idx) => (
                <div key={idx} className={styles.error}>
                  {err}
                </div>
              ))}
            </div>
          )}
          
          <button
            type="submit"
            className={styles.button}
            disabled={loading}
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <p className={styles.footer}>
          Already have an account?{' '}
          <Link href="/login" className={styles.link}>
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}

