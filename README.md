# ContentOS

> AI-powered YouTube content production system with channel memory.

ContentOS is a CLI tool that helps you produce YouTube content with AI assistance. Each channel has its own "brain" that remembers what works, what doesn't, and evolves over time.

**Designed for both humans AND AI agents.**

## Features

- **Channel Brain** - Persistent knowledge per channel (identity, themes, learnings)
- **Context Surfing** - AI can explore system progressively (`contentos index`)
- **Kit Production** - Generate scripts, prompts, and assets
- **Research Agents** - Scout (market research) and Analyst (audience insights)
- **Health Checks** - System diagnostics

---

## Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) (optional, for AI features)
- YouTube API credentials (optional, for analytics)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/yourusername/contentos.git
cd contentos

# Install dependencies
pip install -r requirements.txt

# Run guided setup
python contentos.py setup
```

---

## Using with AI Agents (Agentic IDEs)

ContentOS is designed to be operated by AI assistants in agentic IDEs like:
- **Cursor** (with Agent mode)
- **Windsurf**
- **Cline/Claude Dev**
- **Antigravity**
- **Any terminal-based AI**

### Step 1: Onboard the AI

When starting a new session, tell your AI:

> "Run `python contentos.py boot` to understand this system"

Or for progressive exploration:

> "Run `python contentos.py index` to see the system structure"

### Step 2: AI Explores Context

The AI can navigate like browsing a website:

```bash
python contentos.py index                    # Root sitemap
python contentos.py index brain              # Channel knowledge
python contentos.py index brain.themes.loop  # Specific theme
python contentos.py index kits.018           # Specific kit
```

### Step 3: AI Creates Content

```bash
python contentos.py kit create "video_name" --theme loop
```

### Step 4: AI Updates Brain

After research or analysis:
```bash
python contentos.py scout --keyword "topic"  # Adds to learnings
python contentos.py scan comments            # Adds audience insights
```

### Workflow File (Optional)

Create `.agent/workflows/contentos.md` for your IDE:

```markdown
---
description: ContentOS - YouTube production workflow
---

1. Run `python contentos.py boot` to understand the system
2. Check health: `python contentos.py health`
3. View brain: `python contentos.py brain show`
4. Create kit: `python contentos.py kit create "<name>" --theme loop`
5. After creating, read the prompt.txt and script.txt in the kit folder
```

---

## Ollama Integration (AI Features)

ContentOS uses **Ollama** for local LLM features (scout, scan, suggestions).

### How It Works

1. ContentOS connects to Ollama at `http://localhost:11434`
2. Auto-selects the best available model from priority list:
   - `deepseek-v3.1:671b-cloud` (best reasoning)
   - `qwen3-coder:480b-cloud` (good backup)
   - `llama3.2:1b` (local fallback)
   - `mistral` (old faithful)
3. Falls back gracefully if Ollama isn't running

### Setup Ollama

```bash
# 1. Install Ollama
# Download from https://ollama.ai/

# 2. Pull a model
ollama pull deepseek-r1:8b

# 3. Enable in ContentOS
python contentos.py config enable llm_swarm

# 4. Test connection
python contentos.py test-crew
```

### What Uses Ollama

| Command | Uses LLM For |
|---------|--------------|
| `scout --keyword` | Analyzing competitor videos |
| `scan comments` | Map-reduce sentiment analysis |
| `strategy suggest` | Content recommendations |

---

## Quick Start (Human Usage)

```bash
# Check active channel
python contentos.py channel status

# View channel knowledge
python contentos.py brain show

# Create a production kit
python contentos.py kit create "my_video" --theme loop

# Run health check
python contentos.py health
```

---

## Architecture

```
contentos/
├── contentos.py          # CLI entry point
├── core/                 # Engine code
│   ├── brain.py          # Channel knowledge system
│   ├── llm.py            # Ollama integration
│   └── ...
├── commands/             # CLI commands
├── channels/             # Your channel data
│   └── {name}/
│       ├── brain/        # AI knowledge (state, themes, learnings)
│       ├── production/   # Active kits
│       └── analytics/    # YouTube data
├── protocols/            # Your prompt engineering knowledge
└── .contentos/           # System config
```

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `setup` | Guided first-time setup |
| `boot` | AI onboarding (dump all context) |
| `index [path]` | AI context surfing |
| `channel list/use/create` | Manage channels |
| `brain show/set-theme/init` | Manage channel knowledge |
| `kit create/list/publish` | Content production |
| `scout --keyword "x"` | Market research (needs Ollama) |
| `scan comments` | Audience analysis (needs Ollama) |
| `health` | System diagnostics |
| `config enable/disable` | Feature flags |

---

## License

MIT