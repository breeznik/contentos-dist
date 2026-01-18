# ContentOS User Guide

> How to work with AI assistants on ContentOS.

---

## Starting a Session

When you open a new AI session (new chat, new day, different AI), say:

```
/boot
```

Or if not using Antigravity:

```
Run `python contentos.py boot` to understand this system
```

This gives the AI full context about:
- What ContentOS is
- Active channel
- Channel identity, themes, audience insights
- Available commands

---

## Quick Commands to Give the AI

### Check System
```
Run contentos health
```

### See Channel Knowledge
```
Run contentos brain show
```

### Create Content
```
Create a new kit called "video_name" using the loop theme
```
AI will run: `python contentos.py kit create "video_name" --theme loop`

### Switch Theme
```
Switch to the advice theme
```
AI will run: `python contentos.py brain set-theme advice`

### Research Competition
```
Scout videos about "minecraft satisfying"
```
AI will run: `python contentos.py scout --keyword "minecraft satisfying"`

### Analyze Audience
```
Scan our recent comments
```
AI will run: `python contentos.py scan comments`

---

## What You Should Know

### Channels
You have multiple channels. Check which is active:
```
contentos channel status
```

Switch channels:
```
contentos channel use gaming_channel
```

### Themes
Each channel has themes (prompt formulas). View available:
```
contentos brain show
```

Current themes for gaming_channel:
- `loop` - 16s seamless loops
- `advice` - Corny cursed advice (30s)
- `cinematic` - Micro-stories (30-60s)

### Kits
A "kit" is a production package containing:
- `script.txt` - Video script
- `prompt.txt` - Image generation prompts
- `kit.yaml` - Metadata
- Generated assets (images)

Find them in: `channels/{name}/production/`

---

## Common Workflows

### Create a New Video

1. Tell AI: "Create a kit for a video about [topic] using [theme] theme"
2. AI creates the kit folder
3. Review script.txt and prompt.txt
4. Generate images using prompts
5. Tell AI: "Mark kit XXX as published" after uploading

### Research and Improve

1. Tell AI: "Scout videos about [topic]"
2. AI researches competitors, adds insights to learnings
3. Tell AI: "What did we learn?"
4. AI reads brain/learnings.md

### Check Performance

1. Tell AI: "Sync analytics"
2. AI pulls YouTube data
3. Tell AI: "Show brain performance stats"

---

## Folder Structure You Should Know

```
content/
├── channels/
│   └── gaming_channel/
│       ├── brain/           # AI knowledge
│       │   ├── state.json   # Identity, metrics
│       │   ├── themes/      # Prompt formulas
│       │   └── learnings.md # Insights
│       ├── production/      # Your kits
│       └── analytics/       # YouTube data
│
├── protocols/               # Your prompt engineering docs
│
└── contentos-dist/          # Distributable copy (for GitHub)
```

---

## Tips

1. **Start fresh sessions with `/boot`** - AI forgets everything between sessions

2. **Let AI update the brain** - After research or analysis, insights auto-save to learnings.md

3. **Don't edit brain files manually** - AI reads/writes them automatically

4. **Check health regularly** - `contentos health` catches issues early

5. **Themes live in brain/themes/** - Edit these to refine your prompt formulas

---

## Commands Reference

| What you want | What to say |
|---------------|-------------|
| Start session | `/boot` or "Run contentos boot" |
| Check health | "Run health check" |
| See brain | "Show brain" or "What do we know about this channel?" |
| Create content | "Create a kit called X with theme Y" |
| Change theme | "Switch to loop theme" |
| Research | "Scout videos about X" |
| Analyze comments | "Scan our comments" |
| Switch channel | "Switch to gaming_channel channel" |
| List kits | "Show production kits" |
| Enrich DNA | "Enrich kit X with DNA ingredients" |
| Link Video (Long) | "Link video ID to kit X" |
| Link Video (Short) | "Link short ID to kit X" |

---

## Troubleshooting

**AI doesn't know the system:**
→ Say `/boot` or run `contentos boot`

**Commands failing:**
→ Run `contentos health`

**Ollama not working:**
→ Make sure Ollama is running: `ollama serve`

**Wrong channel active:**
→ Run `contentos channel use <name>`
