"""Data aggregation service for collecting information from multiple sources."""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..clients.jira_client import JiraClient
from ..clients.github_client import GitHubClient
from .data_preprocessor import DataPreprocessor


class DataAggregator:
    """Service for aggregating data from multiple sources."""
    
    def __init__(self, jira_client: Optional[JiraClient] = None, 
                 github_client: Optional[GitHubClient] = None):
        """Initialize data aggregator.
        
        Args:
            jira_client: Optional Jira client instance
            github_client: Optional GitHub client instance
        """
        self.jira_client = jira_client
        self.github_client = github_client
        self.preprocessor = DataPreprocessor()
    
    def get_notes_content(self, notes_directory: Path) -> str:
        """Get combined notes content for today and previous workday.
        
        Args:
            notes_directory: Path to the notes directory
            
        Returns:
            Combined notes content
        """
        today = datetime.now()
        if today.weekday() == 0:  # Monday
            previous_workday = today - timedelta(days=3)  # Friday
        else:
            previous_workday = today - timedelta(days=1)  # Yesterday
        
        combined_content = ""
        
        # Read today's notes
        today_path = self._get_note_path(notes_directory, today)
        if today_path.exists():
            combined_content += f"Notes for {today.strftime('%Y-%m-%d')}:\n"
            combined_content += today_path.read_text(encoding="utf-8") + "\n\n"
        
        # Read previous workday notes
        previous_path = self._get_note_path(notes_directory, previous_workday)
        if previous_path.exists():
            combined_content += f"Notes for {previous_workday.strftime('%Y-%m-%d')}:\n"
            combined_content += previous_path.read_text(encoding="utf-8") + "\n\n"
        
        return combined_content
    
    def _get_note_path(self, base_dir: Path, date: datetime) -> Path:
        """Get the path to a note file for a specific date.
        
        Args:
            base_dir: Base directory for notes
            date: Date for the note
            
        Returns:
            Path to the note file
        """
        return base_dir / date.strftime("%Y") / date.strftime("%m") / f"{date.strftime('%d')}.txt"
    
    def get_git_history(self, author: str, directories: List[str], since: str = "yesterday") -> str:
        """Get Git commit history from multiple repositories.
        
        Args:
            author: Git author name to filter by
            directories: List of Git repository directories
            since: Time period to look back (e.g., 'yesterday', '2 days ago')
            
        Returns:
            Formatted Git history string
        """
        if not directories:
            return "No Git directories configured."
        
        history_info = "Include this Git history:\n"
        
        git_cmd = [
            "git", "log", "--all", "--reverse",
            f"--author={author}",
            f"--since={since}",
            "--pretty=format:%h %ad | %s [%d] (%an)",
            "--date=short"
        ]
        
        for directory in directories:
            if not os.path.isdir(directory):
                continue
            
            try:
                result = subprocess.run(
                    git_cmd,
                    cwd=directory,
                    text=True,
                    capture_output=True,
                    check=True
                )
                
                if result.stdout:
                    history_info += f"\nFolder: {directory}\n"
                    for commit in result.stdout.strip().split('\n'):
                        history_info += f"- {commit}\n"
            
            except subprocess.CalledProcessError:
                continue
        
        return history_info
    
    def get_timewarrior_summary(self) -> str:
        """Get Timewarrior summary for yesterday.
        
        Returns:
            Timewarrior summary string
        """
        try:
            result = subprocess.run(
                ["timew", "summary", ":yesterday"],
                text=True,
                capture_output=True,
                check=True
            )
            return f"Timewarrior Summary for yesterday:\n{result.stdout.strip()}"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "No timewarrior summary available."
    
    def get_jira_tickets(self) -> str:
        """Get formatted Jira tickets.
        
        Returns:
            Formatted Jira tickets string
        """
        if not self.jira_client:
            return "Jira client not configured."
        
        try:
            tickets = self.jira_client.get_my_active_tickets()
            return self.jira_client.format_tickets_for_summary(tickets)
        except Exception as e:
            return f"Error fetching Jira tickets: {e}"
    
    def get_github_events(self, username: str, org: Optional[str] = None) -> str:
        """Get formatted GitHub events.
        
        Args:
            username: GitHub username
            org: Optional organization name
            
        Returns:
            Formatted GitHub events string
        """
        if not self.github_client:
            return "GitHub client not configured."
        
        try:
            events = self.github_client.get_user_events(username, org)
            recent_events = self.github_client.filter_recent_events(events)
            return self.github_client.format_events_for_summary(recent_events)
        except Exception as e:
            return f"Error fetching GitHub events: {e}"
    
    def get_date_range(self) -> Tuple[datetime, datetime]:
        """Get the date range for data collection (previous workday to today).
        
        Returns:
            Tuple of (start_date, end_date)
        """
        today = datetime.now()
        if today.weekday() == 0:  # Monday
            previous_workday = today - timedelta(days=3)  # Friday
        else:
            previous_workday = today - timedelta(days=1)  # Yesterday
        return (previous_workday, today)
    
    def aggregate_all_data(
        self,
        notes_directory: Path,
        git_author: str,
        git_directories: List[str],
        github_username: Optional[str] = None,
        github_org: Optional[str] = None
    ) -> str:
        """Aggregate all available data sources.
        
        Args:
            notes_directory: Path to notes directory
            git_author: Git author name
            git_directories: List of Git directories
            github_username: Optional GitHub username
            github_org: Optional GitHub organization
            
        Returns:
            Combined data string
        """
        combined_data = ""
        
        # Add notes
        notes = self.get_notes_content(notes_directory)
        if notes:
            combined_data += notes
        
        # Add Jira tickets
        jira_info = self.get_jira_tickets()
        combined_data += jira_info + "\n"
        
        # Add Git history
        git_history = self.get_git_history(git_author, git_directories)
        combined_data += git_history + "\n"
        
        # Add Timewarrior summary
        timew_summary = self.get_timewarrior_summary()
        combined_data += timew_summary + "\n"
        
        # Add GitHub events if configured
        if github_username and self.github_client:
            github_events = self.get_github_events(github_username, github_org)
            combined_data += github_events + "\n"
        
        return combined_data
    
    def aggregate_all_data_structured(
        self,
        notes_directory: Path,
        git_author: str,
        git_directories: List[str],
        github_username: Optional[str] = None,
        github_org: Optional[str] = None
    ) -> str:
        """Aggregate and structure all data sources for better AI comprehension.
        
        Args:
            notes_directory: Path to notes directory
            git_author: Git author name
            git_directories: List of Git directories
            github_username: Optional GitHub username
            github_org: Optional GitHub organization
            
        Returns:
            Structured and preprocessed data string
        """
        # Get raw data from all sources
        notes = self.get_notes_content(notes_directory)
        git_history = self.get_git_history(git_author, git_directories)
        timew_summary = self.get_timewarrior_summary()
        
        # Get Jira tickets as structured data
        jira_tickets = []
        if self.jira_client:
            try:
                jira_tickets = self.jira_client.get_my_active_tickets()
            except Exception:
                pass
        
        # Correlate ticket data across sources
        correlated_data = self.preprocessor.correlate_ticket_data(
            notes,
            jira_tickets,
            git_history,
            timew_summary
        )
        
        # Get date range
        date_range = self.get_date_range()
        
        # Structure the data for AI
        structured_data = self.preprocessor.structure_for_ai(
            correlated_data,
            notes,
            date_range
        )
        
        # Add raw data sections that weren't correlated
        structured_data += "\n\n=== ADDITIONAL DATA ===\n"
        
        # Add Git history summary
        if git_history and "No Git directories configured" not in git_history:
            structured_data += "\nGIT ACTIVITY:\n"
            # Deduplicate git history
            structured_data += self.preprocessor.deduplicate_content(git_history)
        
        # Add Timewarrior summary
        if timew_summary and "No timewarrior summary" not in timew_summary:
            structured_data += "\n\nTIME TRACKING:\n"
            structured_data += timew_summary
        
        return structured_data