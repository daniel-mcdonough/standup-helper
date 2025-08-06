#!/usr/bin/env python3
"""Debug script to view the structured data being sent to Gemini."""

from src.config import Config
from src.clients.jira_client import JiraClient
from src.services.data_aggregator import DataAggregator

def main():
    """Show the structured data that would be sent to Gemini."""
    try:
        # Load configuration
        config = Config()
        
        # Initialize Jira client
        jira_client = None
        try:
            jira_client = JiraClient(
                config.jira_domain,
                config.email,
                config.jira_api_key
            )
        except Exception as e:
            print(f"Warning: Could not initialize Jira client: {e}")
        
        # Initialize data aggregator
        data_aggregator = DataAggregator(jira_client, None)
        
        # Get structured data
        print("=" * 80)
        print("STRUCTURED DATA FOR GEMINI")
        print("=" * 80)
        
        structured_data = data_aggregator.aggregate_all_data_structured(
            config.notes_directory,
            config.git_author,
            config.git_directories,
            None  # No GitHub username
        )
        
        print(structured_data)
        
        print("\n" + "=" * 80)
        print(f"Total characters: {len(structured_data)}")
        print("=" * 80)
        
        # Also show the original unstructured data for comparison
        print("\n\n" + "=" * 80)
        print("ORIGINAL UNSTRUCTURED DATA (for comparison)")
        print("=" * 80)
        
        unstructured_data = data_aggregator.aggregate_all_data(
            config.notes_directory,
            config.git_author,
            config.git_directories,
            None
        )
        
        print(unstructured_data[:2000] + "..." if len(unstructured_data) > 2000 else unstructured_data)
        print(f"\nTotal characters: {len(unstructured_data)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()