"""Main standup automation application."""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import Config
from .clients.jira_client import JiraClient
from .clients.github_client import GitHubClient
from .services.data_aggregator import DataAggregator
from .services.ai_service import AIService
from .utils.logger import setup_logger, get_logger


class StandupAutomation:
    """Main application class for standup automation."""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize the application.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.logger = setup_logger()
        
        # Initialize services
        self.jira_client = self._setup_jira_client()
        # GitHub client disabled - API doesn't support user event streams effectively
        self.github_client = None
        self.data_aggregator = DataAggregator(self.jira_client, self.github_client)
        self.ai_service = AIService(
            self.config.project_id,
            self.config.location,
            self.config.vertex_model
        )
    
    def _setup_jira_client(self) -> Optional[JiraClient]:
        """Set up Jira client if configured.
        
        Returns:
            JiraClient instance or None if not configured
        """
        try:
            return JiraClient(
                self.config.jira_domain,
                self.config.email,
                self.config.jira_api_key
            )
        except Exception as e:
            self.logger.warning(f"Failed to setup Jira client: {e}")
            return None
    
    def _setup_github_client(self) -> Optional[GitHubClient]:
        """Set up GitHub client if configured.
        
        Returns:
            GitHubClient instance or None if not configured
        """
        try:
            # Check if GitHub configuration exists
            if not (self.config.github_app_id and 
                    self.config.github_installation_id and 
                    self.config.private_key_path):
                self.logger.info("GitHub client not configured, skipping")
                return None
                
            return GitHubClient(
                self.config.github_app_id,
                self.config.github_installation_id,
                self.config.private_key_path
            )
        except Exception as e:
            self.logger.warning(f"Failed to setup GitHub client: {e}")
            return None
    
    def generate_standup_summary(self, use_structured: bool = True) -> Optional[str]:
        """Generate standup summary from all data sources.
        
        Args:
            use_structured: Whether to use structured data preprocessing
        
        Returns:
            Generated summary or None if failed
        """
        self.logger.info("Starting standup summary generation")
        
        try:
            # Aggregate all data with optional preprocessing
            if use_structured:
                self.logger.info("Using structured data preprocessing")
                combined_data = self.data_aggregator.aggregate_all_data_structured(
                    self.config.notes_directory,
                    self.config.git_author,
                    self.config.git_directories,
                    self.config.github_username
                )
            else:
                combined_data = self.data_aggregator.aggregate_all_data(
                    self.config.notes_directory,
                    self.config.git_author,
                    self.config.git_directories,
                    self.config.github_username
                )
            
            if not combined_data.strip():
                self.logger.warning("No data found to generate summary")
                return None
            
            # Log data size for debugging
            self.logger.info(f"Combined data size: {len(combined_data)} characters")
            
            # Generate summary using AI
            summary = self.ai_service.generate_standup_summary(
                combined_data,
                self.config.vertex_instruction
            )
            
            if summary:
                self.logger.info("Successfully generated standup summary")
                return summary
            else:
                self.logger.error("Failed to generate summary using AI service")
                return None
                
        except Exception as e:
            self.logger.error(f"Error generating standup summary: {e}")
            return None
    
    def save_summary(self, summary: str) -> bool:
        """Save summary to output file.
        
        Args:
            summary: Summary text to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            self.config.output_directory.mkdir(parents=True, exist_ok=True)
            
            output_path = self.config.output_directory / "summaries.txt"
            
            # Create date range string
            today = datetime.now()
            if today.weekday() == 0:  # Monday
                previous_workday = today - timedelta(days=3)
            else:
                previous_workday = today - timedelta(days=1)
            
            date_range = f"{previous_workday.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
            
            # Append summary to file
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(f"{date_range}: {summary}\n")
            
            self.logger.info(f"Summary saved to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving summary: {e}")
            return False
    
    def run(self) -> None:
        """Run the standup automation process."""
        self.logger.info("Starting standup automation")
        
        summary = self.generate_standup_summary()
        
        if summary:
            print(f"Generated Summary:\n{summary}")
            
            if self.save_summary(summary):
                self.logger.info("Standup automation completed successfully")
            else:
                self.logger.warning("Summary generated but failed to save")
        else:
            self.logger.error("Failed to generate standup summary")
            print("Failed to generate standup summary. Check logs for details.")


def main():
    """Main entry point."""
    app = StandupAutomation()
    app.run()


if __name__ == "__main__":
    main()