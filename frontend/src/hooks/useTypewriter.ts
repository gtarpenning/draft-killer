/**
 * Typewriter effect hook.
 * 
 * Animates text character-by-character for a typewriter effect.
 * Used for displaying assistant responses.
 */

'use client';

import { useState, useEffect, useRef } from 'react';
import { theme } from '@/styles/theme';

interface UseTypewriterOptions {
  speed?: number; // milliseconds per character
  enabled?: boolean; // whether to apply the effect
}

export function useTypewriter(
  text: string,
  options: UseTypewriterOptions = {}
) {
  const { speed = theme.animation.typewriterSpeed, enabled = true } = options;
  
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();
  
  useEffect(() => {
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    // If effect is disabled, show full text immediately
    if (!enabled) {
      setDisplayedText(text);
      setIsTyping(false);
      return;
    }
    
    // If text is empty, reset
    if (!text) {
      setDisplayedText('');
      setIsTyping(false);
      return;
    }
    
    // If text is shorter than displayed (e.g., cleared), reset
    if (text.length < displayedText.length) {
      setDisplayedText('');
    }
    
    // If we're already showing all the text, nothing to do
    if (displayedText === text) {
      setIsTyping(false);
      return;
    }
    
    // Start typing animation
    setIsTyping(true);
    
    const currentLength = displayedText.length;
    const nextChar = text[currentLength];
    
    if (nextChar) {
      timeoutRef.current = setTimeout(() => {
        setDisplayedText(text.slice(0, currentLength + 1));
      }, speed);
    } else {
      setIsTyping(false);
    }
    
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [text, displayedText, speed, enabled]);
  
  return {
    displayedText,
    isTyping,
  };
}

