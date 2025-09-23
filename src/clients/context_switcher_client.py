"""Context switcher API client for fetching task switching data."""

import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json


class ContextSwitcherClient:
    """Client for interacting with the context switcher API."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """Initialize the context switcher client.
        
        Args:
            base_url: Base URL for the context switcher API
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10
    
    def test_connection(self) -> bool:
        """Test if the context switcher API is reachable.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/current")
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get current Timewarrior task and summary.
        
        Returns:
            Current task info or None if failed
        """
        try:
            response = self.session.get(f"{self.base_url}/current")
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def get_recent_switches(self, days: int = 1) -> List[Dict[str, Any]]:
        """Get detailed switch log for recent days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of switch entries
        """
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            }
            
            response = self.session.get(f"{self.base_url}/switches/list", params=params)
            response.raise_for_status()
            return response.json().get('switches', [])
        except requests.RequestException:
            return []
    
    def get_switch_counts(self, view: str = "week") -> Dict[str, Any]:
        """Get switch counts by day.
        
        Args:
            view: 'week' or 'month' view
            
        Returns:
            Switch counts data
        """
        try:
            params = {'view': view}
            response = self.session.get(f"{self.base_url}/metrics/counts", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
    
    def get_switch_leaders(self) -> List[Dict[str, Any]]:
        """Get tasks causing most context switches.
        
        Returns:
            List of tasks with switch counts
        """
        try:
            response = self.session.get(f"{self.base_url}/analytics/switch-leaders")
            response.raise_for_status()
            return response.json().get('leaders', [])
        except requests.RequestException:
            return []
    
    def format_switches_for_summary(self, switches: List[Dict[str, Any]]) -> str:
        """Format switch data for standup summary.
        
        Args:
            switches: List of switch entries
            
        Returns:
            Formatted string for summary
        """
        if not switches:
            return "No context switching data available."
        
        # Group switches by date
        switches_by_date = {}
        total_switches = len(switches)
        
        for switch in switches:
            # Parse the start_time (assuming it's in ISO format)
            try:
                if switch.get('start_time'):
                    start_time = datetime.fromisoformat(switch['start_time'].replace('Z', '+00:00'))
                    date_key = start_time.strftime('%Y-%m-%d')
                else:
                    date_key = 'unknown'
                
                if date_key not in switches_by_date:
                    switches_by_date[date_key] = []
                switches_by_date[date_key].append(switch)
            except (ValueError, TypeError):
                # Skip invalid timestamps
                continue
        
        # Build summary
        summary = f"Context Switching Summary ({total_switches} total switches):\n"
        
        for date, date_switches in sorted(switches_by_date.items()):
            if date == 'unknown':
                continue
                
            summary += f"\n{date} ({len(date_switches)} switches):\n"
            
            for switch in date_switches:
                task = switch.get('task', 'Unknown task')
                duration = switch.get('duration_minutes', 0)
                notes = switch.get('notes', '')
                tags = switch.get('tags', [])
                
                duration_str = f"{duration}min" if duration > 0 else "ongoing"
                
                summary += f"  • {task} ({duration_str})"
                
                if tags:
                    summary += f" [{', '.join(tags)}]"
                
                if notes:
                    summary += f" - {notes[:100]}{'...' if len(notes) > 100 else ''}"
                
                summary += "\n"
        
        return summary
    
    def get_productivity_metrics(self) -> str:
        """Get productivity metrics including switch counts and patterns.
        
        Returns:
            Formatted productivity metrics string
        """
        try:
            # Get recent switches
            recent_switches = self.get_recent_switches(days=2)
            
            # Get switch counts
            switch_counts = self.get_switch_counts(view="week")
            
            # Get current task
            current_task = self.get_current_task()
            
            # Build metrics summary
            metrics = "Context Switching Productivity Metrics:\n"
            
            if current_task and current_task.get('current_task'):
                metrics += f"Current Task: {current_task['current_task']}\n"
            
            if switch_counts.get('total_switches_this_week'):
                metrics += f"Total switches this week: {switch_counts['total_switches_this_week']}\n"
            
            if recent_switches:
                today_switches = [s for s in recent_switches 
                                if s.get('start_time', '').startswith(datetime.now().strftime('%Y-%m-%d'))]
                yesterday_switches = [s for s in recent_switches 
                                    if s.get('start_time', '').startswith((datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'))]
                
                metrics += f"Switches today: {len(today_switches)}\n"
                metrics += f"Switches yesterday: {len(yesterday_switches)}\n"
            
            # Add switch details
            if recent_switches:
                metrics += "\n" + self.format_switches_for_summary(recent_switches)
            
            return metrics
            
        except Exception as e:
            return f"Error getting productivity metrics: {e}"