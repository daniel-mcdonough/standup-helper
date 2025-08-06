"""Jira API client for fetching tickets and project information."""

import json
import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Optional


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(self, domain: str, email: str, api_key: str):
        """Initialize Jira client.
        
        Args:
            domain: Jira domain (e.g., 'company.atlassian.net')
            email: User email for authentication
            api_key: Jira API key
        """
        self.domain = domain
        self.email = email
        self.api_key = api_key
        self.base_url = f"https://{domain}/rest/api/3"
        self.auth = HTTPBasicAuth(email, api_key)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def search_issues(
        self,
        jql: str,
        fields: Optional[List[str]] = None,
        max_results: int = 50
    ) -> List[Dict]:
        """Search for issues using JQL.
        
        Args:
            jql: JQL query string
            fields: List of fields to retrieve
            max_results: Maximum number of results
            
        Returns:
            List of issue dictionaries
            
        Raises:
            requests.RequestException: If the API request fails
        """
        if fields is None:
            fields = ["summary", "status", "key"]
        
        url = f"{self.base_url}/search"
        payload = {
            "jql": jql,
            "fields": fields,
            "maxResults": max_results
        }
        
        response = requests.post(
            url,
            data=json.dumps(payload),
            headers=self.headers,
            auth=self.auth
        )
        response.raise_for_status()
        
        return response.json().get("issues", [])
    
    def get_my_active_tickets(self) -> List[Dict]:
        """Get active tickets assigned to the current user.
        
        Returns:
            List of active ticket dictionaries
        """
        jql = 'assignee = currentUser() AND status in ("To Do", "In Progress", "On Hold") ORDER BY priority DESC'
        return self.search_issues(jql)
    
    def format_tickets_for_summary(self, tickets: List[Dict]) -> str:
        """Format tickets for inclusion in summary.
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            Formatted ticket information string
        """
        if not tickets:
            return "No tickets found."
        
        ticket_info = "Take into account these tickets:\n"
        for ticket in tickets:
            key = ticket.get("key", "Unknown")
            fields = ticket.get("fields", {})
            summary = fields.get("summary", "No summary available")
            status = fields.get("status", {}).get("name", "No status available")
            
            ticket_info += f"- {key} ({status}): {summary}\n"
        
        return ticket_info