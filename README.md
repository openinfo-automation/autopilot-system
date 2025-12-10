# Autopilot System

An autonomous AI-powered automation system that uses OpenAI and Claude to execute tasks and workflows.

## Features

- 🤖 Dual AI integration (OpenAI GPT-3.5 + Claude 3 Haiku)
- ⚡ Event-driven task execution
- 🔄 Multi-step workflow automation
- 🆓 Runs on free tier (Render + GitHub)

## API Endpoints

### `GET /`

Health check - returns system status

### `POST /autopilot/execute`

Execute a single AI task

```json
{
  "task_type": "creative",
  "prompt": "Your task here"
}
```

### `POST /autopilot/workflow`

Execute multi-step workflow

```json
{
  "steps": [
    {"type": "claude", "prompt": "Step 1 task"},
    {"type": "openai", "prompt": "Step 2 task"}
  ]
}
```

## Deployment

### Deploy to Render

1. Connect this GitHub repo to Render
1. Add environment variables:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`

1. Set start command: `gunicorn main:app`
1. Deploy!

## Environment Variables

```bash
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

## Local Development

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key
export ANTHROPIC_API_KEY=your_key
python main.py
```

## Tech Stack

- Python 3
- Flask
- OpenAI API
- Anthropic Claude API
- Gunicorn
- Render (hosting)
