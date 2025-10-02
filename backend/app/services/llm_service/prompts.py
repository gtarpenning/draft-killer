"""
Prompt management utilities for LLM service.

This module handles loading, formatting, and managing prompts for the
parlay analysis system. Prompts are stored as separate files for easy
iteration and version control.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


# Get the prompts directory
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    """
    Load a prompt from the prompts directory.
    
    Args:
        filename: Name of the prompt file (e.g., "system_prompt.txt")
        
    Returns:
        The prompt text as a string
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / filename
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    return prompt_path.read_text().strip()


def get_system_prompt() -> str:
    """
    Get the system prompt for parlay analysis.
    
    Returns:
        The system prompt text
    """
    return load_prompt("system_prompt.txt")


def create_user_prompt(parlay_description: str, enriched_odds: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a user prompt for parlay analysis.
    
    Args:
        parlay_description: User's description of their parlay
        enriched_odds: Optional enriched odds data from The Odds API
        
    Returns:
        Formatted prompt for the LLM
    """
    # Load the template
    template = load_prompt("user_prompt_template.txt")
    
    # Build the odds data section if available
    odds_data_section = ""
    if enriched_odds:
        odds_data_section = f"""
Current Market Data (from The Odds API):
{json.dumps(enriched_odds, indent=2)}

Use this live odds data to provide specific, data-driven analysis. Reference current odds, lines, and bookmakers in your analysis."""
    
    # Format the template
    prompt = template.format(
        parlay_description=parlay_description,
        odds_data_section=odds_data_section
    )
    
    return prompt


# For backward compatibility, expose SYSTEM_PROMPT as a module-level constant
SYSTEM_PROMPT = get_system_prompt()

