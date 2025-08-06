"""Data preprocessing service for cleaning and structuring data for AI processing."""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict


class DataPreprocessor:
    """Service for preprocessing and structuring data for better AI comprehension."""
    
    # Common Jira ticket patterns
    TICKET_PATTERNS = [
        r'\b([A-Z]{2,}-\d+)\b',  # Standard JIRA format (INFRA-1234)
        r'\b([A-Z]+\d+)\b',       # Compact format (INFRA1234)
    ]
    
    # Time tracking patterns
    TIME_PATTERNS = [
        r'(\d{1,2}:\d{2})\s*(?:am|pm|AM|PM)?',  # Time mentions
        r'(\d+)\s*(?:hours?|hrs?|minutes?|mins?)',  # Duration mentions
    ]
    
    def __init__(self):
        """Initialize the preprocessor."""
        self.ticket_map = {}
        self.time_entries = defaultdict(list)
    
    def extract_ticket_ids(self, text: str) -> Set[str]:
        """Extract all ticket IDs from text.
        
        Args:
            text: Text to search for ticket IDs
            
        Returns:
            Set of unique ticket IDs found
        """
        tickets = set()
        for pattern in self.TICKET_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tickets.update(match.upper() for match in matches)
        return tickets
    
    def normalize_ticket_references(self, text: str) -> str:
        """Normalize all ticket references to consistent format.
        
        Args:
            text: Text containing ticket references
            
        Returns:
            Text with normalized ticket references
        """
        # Ensure all ticket IDs are uppercase and properly formatted
        for pattern in self.TICKET_PATTERNS:
            text = re.sub(pattern, lambda m: m.group(1).upper(), text)
        return text
    
    def extract_timestamps(self, text: str) -> List[str]:
        """Extract time references from text.
        
        Args:
            text: Text to search for time references
            
        Returns:
            List of time references found
        """
        timestamps = []
        for pattern in self.TIME_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            timestamps.extend(matches)
        return timestamps
    
    def correlate_ticket_data(
        self, 
        notes: str, 
        jira_tickets: List[Dict],
        git_commits: str,
        timew_data: str
    ) -> Dict[str, Dict]:
        """Correlate ticket IDs across all data sources.
        
        Args:
            notes: Work notes text
            jira_tickets: List of Jira ticket dictionaries
            git_commits: Git commit history text
            timew_data: Timewarrior data text
            
        Returns:
            Dictionary mapping ticket IDs to correlated data
        """
        correlated = defaultdict(lambda: {
            'mentioned_in_notes': False,
            'jira_status': None,
            'jira_summary': None,
            'git_commits': [],
            'time_tracked': False,
            'contexts': []
        })
        
        # Extract tickets from notes
        notes_tickets = self.extract_ticket_ids(notes)
        for ticket in notes_tickets:
            correlated[ticket]['mentioned_in_notes'] = True
            # Extract context around ticket mention
            context = self._extract_context(notes, ticket)
            if context:
                correlated[ticket]['contexts'].append(('notes', context))
        
        # Add Jira ticket data
        for ticket in jira_tickets:
            ticket_id = ticket.get('key', '')
            if ticket_id:
                fields = ticket.get('fields', {})
                correlated[ticket_id]['jira_status'] = fields.get('status', {}).get('name')
                correlated[ticket_id]['jira_summary'] = fields.get('summary')
        
        # Extract tickets from git commits
        git_tickets = self.extract_ticket_ids(git_commits)
        for ticket in git_tickets:
            # Find associated commit messages
            commits = self._extract_git_commits_for_ticket(git_commits, ticket)
            correlated[ticket]['git_commits'].extend(commits)
        
        # Extract tickets from timewarrior
        timew_tickets = self.extract_ticket_ids(timew_data)
        for ticket in timew_tickets:
            correlated[ticket]['time_tracked'] = True
            # Extract time duration if available
            duration = self._extract_time_duration(timew_data, ticket)
            if duration:
                correlated[ticket]['time_duration'] = duration
        
        return dict(correlated)
    
    def _extract_context(self, text: str, ticket_id: str, context_size: int = 100) -> str:
        """Extract context around a ticket mention.
        
        Args:
            text: Full text to search
            ticket_id: Ticket ID to find context for
            context_size: Characters of context on each side
            
        Returns:
            Context string or empty if not found
        """
        pattern = re.compile(rf'\b{re.escape(ticket_id)}\b', re.IGNORECASE)
        match = pattern.search(text)
        if match:
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            # Find sentence boundaries
            context = text[start:end].strip()
            # Clean up partial sentences
            if start > 0:
                context = '...' + context
            if end < len(text):
                context = context + '...'
            return context
        return ""
    
    def _extract_git_commits_for_ticket(self, git_log: str, ticket_id: str) -> List[str]:
        """Extract git commits mentioning a ticket.
        
        Args:
            git_log: Git log output
            ticket_id: Ticket ID to search for
            
        Returns:
            List of commit messages mentioning the ticket
        """
        commits = []
        lines = git_log.split('\n')
        for line in lines:
            if ticket_id.upper() in line.upper():
                # Clean up the commit message
                commit = line.strip()
                if commit and commit not in commits:
                    commits.append(commit)
        return commits
    
    def _extract_time_duration(self, timew_data: str, ticket_id: str) -> Optional[str]:
        """Extract time duration for a ticket from timewarrior data.
        
        Args:
            timew_data: Timewarrior output
            ticket_id: Ticket ID to find duration for
            
        Returns:
            Duration string or None
        """
        lines = timew_data.split('\n')
        for i, line in enumerate(lines):
            if ticket_id in line:
                # Look for duration patterns in the same or nearby lines
                for j in range(max(0, i-1), min(len(lines), i+2)):
                    duration_match = re.search(r'(\d+:\d+:\d+|\d+:\d+)', lines[j])
                    if duration_match:
                        return duration_match.group(1)
        return None
    
    def structure_for_ai(
        self,
        correlated_data: Dict[str, Dict],
        notes: str,
        date_range: Tuple[datetime, datetime]
    ) -> str:
        """Structure data in a format optimized for AI comprehension.
        
        Args:
            correlated_data: Correlated ticket data
            notes: Raw notes text
            date_range: Tuple of (start_date, end_date)
            
        Returns:
            Structured text for AI processing
        """
        structured = []
        
        # Add date context
        start_date, end_date = date_range
        structured.append(f"=== TIMEFRAME ===")
        structured.append(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        if start_date.date() != end_date.date():
            structured.append(f"Yesterday: {start_date.strftime('%A, %B %d')}")
            structured.append(f"Today: {end_date.strftime('%A, %B %d')}")
        structured.append("")
        
        # Add ticket correlations
        if correlated_data:
            structured.append("=== TICKET WORK ===")
            
            # Separate tickets by activity level
            active_tickets = []
            mentioned_tickets = []
            
            for ticket_id, data in correlated_data.items():
                if data['git_commits'] or data['time_tracked'] or data['mentioned_in_notes']:
                    active_tickets.append((ticket_id, data))
                else:
                    mentioned_tickets.append((ticket_id, data))
            
            # Process active tickets first
            if active_tickets:
                structured.append("ACTIVELY WORKED ON:")
                for ticket_id, data in sorted(active_tickets):
                    structured.append(f"\n• {ticket_id}")
                    if data['jira_summary']:
                        structured.append(f"  Summary: {data['jira_summary']}")
                    if data['jira_status']:
                        structured.append(f"  Status: {data['jira_status']}")
                    if data.get('time_duration'):
                        structured.append(f"  Time spent: {data['time_duration']}")
                    if data['git_commits']:
                        structured.append(f"  Commits: {len(data['git_commits'])} commit(s)")
                        for commit in data['git_commits'][:2]:  # Show first 2 commits
                            structured.append(f"    - {commit[:100]}")
                    if data['contexts']:
                        for source, context in data['contexts'][:1]:  # Show first context
                            structured.append(f"  Context: {context[:150]}")
            
            # Then mentioned tickets
            if mentioned_tickets:
                structured.append("\nALSO TRACKING:")
                for ticket_id, data in sorted(mentioned_tickets):
                    line = f"• {ticket_id}"
                    if data['jira_status']:
                        line += f" ({data['jira_status']})"
                    if data['jira_summary']:
                        line += f": {data['jira_summary'][:50]}"
                    structured.append(line)
        
        structured.append("")
        
        # Add cleaned notes
        structured.append("=== WORK NOTES ===")
        # Remove redundant ticket IDs from notes since we've already structured them
        cleaned_notes = self._clean_notes(notes, correlated_data.keys())
        structured.append(cleaned_notes)
        
        return '\n'.join(structured)
    
    def _clean_notes(self, notes: str, ticket_ids: Set[str]) -> str:
        """Clean notes for better readability.
        
        Args:
            notes: Raw notes text
            ticket_ids: Set of ticket IDs already processed
            
        Returns:
            Cleaned notes text
        """
        # Remove duplicate timestamps
        notes = re.sub(r'(\d{1,2}:\d{2})\s*(?:am|pm|AM|PM)?\s*-\s*', '', notes)
        
        # Remove excessive whitespace
        notes = re.sub(r'\n{3,}', '\n\n', notes)
        notes = re.sub(r' {2,}', ' ', notes)
        
        # Organize by paragraphs
        lines = notes.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def deduplicate_content(self, text: str) -> str:
        """Remove duplicate lines and similar content.
        
        Args:
            text: Text to deduplicate
            
        Returns:
            Deduplicated text
        """
        lines = text.split('\n')
        seen = set()
        unique_lines = []
        
        for line in lines:
            # Normalize for comparison
            normalized = line.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)