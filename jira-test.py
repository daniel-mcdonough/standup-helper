"""Test script for Jira API integration using the new modular structure."""

from src.config import Config
from src.clients.jira_client import JiraClient

def main():
    """Test Jira client functionality."""
    try:
        # Load configuration
        config = Config()
        
        # Initialize Jira client
        jira_client = JiraClient(
            config.jira_domain,
            config.email,
            config.jira_api_key
        )
        
        # Fetch active tickets
        print("Fetching active Jira tickets...")
        tickets = jira_client.get_my_active_tickets()
        
        # Display results
        if tickets:
            print(f"Found {len(tickets)} active tickets:")
            formatted_tickets = jira_client.format_tickets_for_summary(tickets)
            print(formatted_tickets)
        else:
            print("No active Jira tickets found.")
            
    except Exception as e:
        print(f"Error testing Jira client: {e}")

if __name__ == "__main__":
    main()