"""Vertex AI service for generating summaries and content."""

import vertexai
from vertexai.generative_models import GenerativeModel
from typing import Optional


class AIService:
    """Service for interacting with Vertex AI."""
    
    def __init__(self, project_id: str, location: str, model_name: str = "gemini-2.5-flash"):
        """Initialize AI service.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
            model_name: Vertex AI model name
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
    
    def generate_summary(self, content: str, instruction: str) -> Optional[str]:
        """Generate a summary using Vertex AI.
        
        Args:
            content: Content to summarize
            instruction: Instruction/prompt for the AI
            
        Returns:
            Generated summary or None if failed
        """
        try:
            full_prompt = f"{instruction}\n\n{content}"
            response = self.model.generate_content(full_prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error during Vertex AI summarization: {e}")
            return None
    
    def generate_standup_summary(self, content: str, instruction: str) -> Optional[str]:
        """Generate a standup-specific summary.
        
        Args:
            content: Content to summarize for standup
            instruction: Standup-specific instruction
            
        Returns:
            Generated standup summary or None if failed
        """
        return self.generate_summary(content, instruction)
    
    def test_connection(self) -> bool:
        """Test the connection to Vertex AI.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.model.generate_content("Test connection")
            return response is not None
        except Exception:
            return False