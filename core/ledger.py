"""Ledger utilities for markdown parsing and writing."""
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

def get_analytics_path(context) -> Path:
    return context.strategy_path / f"{context.config.name.lower()}_analytics.md"

def get_viral_dna_path(context) -> Path:
    return context.strategy_path / f"{context.config.name.lower()}_viral_dna.md"

def get_market_research_path(context) -> Path:
    return context.strategy_path / f"{context.config.name.lower()}_market_research.md"

def get_next_project_id(context) -> str:
    """Scans production/ and returns the next available project ID."""
    production_dir = context.production_path
    if not production_dir.exists():
        return "001"
    
    existing = [d.name for d in production_dir.iterdir() if d.is_dir()]
    ids = []
    for name in existing:
        match = re.match(r'^(\d{3})_', name)
        if match:
            ids.append(int(match.group(1)))
    
    next_id = max(ids) + 1 if ids else 1
    return f"{next_id:03d}"

def read_file(file_path: Path) -> str:
    """Reads the entire content of a file."""
    if not file_path.exists():
        return ""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(file_path: Path, content: str) -> None:
    """Writes content to a file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def append_to_file(file_path: Path, content: str) -> None:
    """Appends content to a file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)

def parse_analytics_table(content: str) -> List[Dict]:
    """Parses the performance table from analytics.md."""
    lines = content.split('\n')
    data = []
    in_table = False
    
    for line in lines:
        if '| ID |' in line:
            in_table = True
            continue
        if in_table and line.startswith('|---'):
            continue
        if in_table and line.startswith('|'):
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) >= 6:
                views = parts[3].replace(',', '')
                likes = parts[4].replace(',', '')
                data.append({
                    'id': parts[0],
                    'title': parts[1],
                    'views': int(views) if views.isdigit() else 0,
                    'likes': int(likes) if likes.isdigit() else 0,
                    'score': parts[5]
                })
        elif in_table and not line.startswith('|'):
            in_table = False
    
    return data

def list_production_kits(context) -> List[Dict]:
    """Lists all kits in the production directory."""
    production_dir = context.production_path
    if not production_dir.exists():
        return []
    
    kits = []
    for item in sorted(production_dir.iterdir()):
        if item.is_dir():
            match = re.match(r'^(\d{3})_(.+)$', item.name)
            if match:
                yaml_path = item / 'kit.yaml'
                kit_status = 'setup'
                video_id = None
                
                if yaml_path.exists():
                    import yaml
                    try:
                        with open(yaml_path, 'r', encoding='utf-8') as f:
                            kit_data = yaml.safe_load(f) or {}
                            kit_status = kit_data.get('status', 'setup')
                            video_id = kit_data.get('video_id')
                    except:
                        pass
                
                has_script = (item / 'script.txt').exists()
                has_prompt = (item / 'prompt.txt').exists()
                from core.templates import FORMULAS
                formula_name = 'stitch_2clip'
                if yaml_path.exists():
                    try:
                        with open(yaml_path, 'r', encoding='utf-8') as f:
                            kit_data_yaml = yaml.safe_load(f) or {}
                            formula_name = kit_data_yaml.get('ingredients', {}).get('formula', 'stitch_2clip')
                    except:
                        pass

                f_config = FORMULAS.get(formula_name, FORMULAS['stitch_2clip'])
                # Check if ANY asset directory has files
                has_assets = False
                for d in f_config.get('dirs', []):
                    d_path = item / d
                    if d_path.exists() and any(d_path.iterdir()):
                        has_assets = True
                        break
                
                display_status = '🔧 Setup'
                if has_script and has_prompt and has_assets:
                    if video_id and video_id != 'TBD':
                        display_status = '✅ Published'
                    else:
                        display_status = '⏳ Pending'
                elif not has_script:
                    display_status = '📦 Empty'
                
                kits.append({
                    'id': match.group(1),
                    'name': match.group(2),
                    'path': item,
                    'status': display_status
                })
    
    return kits
