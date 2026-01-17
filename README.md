# ContentOS

> AI-powered YouTube content production system with channel memory.

ContentOS is a CLI tool that helps you produce YouTube content with AI assistance. Each channel has its own "brain" that remembers what works, what doesn't, and evolves over time.

## Features

- **Channel Brain** - Persistent knowledge per channel (identity, themes, learnings)
- **Context Surfing** - AI can explore system progressively (`contentos index`)
- **Kit Production** - Generate scripts, prompts, and assets
- **Research Agents** - Scout (market research) and Analyst (audience insights)
- **Health Checks** - System diagnostics

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

# Initialize system
python contentos.py setup

# Create your first channel
python contentos.py channel create mychannel
```

### Manual Setup

If you prefer manual setup:

```bash
# 1. Create channels folder
mkdir channels

# 2. Create a channel
python contentos.py channel create mychannel

# 3. Initialize brain
python contentos.py brain init

# 4. Check health
python contentos.py health
```

## Quick Start

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

## For AI Agents

ContentOS is designed for AI-first workflows.

### Session Onboarding

```bash
# Full context dump (paste to any AI)
python contentos.py boot

# Progressive exploration
python contentos.py index
python contentos.py index brain
python contentos.py index brain.themes.loop
```

### Workflows

See `.agent/workflows/` for AI workflow definitions:
- `boot.md` - Session initialization
- `rotnation.md` - RotNation content production
- `kathakids.md` - KathaKids content production

## Architecture

```
contentos/
├── contentos.py          # CLI entry point
├── core/                 # Engine (system code)
│   ├── brain.py          # Channel knowledge system
│   ├── llm.py            # LLM integration (Ollama)
│   ├── protocols/        # Prompt engineering guides
│   └── ...
├── commands/             # CLI commands
├── channels/             # Channel data (output)
│   └── {name}/
│       ├── brain/        # AI knowledge
│       ├── production/   # Active kits
│       └── analytics/    # YouTube data
└── .contentos/           # Global config
```

## Commands Reference

| Command | Description |
|---------|-------------|
| `channel list/use/create` | Manage channels |
| `brain show/set-theme/init` | Manage channel knowledge |
| `kit create/list/publish` | Content production |
| `scout --keyword "x"` | Market research |
| `scan comments` | Audience analysis |
| `health` | System diagnostics |
| `boot` | AI onboarding (full dump) |
| `index [path]` | AI context surfing |

## Configuration

### Feature Flags

```bash
# Enable LLM features (requires Ollama)
python contentos.py config enable llm_swarm

# Disable LLM features
python contentos.py config disable llm_swarm
```

### YouTube API (Optional)

To enable YouTube analytics:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable YouTube Data API v3 and YouTube Analytics API
3. Create OAuth 2.0 credentials
4. Download `client_secret.json` to `credentials/`
5. Run `python contentos.py sync` to authenticate

## License

MIT