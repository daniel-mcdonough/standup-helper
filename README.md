# Standup Automation

Personal automation tool that aggregates work data from multiple sources (Git, Jira, notes, time tracking) and generates AI-powered summaries for standup meetings.

Built this because I was tired of manually collecting what I worked on each day.

## What it does

- Collects Git commits from your repos
- Pulls assigned Jira tickets 
- Reads your daily work notes (if you keep them)
- Optionally grabs time tracking data
- Feeds all this to Vertex AI to generate a standup summary

Saves me about 5-10 minutes every morning.

## Setup

You'll need Python 3.8+ and Google Cloud credentials for Vertex AI.

```bash
# Install stuff
make install-dev

# Copy config templates  
cp config.example.ini config.ini
cp secrets/secrets.example.env secrets/secrets.env

# Edit the config files with your settings
# Check SECURITY.md for the credential setup details

# Auth with Google Cloud
gcloud auth application-default login
```

## Running it

```bash
python main.py
```

That's it. It'll spit out a formatted standup summary.

## Config

Settings are split across a few files:
- `config.ini` - non-sensitive stuff (project IDs, file paths)  
- `secrets/secrets.env` - API keys and tokens
- Environment variables override both

Check `SECURITY.md` for the full setup walkthrough.

## Testing individual parts

```bash
python jira-test.py    # Test Jira connection
python github-test.py  # Test GitHub (currently disabled)
```

## Example output

Looks something like:

```
Standup Summary for 2024-01-15

What I worked on yesterday:
• Fixed auth bug in Jira client (PROJ-123)
• Refactored data aggregator 
• Updated docs

What I'm working on today:
• GitHub event filtering (PROJ-124)
• Add tests for AI service

Blockers:
• Waiting for API key from IT
```

## How it works

Pretty simple structure:

```
src/
├── standup_automation.py    # Main entry point
├── config.py               # Config loading
├── clients/
│   ├── jira_client.py     # Jira API stuff
│   └── github_client.py   # GitHub API (disabled for now)
├── services/
│   ├── data_aggregator.py # Collects all the data
│   └── ai_service.py      # Talks to Vertex AI
└── utils/
    └── logger.py          # Logging
```

The `data_aggregator.py` pulls from all sources, then `ai_service.py` formats it into a readable summary.

## Data sources

It pulls from:
- Work notes (if you keep `YYYY/MM/DD.txt` files)
- Git commits from configured repos
- Jira tickets assigned to you  
- Timewarrior data (optional)

## Development

```bash
make format    # Format code with black/isort
make lint      # Run flake8, mypy
make test      # Run tests (when I add them)
```

The code is typed and formatted, because why make life harder.