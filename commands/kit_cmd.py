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
            # Fallback: Initialize brain if not exists
            print("Brain not found. Initializing...")
            init_brain(ctx)
            brain_context = get_prompt_context(ctx, theme_override=args.theme)
            strategy_text += brain_context
            print(f"Brain initialized and context injected.")

        # --- LOAD CHANNEL PROTOCOLS ---
        protocol_path = ctx.brain_path / "protocols.md"
        if protocol_path.exists():
            print(f"\n[!] CHANNEL PROTOCOL DETECTED: {protocol_path.name}")
            try:
                proto_content = protocol_path.read_text(encoding='utf-8')
                strategy_text += "\n\n## CHANNEL PROTOCOLS\n" + proto_content + "\n"
                
                # Extract and print critical sections for the AI/User to see IMMEDIATELY
                print("    > MANDATORY RULES:")
                lines = proto_content.split('\n')
                for line in lines:
                    if "❌" in line or "✅" in line or "CRITICAL" in line:
                        print(f"      {line.strip()}")
            except Exception as e:
                print(f"    Error reading protocol: {e}")

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
            
            # Support --short flag for Shorts vs Video linking
            is_short = hasattr(args, 'short') and args.short
            if is_short:
                kit_data['video_id_short'] = target_video_id
                print(f"Linked {kit['name']} (SHORT) -> {target_video_id}")
            else:
                kit_data['video_id'] = target_video_id
                print(f"Linked {kit['name']} (VIDEO) -> {target_video_id}")
            
            kit_data['status'] = 'published'
            
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(kit_data, f, default_flow_style=False, allow_unicode=True)
            
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
                vid_short = kit_data.get('video_id_short') or 'TBD'
                
                if vid == 'TBD' and vid_short == 'TBD':
                    print(f"  [{kit['id']}] {kit['name']} → needs linking")
                    unlinked.append(kit)
                else:
                    vid_display = vid[:11] if vid != 'TBD' else '---'
                    short_display = vid_short[:11] if vid_short != 'TBD' else '---'
                    print(f"  [{kit['id']}] {kit['name']} -> V:{vid_display} | S:{short_display}")
        
        if unlinked and videos:
            print(f"\nTo link manually:")
            print(f"   Video:  python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID>")
            print(f"   Short:  python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID> --short")
            print(f"\n   Example: python contentos.py kit link --video {videos[0]['id']} --kit {unlinked[0]['id']}")
        elif unlinked:
            print(f"\nTo link manually:")
            print(f"   Video:  python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID>")
            print(f"   Short:  python contentos.py kit link --video <VIDEO_ID> --kit <KIT_ID> --short")
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

def cmd_enrich(args):
    """Use LLM to extract DNA ingredients from prompt.txt and update kit.yaml."""
    import yaml
    import json
    import re
    from core.llm import ask, ensure_ollama_running
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel. Run: contentos channel use <name>")
        return
    
    # Ensure LLM is available (auto-starts Ollama if needed)
    llm_available = ensure_ollama_running()
    if not llm_available:
        print("[!] LLM not available. Using pattern-based extraction.")
    
    kits = list_production_kits(ctx)
    
    # If specific kit ID provided, only process that one
    if hasattr(args, 'kit_id') and args.kit_id:
        kits = [k for k in kits if k['id'] == args.kit_id]
        if not kits:
            print(f"Kit {args.kit_id} not found")
            return
    
    enriched_count = 0
    
    for kit in kits:
        kit_path = ctx.production_path / f"{kit['id']}_{kit['name']}"
        prompt_path = kit_path / "prompt.txt"
        yaml_path = kit_path / "kit.yaml"
        
        if not prompt_path.exists():
            continue
        
        if not yaml_path.exists():
            print(f"[!] {kit['id']} has no kit.yaml, skipping")
            continue
        
        # Read prompt
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Read current kit.yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            kit_data = yaml.safe_load(f) or {}
        
        # Check if already enriched
        ingredients = kit_data.get('ingredients', {})
        if ingredients.get('hook_type') and ingredients.get('audio_style'):
            if not (hasattr(args, 'force') and args.force):
                print(f"[✓] {kit['id']} already enriched, skipping (use --force to re-analyze)")
                continue
        
        print(f"[*] Analyzing {kit['id']}_{kit['name']}...")
        
        extracted = None
        
        # Try LLM first if available
        if llm_available:
            extraction_prompt = f"""Analyze this video production prompt and extract the DNA ingredients.

PROMPT CONTENT:
{prompt_content[:3000]}

Extract these ingredients as a JSON object:
{{
    "hook_type": "<one of: POV_Emotional, POV_Relatable, Question, Statement, Confrontational, Silent, Tutorial>",
    "audio_style": "<one of: ASMR_Purr, Ambient_Silence, Music_Emotional, Music_Upbeat, SFX_Heavy, Voiceover>",
    "visual_style": "<one of: Macro_Closeup, Wide_Establishing, POV_FirstPerson, Handheld_Raw, Cinematic_Smooth, Loop_Seamless>",
    "physics_type": "<one of: Organic_Motion, Rigid_Body, Fluid_Sim, Particle_FX, Static_Hold, None>",
    "emotion": "<primary emotion: Trust, Love, Curiosity, Satisfaction, Nostalgia, FOMO, Humor>",
    "duration_seconds": <number>,
    "clip_count": <number>
}}

Return ONLY valid JSON, no explanation."""

            try:
                result = ask(extraction_prompt, 
                            system="You are a content analyst. Extract structured data from video prompts. Return only valid JSON.",
                            temperature=0.3,
                            json_mode=True)
                extracted = json.loads(result)
            except:
                print("   [!] LLM failed, falling back to pattern extraction")
        
        # Fallback: Pattern-based extraction
        if not extracted:
            extracted = _extract_patterns(prompt_content)
            print("   (Using pattern-based extraction)")
        
        if extracted:
            # Update ingredients in kit.yaml
            if 'ingredients' not in kit_data:
                kit_data['ingredients'] = {}
            
            kit_data['ingredients']['hook_type'] = extracted.get('hook_type', 'Unknown')
            kit_data['ingredients']['audio_style'] = extracted.get('audio_style', 'Unknown')
            kit_data['ingredients']['visual_style'] = extracted.get('visual_style', 'Unknown')
            kit_data['ingredients']['physics_type'] = extracted.get('physics_type', 'None')
            kit_data['ingredients']['emotion'] = extracted.get('emotion', 'Unknown')
            kit_data['ingredients']['duration'] = extracted.get('duration_seconds', 16)
            kit_data['ingredients']['clip_count'] = extracted.get('clip_count', 2)
            
            # Write updated kit.yaml
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(kit_data, f, default_flow_style=False, allow_unicode=True)
            
            print(f"   ✓ Extracted: {extracted.get('hook_type')} + {extracted.get('emotion')} + {extracted.get('audio_style')}")
            enriched_count += 1
    
    print(f"\n>> Enriched {enriched_count} kits with DNA ingredients.")
    
    if enriched_count > 0:
        print(">> Syncing to database...")
        from commands import db_cmd
        db_cmd.cmd_sync(args)
        
        from core.ui import print_ai_hint
        print_ai_hint([
            "Analyze ingredient performance: python contentos.py db analyze",
            "View updated kits: python contentos.py kit list"
        ])

def _extract_patterns(prompt_content: str) -> dict:
    """Fallback pattern-based extraction when LLM is unavailable."""
    import re
    
    content_lower = prompt_content.lower()
    
    # Hook Type Detection
    hook_type = "Unknown"
    if "pov" in content_lower or "pov:" in content_lower:
        if any(w in content_lower for w in ["adopt", "chose", "love", "trust", "emotional"]):
            hook_type = "POV_Emotional"
        else:
            hook_type = "POV_Relatable"
    elif "?" in prompt_content[:200]:
        hook_type = "Question"
    elif "tutorial" in content_lower or "how to" in content_lower:
        hook_type = "Tutorial"
    
    # Audio Style Detection
    audio_style = "Ambient_Silence"
    if "asmr" in content_lower or "purr" in content_lower:
        audio_style = "ASMR_Purr"
    elif "music" in content_lower:
        audio_style = "Music_Emotional"
    elif "voiceover" in content_lower or "narrator" in content_lower:
        audio_style = "Voiceover"
    
    # Visual Style Detection
    visual_style = "Handheld_Raw"
    if "macro" in content_lower or "close-up" in content_lower or "closeup" in content_lower:
        visual_style = "Macro_Closeup"
    elif "pov" in content_lower or "first person" in content_lower:
        visual_style = "POV_FirstPerson"
    elif "loop" in content_lower or "seamless" in content_lower:
        visual_style = "Loop_Seamless"
    elif "cinematic" in content_lower:
        visual_style = "Cinematic_Smooth"
    elif "handheld" in content_lower or "home video" in content_lower:
        visual_style = "Handheld_Raw"
    
    # Physics Type Detection
    physics_type = "Organic_Motion"
    if "rigid" in content_lower:
        physics_type = "Rigid_Body"
    elif "fluid" in content_lower or "water" in content_lower:
        physics_type = "Fluid_Sim"
    elif "particle" in content_lower:
        physics_type = "Particle_FX"
    elif "static" in content_lower:
        physics_type = "Static_Hold"
    
    # Emotion Detection
    emotion = "Trust"
    emotion_map = {
        "love": "Love", "trust": "Trust", "curious": "Curiosity",
        "satisfy": "Satisfaction", "nostalg": "Nostalgia", 
        "fomo": "FOMO", "humor": "Humor", "funny": "Humor",
        "adopt": "Love", "emotional": "Love", "dream": "Curiosity"
    }
    for keyword, emo in emotion_map.items():
        if keyword in content_lower:
            emotion = emo
            break
    
    # Duration Detection
    duration_match = re.search(r'(\d+)\s*(?:second|sec|s\b)', content_lower)
    duration = int(duration_match.group(1)) if duration_match else 16
    
    # Clip Count Detection
    clip_match = re.search(r'(\d+)\s*(?:clip|scene|segment)', content_lower)
    clip_count = int(clip_match.group(1)) if clip_match else 2
    
    return {
        "hook_type": hook_type,
        "audio_style": audio_style,
        "visual_style": visual_style,
        "physics_type": physics_type,
        "emotion": emotion,
        "duration_seconds": duration,
        "clip_count": clip_count
    }

def cmd_suggest(args):
    """Get kit suggestions based on performance data."""
    import sqlite3
    from core.database import get_db_path, init_db
    
    ctx = context_manager.get_current_context()
    if not ctx:
        print("[!] No active channel.")
        return
    
    init_db(ctx)
    db_path = get_db_path(ctx)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get baseline channel stats
    cursor.execute('''
        SELECT AVG(views_7d) as baseline FROM projects 
        WHERE views_7d IS NOT NULL AND views_7d > 0
    ''')
    baseline = cursor.fetchone()['baseline'] or 100
    
    if getattr(args, 'predict', False):
        print(">> PREDICTIVE ENGINE: Ingredient Scoring\n")
        print(f"Channel Baseline: {baseline:.0f} avg views\n")
        
        # Calculate performance score for each ingredient
        ingredient_scores = {}
        for ing_type in ['hook_type', 'theme', 'audio_style', 'visual_style']:
            cursor.execute(f'''
                SELECT {ing_type} as ingredient, AVG(views_7d) as avg_views, COUNT(*) as count
                FROM projects 
                WHERE {ing_type} IS NOT NULL AND views_7d > 0
                GROUP BY {ing_type}
            ''')
            for row in cursor.fetchall():
                if row['ingredient']:
                    score = (row['avg_views'] / baseline) * 100 if baseline > 0 else 0
                    key = f"{ing_type}:{row['ingredient']}"
                    ingredient_scores[key] = {
                        'score': score,
                        'views': row['avg_views'],
                        'count': row['count']
                    }
        
        # Sort and display top ingredients
        sorted_scores = sorted(ingredient_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        print(f"{'Ingredient':<35} {'Score':<10} {'Avg Views':<12} {'Videos':<8}")
        print("-" * 70)
        
        for key, data in sorted_scores[:10]:
            ing_type, ing_name = key.split(':')
            score_display = f"{data['score']:.0f}%" if data['score'] <= 200 else f"{data['score']:.0f}%*"
            print(f"{ing_name[:35]:<35} {score_display:<10} {data['views']:<12.0f} {data['count']:<8}")
        
        print("\n[LEGEND] Score = (Ingredient Avg Views / Channel Baseline) * 100")
        print("         100% = average, >100% = above average, <100% = below average")
        
        # Generate top recommendation
        if sorted_scores:
            top = sorted_scores[0]
            ing_type, ing_name = top[0].split(':')
            print(f"\n[RECOMMENDED] Use '{ing_name}' ({ing_type}) for your next kit!")
            print(f"              Predicted views: {top[1]['views']:.0f}")
    else:
        # Simple suggestion mode (no prediction)
        print(">> KIT SUGGESTIONS\n")
        print("Run with --predict to see ingredient scoring.")
        print("\nQuick tips based on your data:")
        
        cursor.execute('''
            SELECT theme, AVG(views_7d) as avg FROM projects 
            WHERE views_7d > 0 GROUP BY theme ORDER BY avg DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        if row and row['theme']:
            print(f"   - Best theme: {row['theme']} ({row['avg']:.0f} avg views)")
        
        cursor.execute('''
            SELECT hook_type, AVG(views_7d) as avg FROM projects 
            WHERE views_7d > 0 GROUP BY hook_type ORDER BY avg DESC LIMIT 1
        ''')
        row = cursor.fetchone()
        if row and row['hook_type']:
            print(f"   - Best hook: {row['hook_type']} ({row['avg']:.0f} avg views)")
    
    conn.close()


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
    elif args.kit_action == 'enrich':
        cmd_enrich(args)
    elif args.kit_action == 'suggest':
        cmd_suggest(args)
    else:
        print("Usage: contentos kit {create|list|publish|link|enrich|suggest}")
