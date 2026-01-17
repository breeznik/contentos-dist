"""Kit management commands (context-aware)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.ledger import get_next_project_id, list_production_kits
from core.templates import create_kit_files
from core.brain import brain_exists, get_prompt_context, init_brain, list_themes

def cmd_create(args):
    """Create a new production kit."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    # --- Theme Selection ---
    if args.theme is None:
        if brain_exists(ctx):
            themes = list_themes(ctx)
            if themes:
                print(f"\nSelect Theme for '{args.name}':")
                for i, t in enumerate(themes):
                    print(f"  [{i+1}] {t}")
                
                try:
                    selection = input(f"\nEnter number (default 1): ").strip()
                    if not selection:
                        args.theme = themes[0]
                    else:
                        idx = int(selection) - 1
                        if 0 <= idx < len(themes):
                            args.theme = themes[idx]
                        else:
                            print("Invalid selection. Using default.")
                            args.theme = themes[0]
                except ValueError:
                    print("Invalid input. Using default.")
                    args.theme = themes[0]
            else:
                args.theme = "loop"
        else:
            args.theme = "loop"

    project_id = get_next_project_id(ctx)
    folder_name = f"{project_id}_{args.name.lower().replace(' ', '_')}"
    kit_path = ctx.production_path / folder_name
    
    # Load Viral DNA Strategy & AI Tokens
    strategy_text = ""
    
    # --- WILDCARD PROTOCOL (Prevent Local Maximums) ---
    is_wildcard = False
    try:
        pid_num = int(project_id)
        if pid_num > 0 and pid_num % 5 == 0:
            is_wildcard = True
            print(f"WILDCARD TRIGGERED (Kit {pid_num})")
            print("   • Ignoring Viral DNA")
            print("   • Injecting Experimental Strategy")
            
            strategy_text += "## EXPERIMENTAL WILDCARD\n"
            strategy_text += "DO NOT reuse past successful hooks or physics.\n"
            strategy_text += "You must TRY SOMETHING NEW to discover new viral ingredients.\n"
            strategy_text += "1. Use a completely new Hook type (e.g. 'Confrontational', 'Silent').\n"
            strategy_text += "2. Invert the usual Physics (e.g. if we usually Melt, trying Shattering).\n"
            strategy_text += "3. Change the Audio Landscape (e.g. Silence instead of Bass).\n\n"
    except:
        pass

    if not is_wildcard:
        # --- BRAIN INTEGRATION (Replaces legacy strategy loading) ---
        if brain_exists(ctx):
            # Pass the selected theme to ensure correct context is loaded
            brain_context = get_prompt_context(ctx, theme_override=args.theme)
            strategy_text += brain_context
            print(f"Injected Channel Brain context (Theme: {args.theme})")
        else:
            # Fallback: Initialize brain if not exists
            print("Brain not found. Initializing...")
            init_brain(ctx)
            brain_context = get_prompt_context(ctx, theme_override=args.theme)
            strategy_text += brain_context
            print(f"Brain initialized and context injected.")

    print(f"Creating kit: {args.name} (Theme: {args.theme}, Formula: {args.formula})")
    try:
        create_kit_files(kit_path, args.name, args.theme, args.formula, strategy=strategy_text)
    except Exception as e:
        print(f"Error creating kit files: {e}")
        return
    
    print(f"Created: {ctx.name}/production/{folder_name}/")
    print(f"   • script.txt ({args.theme} template)")
    print(f"   • prompt.txt ({args.formula} formula)")
    
    # FPP-SPECIFIC PROTOCOL HINT
    if args.formula in ['fpp_narrative', 'fpp_short']:
        clip_count = 8 if args.formula == 'fpp_narrative' else 3
        print(f"\n[FPP CINEMATOGRAPHY PROTOCOL]")
        print(f"   This is a {clip_count}-clip First-Person story. REQUIRED reading:")
        print(f"   Protocol: core/protocols/fpp_cinematography.md")
        print(f"   ")
        print(f"   CRITICAL: SEQUENTIAL IMAGE GENERATION")
        print(f"   DO NOT generate all images in parallel!")
        print(f"   ")
        print(f"   CORRECT WORKFLOW:")
        print(f"   1. Generate clip_01.png (standalone)")
        print(f"   2. STUDY clip_01 output (environment, hands, lighting)")
        print(f"   3. Generate clip_02.png using clip_01 as ImagePath reference")
        print(f"   4. Prompt must include: 'SAME EXACT environment as reference'")
        print(f"   5. Repeat for remaining clips")
        print(f"   ")
        print(f"   Key Settings:")
        print(f"   • Style: Stylized 3D graphics (NOT photorealistic)")
        print(f"   • Audio: 5 layers (Music+Ambient+SFX+Voice+Narrator)")
        print(f"   • Anti-Artifact: NO morphing, geometry LOCKED")
    
    from core.ui import print_ai_hint
    
    # Different hints for FPP vs standard
    if args.formula in ['fpp_narrative', 'fpp_short']:
        clip_count = 8 if args.formula == 'fpp_narrative' else 3
        print_ai_hint([
            f"SEQUENTIAL GENERATION: Generate clip_01 first, STUDY it, then chain others",
            f"{clip_count} images needed: Generate clip_01.png through clip_0{clip_count}.png",
            f"Use ImagePaths=[clip_01.png] for clips 02+",
            f"Prompt: 'SAME EXACT environment as reference image'"
        ])
    else:
        print_ai_hint([
            f"Inspect the prompt: view_file {kit_path}/prompt.txt",
            f"Generate assets: generate_image ...",
            f"Update Task List: Add '{args.name}' to task.md"
        ])

def cmd_list(args):
    """List all production kits."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    kits = list_production_kits(ctx)
    
    print(f"Production Kits for {ctx.config.name}:\n")
    
    if not kits:
        print("  (No kits found)")
        print(f"\n  Create one: contentos kit create <name> --theme loop")
        return
    
    print(f"{'ID':<5} {'Name':<30} {'Status':<15}")
    print("-" * 50)
    for k in kits:
        print(f"{k['id']:<5} {k['name']:<30} {k['status']:<15}")
    print(f"\nTotal: {len(kits)} kits")

def cmd_publish(args):
    """Mark a kit as published."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
    
    # Growth Guardrails Check
    from core.growth import check_safety, get_next_slot
    from core.auth import get_youtube_for_channel
    from commands.sync_cmd import get_channel_uploads, get_video_stats
    from datetime import datetime
    
    try:
        youtube = get_youtube_for_channel(ctx)
        playlist_id = get_channel_uploads(youtube)
        videos = get_video_stats(youtube, playlist_id, max_results=10) if playlist_id else []
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_count = sum(1 for v in videos if v.get('published_at', '').startswith(today_str))
        
        last_time = None
        if videos:
            sorted_vids = sorted(videos, key=lambda x: x.get('published_at', ''), reverse=True)
            try:
                last_time_str = sorted_vids[0].get('published_at')
                if last_time_str:
                    last_time = datetime.fromisoformat(last_time_str.replace('Z', '+00:00'))
            except:
                pass
        
        safety = check_safety(last_time, daily_count)
        if not safety['safe']:
            print("GROWTH GUARDRAILS WARNING:")
            for w in safety['warnings']:
                print(f"   [!] {w}")
            print(f"   Next safe slot: {get_next_slot()}")
            
            # Check for --force flag
            if hasattr(args, 'force') and args.force:
                print("   --force used. Overriding guardrails...")
            else:
                print("\n   BLOCKED. Use --force to override:")
                print(f"      python contentos.py kit publish {args.id} --force")
                return
    except Exception as e:
        print(f"Warning: Could not check growth guardrails: {e}")
    
    print(f"Marking kit {args.id} as published...")
    
    kits = list_production_kits(ctx)
    kit = next((k for k in kits if k['id'] == args.id), None)
    if not kit:
        print(f"Kit {args.id} not found")
        return

    import yaml
    kit_path = ctx.production_path / f"{kit['id']}_{kit['name']}"
    yaml_path = kit_path / "kit.yaml"
    
    if not yaml_path.exists():
        print(f"kit.yaml missing for {kit['name']}")
        return

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        data['status'] = 'published'
        data['published_at'] = datetime.now().isoformat()  # PUBLISH TIME TRACKING
        
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False)
            
        print(f"Kit {args.id} status updated to 'published'")
        print(f"   Timestamp: {data['published_at']}")
        
        # Auto-sync DB
        print("Updating database...")
        from commands import db_cmd
        db_cmd.cmd_sync(args)
        
    except Exception as e:
        print(f"Error updating kit: {e}")

def cmd_link(args):
    """Auto-link YouTube videos to kits by matching titles."""
    import yaml
    from core.auth import get_youtube_for_channel
    from commands.sync_cmd import get_channel_uploads, get_video_stats
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    print(f"Fetching videos from {ctx.config.name}...")
    
    try:
        youtube = get_youtube_for_channel(ctx)
        playlist_id = get_channel_uploads(youtube)
        
        if not playlist_id:
            print("Could not find channel uploads.")
            return
        
        videos = get_video_stats(youtube, playlist_id, max_results=50)
        kits = list_production_kits(ctx)
        linked = 0
        
        # Manual link mode: --video and --kit provided
        if hasattr(args, 'kit_id') and args.kit_id:
            # Auto-link fallback: Fetch latest video if ID missing
            target_video_id = args.video_id
            if not target_video_id and videos:
                print(f"Auto-Linking: Using latest video '{videos[0]['title']}'")
                target_video_id = videos[0]['id']
            elif not target_video_id:
                print("No videos found on channel to link.")
                return

            kit = next((k for k in kits if k['id'] == args.kit_id), None)
            if not kit:
                print(f"Kit {args.kit_id} not found")
                return
            
            kit_path = ctx.production_path / f"{kit['id']}_{kit['name']}"
            yaml_path = kit_path / "kit.yaml"
            
            with open(yaml_path, 'r', encoding='utf-8') as f:
                kit_data = yaml.safe_load(f)
            
            kit_data['video_id'] = target_video_id
            kit_data['status'] = 'published'
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(kit_data, f, default_flow_style=False, allow_unicode=True)
            
            print(f"Linked {kit['name']} -> {target_video_id}")
            return
        
        # Show available videos
        print(f"\nVideos on Channel ({len(videos)}):")
        print("-" * 60)
        for i, v in enumerate(videos):
            print(f"  [{i+1}] {v['title'][:45]}  (ID: {v['id']})")
        
        # Show kits needing links
        print(f"\nKits Needing Link:")
        print("-" * 60)
        unlinked = []
        for kit in kits:
            kit_path = ctx.production_path / f"{kit['id']}_{kit['name']}"
            yaml_path = kit_path / "kit.yaml"
            
            if yaml_path.exists():
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    kit_data = yaml.safe_load(f) or {}
                
                vid = kit_data.get('video_id') or 'TBD'
                if vid == 'TBD':
                    print(f"  [{kit['id']}] {kit['name']} → needs video_id")
                    unlinked.append(kit)
                else:
                    print(f"  [{kit['id']}] {kit['name']} -> {vid[:11]}")
        
        if unlinked and videos:
            print(f"\nTo link manually:")
            print(f"   python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID>")
            print(f"\n   Example: python contentos.py kit link --video {videos[0]['id']} --kit {unlinked[0]['id']}")
        elif unlinked:
            print(f"\nTo link manually:")
            print(f"   python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID>")
        else:
            print(f"\nLinked {linked} videos to kits")
        
        # --- Growth Check ---
        from core.growth import check_safety, get_next_slot
        from datetime import datetime
        
        # Count daily uploads
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_count = sum(1 for v in videos if v.get('published_at', '').startswith(today_str))
        
        # Get last publish time
        last_time = None
        if videos:
            # Sort by publishedAt just in case
            sorted_vids = sorted(videos, key=lambda x: x.get('published_at', ''), reverse=True)
            try:
                # Youtube returns ISO format like 2026-01-10T15:00:00Z
                last_time_str = sorted_vids[0].get('published_at')
                if last_time_str:
                    last_time = datetime.fromisoformat(last_time_str.replace('Z', '+00:00'))
            except:
                pass
        
        safety = check_safety(last_time, daily_count)
        print(f"\nGrowth Guardrails:")
        print(f"   • Daily Uploads: {daily_count}/3")
        print(f"   • Next Slot: {get_next_slot()}")
        
        if not safety['safe']:
            print("\nWARNINGS:")
            for w in safety['warnings']:
                print(f"   [!] {w}")
        else:
            print("\nSafe to post more!")

        if linked > 0:
            print("Auto-syncing database...")
            from commands import db_cmd
            db_cmd.cmd_sync(args)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print(f"   Copy client_secrets.json to {ctx.analytics_path}/")
    except Exception as e:
        print(f"Error: {e}")

def run(args):
    """Main entry point for kit command."""
    if args.kit_action == 'create':
        cmd_create(args)
    elif args.kit_action == 'list':
        cmd_list(args)
    elif args.kit_action == 'publish':
        cmd_publish(args)
    elif args.kit_action == 'link':
        cmd_link(args)
    else:
        print("Usage: contentos kit {create|list|publish|link}")
