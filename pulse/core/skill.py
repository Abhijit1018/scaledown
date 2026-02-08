"""
Pulse Skill Interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class Skill(ABC):
    """
    Abstract base class for all Pulse skills (tools).
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the skill."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the skill does."""
        pass
        
    @property
    def commands(self) -> List[str]:
        """List of keywords or regex patterns that trigger this skill."""
        return []

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute the skill logic.
        
        Args:
            context: Dictionary containing 'user_input' and other metadata.
            
        Returns:
            A string response to be spoken/shown to the user.
        """
        pass
