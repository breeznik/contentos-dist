"""
Channel Brain Module
The unified knowledge system for each channel.
Contains: state.json (facts), playbook.md (prompts), learnings.md (insights)
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

# Default brain templates
DEFAULT_STATE = {
    "version": "1.0",
    "updated_at": None,
    "identity": {
        "name": "",
        "niche": "",
        "audience": "",
        "tone": ""
    },
    "performance": {
        "total_videos": 0,
        "avg_views": 0,
        "best_format": "",
        "best_post_time": ""
    },
    "audience": {
        "wants": [],
        "complaints": [],
        "sentiment": 0.0
    },
    "active_theme": "loop"
}

DEFAULT_THEME_TEMPLATE = """# {theme_name} Theme

> Prompt formula and quality markers for {theme_name} format.
> Last updated: {date}

## Prompt Formula
```
[STYLE]: (Define visual style)
[ACTION]: (Define motion/action)
[PHYSICS]: (Define physics simulation)
[CAMERA]: (Define camera work)
```

## Anti-AI Tokens (Required)
- Subtle film grain, 16mm film texture
- Gentle handheld camera shake
- Atmospheric haze, dust particles
- Natural physics, weight and momentum

## Script Style
(Define the voiceover/text style for this theme)

## Proven Hooks
| Pattern | Win Rate | Uses |
|---------|----------|------|
| (Track successful hooks here) | | |

## Notes
(Any learnings specific to this theme)
"""

DEFAULT_LEARNINGS = """# {channel_name} Learnings

> Auto-generated insights from Scout, Analyst, and performance data.
> DO NOT EDIT MANUALLY - AI maintains this file.
> Last updated: {date}

## Performance Insights
- (Auto-populated after sync runs)

## Audience Insights
- (Auto-populated after scan runs)

## Market Gaps
- (Auto-populated after scout runs)

## Failed Experiments
- (Track what didn't work to avoid repeating)
"""

# Built-in theme definitions for quick setup
BUILTIN_THEMES = {
    "loop": {
        "name": "Brain Rot Loop",
        "format": "16s seamless loop (8s forward + 8s reverse)",
        "vibe": "Satisfying, hypnotic, infinite scroll bait",
        "style": "Macro, 8k, neon, high contrast, octane render",
        "action": "NO FADE. Continuous physics simulation",
        "physics": "Rigid body, fluid, particles",
        "camera": "Stationary, shallow DOF",
        "script": "Shower Thoughts / Uncomfortable Facts (Max 25 words)"
    },
    "advice": {
        "name": "Corny Cursed Advice",
        "format": "30s cursed advice with disaster",
        "vibe": "Dark humor, absurd, unexpected outcome",
        "style": "Stylized 3D, clean stock footage aesthetic",
        "action": "POV character follows bad advice, disaster ensues",
        "physics": "Exaggerated but grounded",
        "camera": "Dynamic, follows action, reaction shots",
        "script": "Narrator gives terrible advice, deadpan delivery"
    },
    "cinematic": {
        "name": "Cinematic Realism",
        "format": "30-60s micro-story",
        "vibe": "Film-quality, emotional, narrative-driven",
        "style": "Photorealistic, moody lighting, anamorphic",
        "action": "Single simple action with emotional weight",
        "physics": "Realistic, subtle",
        "camera": "Dolly, crane, handheld, 35mm/85mm lens",
        "script": "Micro-Narrative / Spoken Poetry, first-person"
    }
}

def get_brain_path(ctx) -> Path:
    """Returns the brain folder path for a channel context."""
    return ctx.path / "brain"

def get_themes_path(ctx) -> Path:
    """Returns the themes folder path."""
    return get_brain_path(ctx) / "themes"

def init_brain(ctx) -> bool:
    """
    Initialize brain folder structure for a channel.
    Creates: state.json, themes/ folder with theme files, learnings.md
    """
    brain_path = get_brain_path(ctx)
    brain_path.mkdir(exist_ok=True)
    
    themes_path = get_themes_path(ctx)
    themes_path.mkdir(exist_ok=True)
    
    now = datetime.now().isoformat()
    date_str = datetime.now().strftime('%Y-%m-%d')
    channel_name = ctx.name.replace('_', ' ').title()
    
    # Create state.json
    state_path = brain_path / "state.json"
    if not state_path.exists():
        state = DEFAULT_STATE.copy()
        state['updated_at'] = now
        state['identity']['name'] = channel_name
        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
    
    # Create theme files from built-in templates
    for theme_key, theme_data in BUILTIN_THEMES.items():
        theme_path = themes_path / f"{theme_key}.md"
        if not theme_path.exists():
            theme_content = f"""# {theme_data['name']} Theme

> Prompt formula and quality markers for {theme_data['name']} format.
> Last updated: {date_str}

## Format
{theme_data['format']}

## Vibe
{theme_data['vibe']}

## Prompt Formula
```
[STYLE]: {theme_data['style']}
[ACTION]: {theme_data['action']}
[PHYSICS]: {theme_data['physics']}
[CAMERA]: {theme_data['camera']}
```

## Script Style
{theme_data['script']}

## Anti-AI Tokens (Required)
- Subtle film grain, 16mm film texture
- Gentle handheld camera shake
- Atmospheric haze, dust particles
- Natural physics, weight and momentum

## Proven Hooks
| Pattern | Win Rate | Uses |
|---------|----------|------|
| (Track successful hooks here) | | |

## Notes
(Any learnings specific to this theme)
"""
            with open(theme_path, 'w', encoding='utf-8') as f:
                f.write(theme_content)
    
    # Create learnings.md
    learnings_path = brain_path / "learnings.md"
    if not learnings_path.exists():
        learnings = DEFAULT_LEARNINGS.format(channel_name=channel_name, date=date_str)
        with open(learnings_path, 'w', encoding='utf-8') as f:
            f.write(learnings)
    
    return True

def load_state(ctx) -> Dict[str, Any]:
    """Load current brain state (JSON)."""
    state_path = get_brain_path(ctx) / "state.json"
    if not state_path.exists():
        return DEFAULT_STATE.copy()
    
    with open(state_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_state(ctx, state: Dict[str, Any]) -> bool:
    """Save brain state (JSON)."""
    state['updated_at'] = datetime.now().isoformat()
    state_path = get_brain_path(ctx) / "state.json"
    
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2)
    return True

def load_playbook(ctx) -> str:
    """Load the active theme's markdown content."""
    state = load_state(ctx)
    active_theme = state.get('active_theme', 'loop')
    
    theme_path = get_themes_path(ctx) / f"{active_theme}.md"
    if not theme_path.exists():
        # Fallback to loop if active theme doesn't exist
        theme_path = get_themes_path(ctx) / "loop.md"
    
    if not theme_path.exists():
        return ""
    
    with open(theme_path, 'r', encoding='utf-8') as f:
        return f.read()

def list_themes(ctx) -> List[str]:
    """List all available themes for this channel."""
    themes_path = get_themes_path(ctx)
    if not themes_path.exists():
        return []
    return [f.stem for f in themes_path.glob("*.md")]

def load_learnings(ctx) -> str:
    """Load learnings markdown content."""
    learnings_path = get_brain_path(ctx) / "learnings.md"
    if not learnings_path.exists():
        return ""
    
    with open(learnings_path, 'r', encoding='utf-8') as f:
        return f.read()

def add_learning(ctx, category: str, insight: str, evidence: str = "") -> bool:
    """
    Add a new learning to the learnings.md file.
    Categories: performance, audience, gaps, failures
    """
    learnings_path = get_brain_path(ctx) / "learnings.md"
    if not learnings_path.exists():
        init_brain(ctx)
    
    content = load_learnings(ctx)
    
    # Map category to section header
    section_map = {
        "performance": "## Performance Insights",
        "audience": "## Audience Insights", 
        "gaps": "## Market Gaps",
        "failures": "## Failed Experiments"
    }
    
    section_header = section_map.get(category, "## Other")
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Build learning entry
    entry = f"\n- [{date_str}] {insight}"
    if evidence:
        entry += f" (Source: {evidence})"
    
    # Find section and append
    if section_header in content:
        # Insert after section header
        parts = content.split(section_header)
        if len(parts) >= 2:
            # Find the next section or end
            rest = parts[1]
            next_section = rest.find("\n## ")
            if next_section > 0:
                # Insert before next section
                new_rest = rest[:next_section].rstrip() + entry + rest[next_section:]
            else:
                # Append at end of section
                new_rest = rest.rstrip() + entry + "\n"
            content = parts[0] + section_header + new_rest
    else:
        # Section doesn't exist, add it
        content += f"\n\n{section_header}\n{entry}\n"
    
    with open(learnings_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def update_performance(ctx, stats: Dict[str, Any]) -> bool:
    """Update performance section of brain state."""
    state = load_state(ctx)
    state['performance'].update(stats)
    return save_state(ctx, state)

def update_audience(ctx, wants: List[str] = None, complaints: List[str] = None, sentiment: float = None) -> bool:
    """Update audience section of brain state."""
    state = load_state(ctx)
    if wants:
        # Merge, avoiding duplicates
        existing = set(state['audience'].get('wants', []))
        state['audience']['wants'] = list(existing.union(set(wants)))
    if complaints:
        existing = set(state['audience'].get('complaints', []))
        state['audience']['complaints'] = list(existing.union(set(complaints)))
    if sentiment is not None:
        state['audience']['sentiment'] = sentiment
    return save_state(ctx, state)

def set_active_theme(ctx, theme_name: str) -> bool:
    """Set the active theme in brain state."""
    state = load_state(ctx)
    state['active_theme'] = theme_name
    return save_state(ctx, state)

def get_prompt_context(ctx) -> str:
    """
    Generate the full prompt context from brain for kit creation.
    This is injected into kit prompts.
    """
    state = load_state(ctx)
    playbook = load_playbook(ctx)
    learnings = load_learnings(ctx)
    
    # Extract identity
    identity = state.get('identity', {})
    
    # Extract audience insights
    audience = state.get('audience', {})
    wants = audience.get('wants', [])
    complaints = audience.get('complaints', [])
    
    # Build context string
    context = f"""
## Channel Identity
- Name: {identity.get('name', 'Unknown')}
- Niche: {identity.get('niche', 'Not defined')}
- Audience: {identity.get('audience', 'Not defined')}
- Tone: {identity.get('tone', 'Not defined')}

## Active Theme: {state.get('active_theme', 'loop')}

{playbook}

## Audience Wants
{chr(10).join(['- ' + w for w in wants]) if wants else '- (No data yet)'}

## Audience Complaints (Avoid These)
{chr(10).join(['- ' + c for c in complaints]) if complaints else '- (No complaints recorded)'}

## Recent Learnings
{learnings[:2000] if learnings else '(No learnings yet)'}
"""
    return context

def brain_exists(ctx) -> bool:
    """Check if brain folder exists for this channel."""
    return get_brain_path(ctx).exists()
