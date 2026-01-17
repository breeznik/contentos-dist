"""Database module for ContentOS - SQLite + File hybrid system.

FILES (for humans to copy):
- production/XXX/script.txt
- production/XXX/prompt.txt
- production/XXX/kit.yaml

DATABASE (for AI to query):
- projects, scripts, prompts, assets tables
- Synced from files via `contentos db sync`
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

def get_db_path(context) -> Path:
    """Get database path for the active channel."""
    return context.analytics_path / "contentos.db"

def init_db(context):
    """Initialize the complete database schema."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ============ PROJECTS ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TEXT,
            status TEXT DEFAULT 'draft',
            video_id TEXT,
            published_at TEXT,
            hook_type TEXT,
            theme TEXT,
            audio_style TEXT,
            visual_style TEXT,
            physics_type TEXT,
            formula_version TEXT,
            views_24h INTEGER,
            views_7d INTEGER,
            views_30d INTEGER,
            likes INTEGER,
            retention_avg REAL,
            overall_rating TEXT,
            notes TEXT
        )
    ''')
    
    # ============ SCRIPTS ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            hook TEXT,
            visual_sequence TEXT,
            audio_direction TEXT,
            full_text TEXT
        )
    ''')
    
    # ============ PROMPTS ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            prompt_type TEXT,
            content TEXT
        )
    ''')
    
    # ============ ASSETS ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            slot TEXT,
            filename TEXT,
            prompt_used TEXT
        )
    ''')
    
    # ============ INGREDIENTS ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            type TEXT,
            id TEXT,
            name TEXT,
            description TEXT,
            PRIMARY KEY (type, id)
        )
    ''')
    
    # ============ COMMENTS (Community Sensing) ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            video_id TEXT,
            author_name TEXT,
            text_original TEXT,
            sentiment_score REAL,
            published_at TEXT,
            reply_count INTEGER,
            like_count INTEGER
        )
    ''')

    # ============ TRENDS (External Radar) ============
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            volume_score INTEGER,
            source TEXT,
            detected_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Auto-Migration Check
    check_migrations(context)
    
    return db_path

def check_migrations(context):
    """Checks and applies schema updates automatically."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Migration 1: Add published_at to projects if missing (Legacy Fix)
    try:
        cursor.execute("SELECT published_at FROM projects LIMIT 1")
    except sqlite3.OperationalError:
        print("🔧 Migrating DB: Adding 'published_at' column...")
        cursor.execute("ALTER TABLE projects ADD COLUMN published_at TEXT")
    
    conn.commit()
    conn.close()

def sync_project_to_db(context, project_path: Path):
    """Sync a single project folder to database."""
    import yaml
    
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    project_id = project_path.name.split('_')[0]
    project_name = '_'.join(project_path.name.split('_')[1:])
    
    # Read kit.yaml if exists
    kit_file = project_path / "kit.yaml"
    kit = {}
    if kit_file.exists():
        with open(kit_file, 'r') as f:
            kit = yaml.safe_load(f) or {}
    
    ingredients = kit.get('ingredients', {})
    performance = kit.get('performance', {})
    ratings = kit.get('ratings', {})
    
    # Insert/update project
    cursor.execute('''
        INSERT OR REPLACE INTO projects (
            id, name, created_at, status, video_id, published_at,
            hook_type, theme, audio_style, visual_style, physics_type, formula_version,
            views_24h, views_7d, views_30d, likes, retention_avg,
            overall_rating, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        kit.get('id', project_id),
        kit.get('name', project_name),
        kit.get('created'),
        kit.get('status', 'draft'),
        kit.get('video_id'),
        kit.get('published_at'),
        ingredients.get('hook_type'),
        ingredients.get('theme'),
        ingredients.get('audio_style'),
        ingredients.get('visual_style'),
        ingredients.get('physics_type'),
        ingredients.get('formula_version'),
        performance.get('views_24h'),
        performance.get('views_7d'),
        performance.get('views_30d'),
        performance.get('likes'),
        performance.get('retention_avg'),
        ratings.get('overall'),
        ratings.get('notes')
    ))
    
    # Read and sync script.txt
    script_file = project_path / "script.txt"
    if script_file.exists():
        with open(script_file, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        cursor.execute('DELETE FROM scripts WHERE project_id = ?', (project_id,))
        cursor.execute('''
            INSERT INTO scripts (project_id, full_text) VALUES (?, ?)
        ''', (project_id, script_text))
    
    # Read and sync prompt.txt
    prompt_file = project_path / "prompt.txt"
    if prompt_file.exists():
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
        
        cursor.execute('DELETE FROM prompts WHERE project_id = ?', (project_id,))
        cursor.execute('''
            INSERT INTO prompts (project_id, prompt_type, content) VALUES (?, ?, ?)
        ''', (project_id, 'full', prompt_text))
    
    # Sync assets
    cursor.execute('DELETE FROM assets WHERE project_id = ?', (project_id,))
    
    from core.templates import FORMULAS
    formula_name = ingredients.get('formula', 'stitch_2clip')
    formula_config = FORMULAS.get(formula_name, FORMULAS['stitch_2clip'])
    
    # Use slots defined in the Formula
    for slot_path_str in formula_config.get('slots', []):
        asset_path = project_path / slot_path_str
        if asset_path.exists():
            # slot name: "forward/start_frame.png" -> "forward_start_frame"
            slot_name = slot_path_str.replace('/', '_').replace('.png', '')
            cursor.execute('''
                INSERT INTO assets (project_id, slot, filename) VALUES (?, ?, ?)
            ''', (project_id, slot_name, str(asset_path)))
    
    conn.commit()
    conn.close()
    return True

def sync_all_projects(context):
    """Sync all project folders to database."""
    init_db(context)
    
    count = 0
    for project_dir in context.production_path.iterdir():
        if project_dir.is_dir() and project_dir.name[0].isdigit():
            sync_project_to_db(context, project_dir)
            count += 1
    
    return count

def query_projects(context, sql_where="1=1"):
    """Query projects from database."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT * FROM projects WHERE {sql_where} ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def query_scripts(context, project_id):
    """Get script for a project."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scripts WHERE project_id = ?', (project_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None

def get_ingredient_stats(context):
    """Get performance stats grouped by ingredient."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    results = {}
    for ingredient_type in ['hook_type', 'theme', 'audio_style', 'visual_style', 'physics_type']:
        cursor.execute(f'''
            SELECT 
                {ingredient_type} as ingredient,
                COUNT(*) as count,
                AVG(views_7d) as avg_views,
                AVG(retention_avg) as avg_retention,
                MAX(published_at) as max_published_at
            FROM projects 
            WHERE {ingredient_type} IS NOT NULL
            GROUP BY {ingredient_type}
            ORDER BY avg_views DESC
        ''')
        results[ingredient_type] = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    conn.close()
    return results

def get_channel_stats(context):
    """Get overall channel stats (avg views, video count)."""
    db_path = get_db_path(context)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Simple stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_videos,
            AVG(views_7d) as avg_views
        FROM projects 
        WHERE views_7d IS NOT NULL AND views_7d > 0
    ''')
    row = cursor.fetchone()
    stats = dict(row) if row else {'total_videos': 0, 'avg_views': 0}
    
    conn.close()
    return stats
