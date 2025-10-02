/**
 * Centralized theme configuration.
 * 
 * All visual styling is defined here for easy modification.
 * Change colors, fonts, spacing, or animations by editing this file.
 * No need to hunt through component files for styling.
 */

export const theme = {
  colors: {
    // Main colors
    background: '#FFFFFF',
    text: '#000000',
    textSecondary: '#666666',
    
    // Input styling
    inputBackground: '#F5F5F5',
    inputBorder: '#E0E0E0',
    inputBorderFocus: '#333333',
    
    // Accents
    accent: '#333333',
    error: '#DC2626',
    success: '#16A34A',
    
    // Message bubbles (if used)
    userMessage: '#F5F5F5',
    assistantMessage: '#FFFFFF',
  },
  
  fonts: {
    // Primary font family - change this to switch entire aesthetic
    // Options: 'Courier Prime', 'Courier New', 'Crimson Text', 'Georgia', etc.
    body: "'Courier Prime', 'Courier New', monospace",
    
    size: {
      small: '14px',
      base: '16px',
      large: '18px',
      xlarge: '20px',
    },
    
    weight: {
      normal: 400,
      medium: 500,
      bold: 700,
    },
    
    lineHeight: '1.6',
  },
  
  spacing: {
    // Page-level spacing
    pageHorizontal: '2rem',
    pageVertical: '2rem',
    
    // Component spacing
    messageGap: '1.5rem',
    inputPadding: '1rem',
    buttonPadding: '0.75rem 1.5rem',
    
    // Container spacing
    maxWidth: '800px',
  },
  
  animation: {
    // Typewriter effect speed (milliseconds per character)
    typewriterSpeed: 10,
    
    // Transition speeds
    fast: '0.15s',
    normal: '0.3s',
    slow: '0.5s',
    
    // Easing functions
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
  
  layout: {
    maxWidth: '800px',
    inputHeight: '60px',
    headerHeight: '60px',
    
    // Border radius (0 for sharp corners, increase for rounded)
    borderRadius: '4px',
    borderRadiusLarge: '8px',
  },
  
  shadows: {
    none: 'none',
    small: '0 1px 3px rgba(0, 0, 0, 0.1)',
    medium: '0 4px 6px rgba(0, 0, 0, 0.1)',
    large: '0 10px 15px rgba(0, 0, 0, 0.1)',
  },
} as const;

export type Theme = typeof theme;

/**
 * CSS Variables version of the theme for use in CSS files.
 * 
 * Usage in CSS:
 *   color: var(--color-text);
 *   font-family: var(--font-body);
 */
export const getCSSVariables = () => {
  return `
    :root {
      /* Colors */
      --color-background: ${theme.colors.background};
      --color-text: ${theme.colors.text};
      --color-text-secondary: ${theme.colors.textSecondary};
      --color-input-background: ${theme.colors.inputBackground};
      --color-input-border: ${theme.colors.inputBorder};
      --color-input-border-focus: ${theme.colors.inputBorderFocus};
      --color-accent: ${theme.colors.accent};
      --color-error: ${theme.colors.error};
      --color-success: ${theme.colors.success};
      
      /* Fonts */
      --font-body: ${theme.fonts.body};
      --font-size-small: ${theme.fonts.size.small};
      --font-size-base: ${theme.fonts.size.base};
      --font-size-large: ${theme.fonts.size.large};
      --font-size-xlarge: ${theme.fonts.size.xlarge};
      --font-line-height: ${theme.fonts.lineHeight};
      
      /* Spacing */
      --spacing-page-horizontal: ${theme.spacing.pageHorizontal};
      --spacing-page-vertical: ${theme.spacing.pageVertical};
      --spacing-message-gap: ${theme.spacing.messageGap};
      
      /* Layout */
      --layout-max-width: ${theme.layout.maxWidth};
      --layout-border-radius: ${theme.layout.borderRadius};
      
      /* Animation */
      --animation-speed-normal: ${theme.animation.normal};
    }
  `;
};


