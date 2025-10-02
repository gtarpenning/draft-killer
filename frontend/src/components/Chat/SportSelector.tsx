/**
 * Sport selector component with typing/filtering support.
 * 
 * Allows users to select a sport for their parlay analysis.
 */

'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import styles from './SportSelector.module.css';

export interface Sport {
  id: string;
  name: string;
  icon: string;
}

// Top 10 sports hardcoded
const SPORTS: Sport[] = [
  { id: 'americanfootball_nfl', name: 'NFL', icon: '🏈' },
  { id: 'basketball_nba', name: 'NBA', icon: '🏀' },
  { id: 'baseball_mlb', name: 'MLB', icon: '⚾' },
  { id: 'icehockey_nhl', name: 'NHL', icon: '🏒' },
  { id: 'soccer_epl', name: 'Premier League', icon: '⚽' },
  { id: 'soccer_uefa_champs_league', name: 'Champions League', icon: '⚽' },
  { id: 'basketball_ncaab', name: 'College Basketball', icon: '🏀' },
  { id: 'americanfootball_ncaaf', name: 'College Football', icon: '🏈' },
  { id: 'mma_mixed_martial_arts', name: 'MMA/UFC', icon: '🥊' },
  { id: 'boxing_boxing', name: 'Boxing', icon: '🥊' },
];

interface SportSelectorProps {
  selectedSport: Sport;
  onSportChange: (sport: Sport) => void;
}

export function SportSelector({ selectedSport, onSportChange }: SportSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Filter sports based on search term
  const filteredSports = useMemo(() => {
    if (!searchTerm.trim()) return SPORTS;
    
    const term = searchTerm.toLowerCase();
    return SPORTS.filter(sport => 
      sport.name.toLowerCase().includes(term) ||
      sport.id.toLowerCase().includes(term)
    );
  }, [searchTerm]);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setSearchTerm('');
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Focus input when dropdown opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSelectSport = (sport: Sport) => {
    onSportChange(sport);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && filteredSports.length > 0) {
      handleSelectSport(filteredSports[0]);
    } else if (e.key === 'Escape') {
      setIsOpen(false);
      setSearchTerm('');
    }
  };

  return (
    <div className={styles.container} ref={dropdownRef}>
      <button
        type="button"
        className={styles.selector}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
      >
        <span className={styles.selectedValue}>
          <span className={styles.icon}>{selectedSport.icon}</span>
          <span className={styles.name}>{selectedSport.name}</span>
        </span>
        <span className={styles.arrow}>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <input
            ref={inputRef}
            type="text"
            className={styles.search}
            placeholder="Search sports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          
          <ul className={styles.list} role="listbox">
            {filteredSports.length > 0 ? (
              filteredSports.map((sport) => (
                <li
                  key={sport.id}
                  className={`${styles.item} ${sport.id === selectedSport.id ? styles.active : ''}`}
                  onClick={() => handleSelectSport(sport)}
                  role="option"
                  aria-selected={sport.id === selectedSport.id}
                >
                  <span className={styles.icon}>{sport.icon}</span>
                  <span className={styles.name}>{sport.name}</span>
                </li>
              ))
            ) : (
              <li className={styles.noResults}>No sports found</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}

// Export the default sport
export const DEFAULT_SPORT: Sport = SPORTS[0]; // NFL
export { SPORTS };

