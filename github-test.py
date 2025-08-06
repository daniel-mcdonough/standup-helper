"""Test script for GitHub API integration using the new modular structure."""

from src.config import Config
from src.clients.github_client import GitHubClient

def main():
    """Test GitHub client functionality."""
    try:
        # Load configuration
        config = Config()
        
        # Initialize GitHub client
        github_client = GitHubClient(
            config.github_app_id,
            config.github_installation_id,
            config.private_key_path
        )
        
        # Fetch events
        print("Fetching GitHub events...")
        events = github_client.get_user_events(config.github_username, "MagMutual")
        
        # Filter recent events
        recent_events = github_client.filter_recent_events(events)
        
        # Display results
        if recent_events:
            print(f"Found {len(recent_events)} recent events:")
            formatted_events = github_client.format_events_for_summary(recent_events)
            print(formatted_events)
        else:
            print("No recent GitHub events found.")
            
    except Exception as e:
        print(f"Error testing GitHub client: {e}")

if __name__ == "__main__":
    main()
