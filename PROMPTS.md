# Vertex AI Prompt Templates

This file contains alternative prompts you can use in your `config.ini` file under the `[vertex]` section.

## Strict Past-Work Only (Default)

Best for: Avoiding speculation and focusing only on completed work.

```ini
INSTRUCTION = Generate a standup summary for a site reliability engineer. 
    CRITICAL RULES:
    1. ONLY report work that was ACTUALLY COMPLETED - no future plans or intentions
    2. ONLY mention tickets that have EVIDENCE of work (commits, time tracking, or explicit notes)
    3. Use PAST TENSE exclusively - describe what was done, not what will be done
    4. DO NOT speculate about future work or next steps
    5. DO NOT mention tickets just because they exist in Jira - only if work was performed
    6. Focus on concrete actions: deployed, fixed, configured, investigated, resolved
    7. Group related work together by ticket when possible
    8. Be specific but concise - mention environment names, repos, and specific changes
    
    Structure the summary as:
    - Yesterday's completed work (with ticket numbers where applicable)
    - This morning's completed work (if any)
    
    Base the summary ONLY on evidence from notes, git commits, and time tracking.
```

## Conversational Style

Best for: More natural-sounding updates with personality.

```ini
INSTRUCTION = Create a friendly standup update for an SRE. 
    Rules:
    - Report only on work that's been completed (past tense)
    - Be conversational but professional
    - Include ticket numbers naturally in the flow
    - Mention specific environments, repos, and changes
    - Group related work together
    - No future plans unless explicitly noted as done
    
    Format: Brief paragraph for yesterday, brief paragraph for today (if applicable).
```

## Bullet Point Style

Best for: Quick scanning and clarity.

```ini
INSTRUCTION = Generate a bullet-point standup summary.
    
    Requirements:
    - Use bullet points for each completed task
    - Include ticket ID at the start of each bullet
    - Past tense only - work that was completed
    - Specific details (environments, repos, what changed)
    - No speculation or future work
    - Separate sections for "Yesterday:" and "Today:" (if applicable)
    
    Focus on evidence from notes, commits, and time tracking only.
```

## Technical Detail Focus

Best for: Teams that want more technical depth.

```ini
INSTRUCTION = Generate a technical standup summary for an SRE.
    
    Include:
    - Ticket numbers for all work
    - Specific technical changes made (configs, deployments, permissions)
    - Repository names and commit references where applicable
    - Environment names (dev, staging, prod)
    - Any errors or issues encountered and how they were resolved
    
    Exclude:
    - Future plans or intentions
    - Tickets without actual work performed
    - Speculation about next steps
    
    Use past tense exclusively. Structure as Yesterday/Today sections.
```

## Time-Conscious Summary

Best for: When time tracking is important.

```ini
INSTRUCTION = Generate a time-aware standup summary.
    
    For each significant task completed:
    - Include ticket number
    - Mention time spent (if tracked)
    - Describe what was accomplished
    - Note the environment or system affected
    
    Rules:
    - Past tense only
    - No future planning
    - Only tickets with actual work
    - If multiple related commits, summarize the overall change
    
    Format: Organize by day (yesterday/today), with time annotations where available.
```

## Usage

To use any of these prompts:

1. Copy the `INSTRUCTION = ...` block you want
2. Open your `config.ini` file
3. Replace the existing `INSTRUCTION` value in the `[vertex]` section
4. Save the file
5. Run the application as normal

## Tips for Custom Prompts

When writing your own prompt, consider:

- **Be explicit** about what NOT to include (future work, unworked tickets)
- **Use clear rules** rather than vague guidance
- **Specify the output format** you want
- **Focus on evidence** from actual data sources
- **Use action verbs** that match your work style
- **Test and iterate** to get the tone right for your team