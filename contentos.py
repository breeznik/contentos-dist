#!/usr/bin/env python3
"""
ContentOS - Universal Multi-Channel YouTube Production CLI

Usage:
    python contentos.py <command> [options]

Commands:
    channel     Manage channels (list, use, create, status)
    sync        Update active channel's analytics
    kit         Manage production kits (create, list, publish)
    strategy    AI-driven recommendations (update, suggest)
"""

import argparse
import sys

from commands import channel_cmd, kit_cmd, sync_cmd, strategy_cmd, retention_cmd, health_cmd, scout_cmd, asset_cmd, db_cmd, scan_cmd, test_crew_cmd, config_cmd, archive_cmd, context_cmd, brain_cmd, boot_cmd, index_cmd, setup_cmd

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='contentos',
        description='ContentOS - Universal YouTube Production CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # --- Setup Command (First-time install) ---
    setup_parser = subparsers.add_parser('setup', help='Initialize ContentOS for first-time use')
    setup_parser.set_defaults(func=setup_cmd.run)

    # --- Boot Command (AI Onboarding) ---
    boot_parser = subparsers.add_parser('boot', help='Generate AI onboarding context')
    boot_parser.set_defaults(func=boot_cmd.run)

    # --- Index Command (Context Surfing) ---
    index_parser = subparsers.add_parser('index', help='Navigate system context')
    index_parser.add_argument('path', nargs='?', default='', help='Dot-notation path (e.g., brain.themes.loop)')
    index_parser.add_argument('--json', action='store_true', help='Output as JSON')
    index_parser.set_defaults(func=index_cmd.run)

    # --- Config Command ---
    config_parser = subparsers.add_parser('config', help='Manage system settings')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_subparsers.add_parser('show', help='Show current configuration')
    
    cfg_enable = config_subparsers.add_parser('enable', help='Enable a feature')
    cfg_enable.add_argument('feature_name', type=str, help='Feature name (e.g. llm_swarm)')
    
    cfg_disable = config_subparsers.add_parser('disable', help='Disable a feature')
    cfg_disable.add_argument('feature_name', type=str, help='Feature name')
    
    config_parser.set_defaults(func=config_cmd.run)

    # --- Archive Command ---
    archive_parser = subparsers.add_parser('archive', help='Manage kit archival')
    archive_subparsers = archive_parser.add_subparsers(dest='archive_action')
    
    archive_subparsers.add_parser('list', help='List kits eligible for archiving')
    
    archive_run = archive_subparsers.add_parser('run', help='Archive old kits')
    archive_run.add_argument('--all', action='store_true', help='Archive all eligible kits')
    archive_run.add_argument('--kit', dest='kit_id', type=str, help='Archive specific kit by ID')
    archive_run.add_argument('--force', action='store_true', help='Override age check')
    
    archive_restore = archive_subparsers.add_parser('restore', help='Restore archived kit')
    archive_restore.add_argument('--kit', dest='kit_id', type=str, help='Kit folder name to restore')
    
    archive_parser.set_defaults(func=archive_cmd.run)

    # --- Context Command ---
    context_parser = subparsers.add_parser('context', help='AI context management')
    context_subparsers = context_parser.add_subparsers(dest='context_action')
    
    context_subparsers.add_parser('show', help='Show context usage')
    context_subparsers.add_parser('optimize', help='Optimization suggestions')
    
    context_parser.set_defaults(func=context_cmd.run)

    # --- Brain Command ---
    brain_parser = subparsers.add_parser('brain', help='Channel knowledge system')
    brain_subparsers = brain_parser.add_subparsers(dest='brain_action')
    
    brain_subparsers.add_parser('init', help='Initialize brain for current channel')
    brain_subparsers.add_parser('show', help='Show brain state')
    brain_subparsers.add_parser('context', help='Show full prompt context')
    
    brain_theme = brain_subparsers.add_parser('set-theme', help='Set active theme')
    brain_theme.add_argument('theme_name', type=str, help='Theme name (loop, advice, cinematic)')
    
    brain_learn = brain_subparsers.add_parser('learn', help='Add manual learning')
    brain_learn.add_argument('category', type=str, help='Category: performance, audience, gaps, failures')
    brain_learn.add_argument('insight', type=str, help='The insight to add')
    
    brain_parser.set_defaults(func=brain_cmd.run)

    # --- Channel Command ---
    channel_parser = subparsers.add_parser('channel', help='Manage channels')
    channel_subparsers = channel_parser.add_subparsers(dest='channel_action')
    
    channel_subparsers.add_parser('list', help='List all channels')
    channel_subparsers.add_parser('status', help='Show active channel status')
    
    channel_use = channel_subparsers.add_parser('use', help='Switch active channel')
    channel_use.add_argument('name', type=str, help='Channel name')
    
    channel_create = channel_subparsers.add_parser('create', help='Create new channel')
    channel_create.add_argument('name', type=str, help='Channel name')
    channel_create.add_argument('--handle', type=str, help='YouTube handle')
    
    channel_parser.set_defaults(func=channel_cmd.run)

    # --- Sync Command ---
    sync_parser = subparsers.add_parser('sync', help='Sync analytics for active channel')
    sync_parser.add_argument('--auto-dna', '-a', action='store_true', 
                            help='Auto-update viral_dna.md after sync')
    sync_parser.add_argument('--all', dest='all_channels', action='store_true',
                            help='Sync ALL channels sequentially')
    sync_parser.set_defaults(func=sync_cmd.run)


    # --- Retention Command ---
    retention_parser = subparsers.add_parser('retention', help='Fetch retention curve')
    retention_parser.add_argument('--video', '-v', type=str, help='Video title to search')
    retention_parser.set_defaults(func=retention_cmd.run)

    # --- Health Command ---
    health_parser = subparsers.add_parser('health', help='System health & diagnostic checks')
    health_parser.set_defaults(func=health_cmd.run)

    # --- Scout Command ---
    scout_parser = subparsers.add_parser('scout', help='Research competitor videos')
    scout_parser.add_argument('--keyword', '-k', type=str, help='Custom keyword')
    scout_parser.set_defaults(func=scout_cmd.run)

    # --- Scan Command (Community) ---
    scan_parser = subparsers.add_parser('scan', help='Scan community & trends')
    scan_parser.add_argument('scan_target', type=str, choices=['comments'], help='Target to scan')
    scan_parser.set_defaults(func=scan_cmd.run)

    # --- Kit Command ---
    kit_parser = subparsers.add_parser('kit', help='Manage production kits')
    kit_subparsers = kit_parser.add_subparsers(dest='kit_action')
    
    kit_create = kit_subparsers.add_parser('create', help='Create a new kit')
    kit_create.add_argument('name', type=str, help='Kit name')
    kit_create.add_argument('--theme', '-t', type=str, 
                            choices=['loop', 'cinematic', 'voxel'], 
                            default='loop', help='Theme')
    kit_create.add_argument('--formula', '-f', type=str,
                            choices=['stitch_2clip', 'loop_circular', 'loop_boomerang', 'cinematic_4shot', 'fpp_narrative', 'fpp_short'],
                            default='stitch_2clip', help='Production Formula')
    
    kit_subparsers.add_parser('list', help='List all kits')
    
    kit_publish = kit_subparsers.add_parser('publish', help='Mark kit as published')
    kit_publish.add_argument('id', type=str, help='Kit ID')
    kit_publish.add_argument('--force', '-f', action='store_true', 
                            help='Override growth guardrails warnings')
    
    kit_link = kit_subparsers.add_parser('link', help='Auto-link YouTube videos to kits')
    kit_link.add_argument('--video', '-v', dest='video_id', type=str, help='YouTube video ID')
    kit_link.add_argument('--kit', '-k', dest='kit_id', type=str, help='Kit ID (e.g., 003)')
    
    kit_parser.set_defaults(func=kit_cmd.run)

    # --- Strategy Command ---
    strategy_parser = subparsers.add_parser('strategy', help='AI strategy recommendations')
    strategy_subparsers = strategy_parser.add_subparsers(dest='strategy_action')
    
    strategy_subparsers.add_parser('update', help='Update viral_dna.md')
    strategy_subparsers.add_parser('suggest', help='Get next video recommendation')
    
    strategy_parser.set_defaults(func=strategy_cmd.run)

    # --- Asset Command ---
    asset_parser = subparsers.add_parser('asset', help='Manage generated assets')
    asset_subparsers = asset_parser.add_subparsers(dest='asset_action')
    
    asset_subparsers.add_parser('list', help='List recent generated images')
    
    asset_place = asset_subparsers.add_parser('place', help='Place asset into kit')
    asset_place.add_argument('name', type=str, help='Image name (partial match)')
    asset_place.add_argument('--kit', '-k', type=str, required=True, help='Kit ID (e.g., 007)')
    asset_place.add_argument('--slot', '-s', type=str, required=True, 
                            help='Slot: fs (forward_start), fe (forward_end), rs (reverse_start), re (reverse_end)')
    
    asset_parser.set_defaults(func=asset_cmd.run)

    # --- Database Command ---
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_subparsers = db_parser.add_subparsers(dest='db_action')
    
    db_subparsers.add_parser('sync', help='Sync all projects to database')
    db_subparsers.add_parser('analyze', help='Analyze ingredient performance')
    db_subparsers.add_parser('query', help='Query projects')
    db_subparsers.add_parser('export', help='Export to JSON for cloud sync')
    
    db_parser.set_defaults(func=db_cmd.run)


    # --- Test Crew Command ---
    test_crew_parser = subparsers.add_parser('test-crew', help='Test LLM Swarm connectivity')
    test_crew_parser.set_defaults(func=test_crew_cmd.run)






    # --- Parse and Execute ---
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\n📺 Quick Start:")
        print("   contentos channel list")
        print("   contentos channel use rotnation")
        print("   contentos kit create 'neon_jelly' --theme loop")
        sys.exit(0)
    
    args.func(args)

if __name__ == '__main__':
    main()
