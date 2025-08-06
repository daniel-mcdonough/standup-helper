"""GitHub API client for fetching events and repository information."""

import jwt
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class GitHubClient:
    """Client for interacting with GitHub API using GitHub App authentication."""
    
    def __init__(self, app_id: str, installation_id: str, private_key_path: str):
        """Initialize GitHub client.
        
        Args:
            app_id: GitHub App ID
            installation_id: GitHub App Installation ID
            private_key_path: Path to the private key file
        """
        self.app_id = app_id
        self.installation_id = installation_id
        self.private_key_path = private_key_path
        self._access_token = None
        self._token_expires_at = None
    
    def _generate_jwt(self) -> str:
        """Generate a JWT for GitHub App authentication.
        
        Returns:
            JWT token string
        """
        with open(self.private_key_path, "r") as key_file:
            private_key = key_file.read()
        
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + (10 * 60),  # 10 minutes
            "iss": self.app_id
        }
        
        return jwt.encode(payload, private_key, algorithm="RS256")
    
    def _get_access_token(self) -> Optional[str]:
        """Get installation access token.
        
        Returns:
            Access token string or None if failed
        """
        # Check if we have a valid token
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at - timedelta(minutes=5)):
            return self._access_token
        
        jwt_token = self._generate_jwt()
        url = f"https://api.github.com/app/installations/{self.installation_id}/access_tokens"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github+json"
        }
        
        response = requests.post(url, headers=headers)
        if response.status_code == 201:
            data = response.json()
            self._access_token = data["token"]
            # GitHub tokens expire in 1 hour
            self._token_expires_at = datetime.now() + timedelta(hours=1)
            return self._access_token
        else:
            print(f"Failed to get access token: {response.status_code} - {response.text}")
            return None
    
    def get_user_events(self, username: str, org: Optional[str] = None) -> List[Dict]:
        """Get GitHub events for a user.
        
        Args:
            username: GitHub username
            org: Optional organization name to filter events
            
        Returns:
            List of event dictionaries
        """
        access_token = self._get_access_token()
        if not access_token:
            return []
        
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {access_token}"
        }
        
        if org:
            url = f"https://api.github.com/users/{username}/events/orgs/{org}"
        else:
            url = f"https://api.github.com/users/{username}/events"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch events: {response.status_code} - {response.text}")
            return []
        
        return response.json()
    
    def filter_recent_events(self, events: List[Dict], days: int = 2) -> List[Dict]:
        """Filter events to only include recent ones.
        
        Args:
            events: List of event dictionaries
            days: Number of days to look back
            
        Returns:
            Filtered list of recent events
        """
        cutoff_date = datetime.now().date() - timedelta(days=days-1)
        recent_events = []
        
        for event in events:
            try:
                event_date = datetime.strptime(
                    event["created_at"], "%Y-%m-%dT%H:%M:%SZ"
                ).date()
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except (ValueError, KeyError):
                continue
        
        return recent_events
    
    def format_events_for_summary(self, events: List[Dict]) -> str:
        """Format events for inclusion in summary.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            Formatted event information string
        """
        if not events:
            return "No GitHub events found for the recent days."
        
        event_info = "Recent GitHub Events:\n"
        for event in events:
            event_type = event.get("type", "Unknown")
            repo_name = event.get("repo", {}).get("name", "Unknown repo")
            event_time = event.get("created_at", "Unknown time")
            
            event_info += f"- {event_type} on {repo_name} at {event_time}\n"
        
        return event_info