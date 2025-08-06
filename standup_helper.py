import os
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import json
import vertexai
from vertexai.generative_models import GenerativeModel
import configparser
import subprocess
from typing import List

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Variables from the config file
PROJECT_ID = config.get("settings", "PROJECT_ID")
LOCATION = config.get("settings", "LOCATION")
JIRA_DOMAIN = config.get("settings", "JIRA_DOMAIN")
EMAIL = config.get("settings", "EMAIL")
JIRA_API_KEY = config.get("settings", "JIRA_API_KEY")
NOTES_DIRECTORY = config.get("paths", "NOTES_DIRECTORY")
OUTPUT_DIRECTORY = config.get("paths", "OUTPUT_DIRECTORY")
GIT_AUTHOR = config.get("settings", "GIT_AUTHOR")
GIT_DIRECTORIES = json.loads(config.get("paths", "GIT_DIRECTORIES"))
INSTRUCTION = config.get("vertex", "INSTRUCTION")
MODEL = config.get("vertex", "MODEL")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel(MODEL)

# Jira API endpoint and authentication
url = f"https://{JIRA_DOMAIN}/rest/api/3/search"
auth = HTTPBasicAuth(EMAIL, JIRA_API_KEY)

# Headers for Jira
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def fetch_tickets():
    """Fetch tickets from Jira using a POST request and JQL."""
    jql_query = 'assignee = currentUser() AND status in ("To Do", "In Progress", "On Hold") ORDER BY priority DESC'
    payload = json.dumps({
        "jql": jql_query,
        "fields": ["summary", "status", "key"],
        "maxResults": 50
    })

    response = requests.post(url, data=payload, headers=headers, auth=auth)

    if response.status_code == 200:
        return response.json().get("issues", [])
    else:
        print(f"Failed to fetch tickets: {response.status_code} - {response.text}")
        return []

def format_tickets_for_prompt(tickets):
    """Format Jira tickets data for appending to Vertex AI prompt."""
    if not tickets:
        return "No tickets found."
    
    ticket_info = "Take into account these tickets:\n"
    for ticket in tickets:
        key = ticket.get("key")
        fields = ticket.get("fields", {})
        summary = fields.get("summary", "No summary available")
        status = fields.get("status", {}).get("name", "No status available")
        
        ticket_info += f"- {key} ({status}): {summary}\n"
    return ticket_info

def get_git_history(author: str, folders: List[str], since: str = "yesterday") -> dict:
    """
    Retrieves the Git commit history for the specified author from multiple folders.
    """
    commit_data = {}

    git_log_cmd = [
        "git", "log", "--all", "--reverse",
        f"--author={author}",
        f"--since={since}",
        "--pretty=format:%h %ad | %s [%d] (%an)",
        "--date=short"
    ]

    for folder in folders:
        if not os.path.isdir(folder):
            print(f"Folder '{folder}' does not exist or is not accessible.")
            continue

        try:
            # Run git log command in each specified folder
            result = subprocess.run(
                git_log_cmd, cwd=folder, text=True,
                capture_output=True, check=True
            )
            # Store the output in the dictionary, keyed by folder path
            commit_data[folder] = result.stdout.strip().split('\n') if result.stdout else []
        
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving git log from '{folder}': {e}")
            commit_data[folder] = []

    return commit_data

def format_git_history(history):
    """Format Git commit history for appending to Vertex AI prompt."""
    if not history:
        return "No Git history found."

    history_info = "Include this Git history:\n"
    for folder, commits in history.items():
        history_info += f"\nFolder: {folder}\n"
        for commit in commits:
            history_info += f"- {commit}\n"
    return history_info

def get_timew_summary() -> str:
    """Retrieve Timewarrior summary for yesterday."""
    try:
        result = subprocess.run(
            ["timew", "summary", ":yesterday"],
            text=True,
            capture_output=True,
            check=True
        )
        return f"Timewarrior Summary for yesterday:\n{result.stdout.strip()}"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving Timewarrior summary: {e}")
        return "No timewarrior summary available."

def summarize_text(content):
    """Summarize or add context to the combined content of two days' notes using Vertex AI's GenerativeModel."""
    try:
        full_prompt = f"{INSTRUCTION}\n\n{content}"
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during Vertex AI summarization: {e}")
        return None

def process_notes(directory):
    """Read notes for today and the previous workday (handles special case for Monday), combine them, add Jira ticket info and GitHub activity, and summarize the content."""
    today = datetime.now()
    if today.weekday() == 0:  # Check if it's Monday
        # If it's Monday, set `previous_workday` to Friday
        previous_workday = today - timedelta(days=3)
    else:
        # Otherwise, set `previous_workday` to yesterday
        previous_workday = today - timedelta(days=1)

    today_path = os.path.join(directory, today.strftime("%Y"), today.strftime("%m"), f"{today.strftime('%d')}.txt")
    previous_workday_path = os.path.join(directory, previous_workday.strftime("%Y"), previous_workday.strftime("%m"), f"{previous_workday.strftime('%d')}.txt")

    combined_content = ""

    if os.path.exists(today_path):
        with open(today_path, "r", encoding="utf-8") as file:
            combined_content += f"Notes for {today.strftime('%Y-%m-%d')}:\n{file.read()}\n\n"

    if os.path.exists(previous_workday_path):
        with open(previous_workday_path, "r", encoding="utf-8") as file:
            combined_content += f"Notes for {previous_workday.strftime('%Y-%m-%d')}:\n{file.read()}\n\n"

    tickets = fetch_tickets()
    jira_info = format_tickets_for_prompt(tickets)
    combined_content += jira_info + "\n"

    git_history = get_git_history(GIT_AUTHOR, GIT_DIRECTORIES, since="yesterday")
    git_info = format_git_history(git_history)
    combined_content += git_info + "\n"
    timew_summary = get_timew_summary()
    combined_content += timew_summary + "\n\n"

    if combined_content:
        summary = summarize_text(combined_content)
        if summary:
            print(f"Combined summary for {previous_workday.strftime('%Y-%m-%d')} and {today.strftime('%Y-%m-%d')}:\n{summary}")
            return {"date_range": f"{previous_workday.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}", "summary": summary}
        else:
            print("Failed to summarize the combined notes")
            return None
    else:
        print("No notes found for today or the previous workday.")
        return None

summarized_notes = process_notes(NOTES_DIRECTORY)

if summarized_notes:
    # Define the output file path
    output_path = os.path.join(OUTPUT_DIRECTORY, "summaries.txt")
    
    # Append the summary to the file
    with open(output_path, "a", encoding="utf-8") as output_file:
        output_file.write(f"{summarized_notes['date_range']}: {summarized_notes['summary']}\n")