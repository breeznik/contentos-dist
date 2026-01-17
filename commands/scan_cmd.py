"""Scan command: Community and Trend sensing."""
import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.context import context_manager
from core.community import fetch_comments, analyze_community_sentiment
from core.database import get_db_path

BATCH_SIZE = 50  # Comments per LLM batch

def cmd_comments(args):
    """Scan recent video comments."""
    ctx = context_manager.get_current_context()
    if not ctx:
        print("No active channel.")
        return
        
    print(f"Scanning community frequency for {ctx.name}...")
    
    # Fetch
    count = fetch_comments(ctx, max_results=20)
    print(f"\nSynced {count} comments to database.")
    
    # Basic Analyze
    report = analyze_community_sentiment(ctx)
    
    print("\nCOMMUNITY PULSE")
    print("-------------------")
    print(f"Total Database: {report['total_comments']} comments")
    print(f"Sentiment Score: {report['average_sentiment']:.2f} (-1.0 to 1.0)")
    
    print("\nTop Voice (Most Liked):")
    for author, text, likes in report['top_comments']:
        safe_text = text[:60].encode('ascii', 'ignore').decode('ascii')
        print(f"   * {author} ({likes} likes): \"{safe_text}...\"")
    
    # --- LLM ANALYST INJECTION ---
    if ctx.global_config.features.llm_swarm:
        print("\nActivating The Analyst (Map-Reduce)...")
        run_analyst(ctx)
    else:
        print("\nThe Analyst disabled (Feature: llm_swarm=OFF).")
        print("Use 'contentos config enable llm_swarm' to unlock AI insights.")

def run_analyst(ctx):
    """Map-Reduce pattern for comment analysis."""
    from core.llm import ask
    
    # 1. Load ALL comments from DB
    conn = sqlite3.connect(get_db_path(ctx))
    cursor = conn.cursor()
    cursor.execute('SELECT text_original FROM comments ORDER BY like_count DESC LIMIT 500')
    all_comments = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if len(all_comments) < 5:
        print("Not enough comments for deep analysis (need 5+).")
        return

    print(f"   Loaded {len(all_comments)} comments.")
    
    # 2. MAP PHASE: Batch summaries
    batches = [all_comments[i:i+BATCH_SIZE] for i in range(0, len(all_comments), BATCH_SIZE)]
    batch_summaries = []
    
    print(f"   Running MAP phase ({len(batches)} batches)...")
    for i, batch in enumerate(batches):
        batch_text = "\n".join([f"- {c[:100]}" for c in batch])
        
        prompt = f"""
        Analyze these {len(batch)} YouTube comments.
        Extract: 
        1. Top 3 themes/topics mentioned.
        2. Key audience requests or questions.
        3. Negative feedback or complaints.
        
        Comments:
        {batch_text}
        
        Output: Concise bullet points only.
        """
        
        summary = ask(prompt, system="You are a community analyst.", temperature=0.5)
        batch_summaries.append(summary)
        print(f"     Batch {i+1}/{len(batches)} processed.")

    # 3. REDUCE PHASE: Aggregate
    print("   Running REDUCE phase...")
    all_summaries = "\n\n---\n\n".join(batch_summaries)
    
    reduce_prompt = f"""
    You have analyzed {len(all_comments)} YouTube comments in batches.
    Here are the batch summaries:
    
    {all_summaries}
    
    Now synthesize a FINAL ANALYST REPORT:
    1. **Dominant Themes**: What does this audience care about most?
    2. **Audience Requests**: What do they explicitly ask for?
    3. **Pain Points**: What are they complaining about?
    4. **Content Recommendations**: 2-3 specific video ideas based on this data.
    
    Output: Clean Markdown.
    """
    
    final_report = ask(reduce_prompt, system="You are a senior content strategist.", temperature=0.7)
    
    # 4. Print & Save
    print("\nANALYST REPORT:")
    safe_report = final_report.encode('ascii', 'ignore').decode('ascii')
    print(safe_report)
    
    # Save to strategy folder
    import datetime
    report_path = ctx.strategy_path / "analyst_report.md"
    with open(report_path, 'a', encoding='utf-8') as f:
        f.write(f"\n\n## Analyst Report: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Comments Analyzed**: {len(all_comments)}\n\n")
        f.write(final_report + "\n")
    
    print(f"\nReport saved to: {report_path.name}")
    
    # --- BRAIN INTEGRATION ---
    from core.brain import add_learning, brain_exists
    if brain_exists(ctx):
        add_learning(ctx, "audience", f"Analyst processed {len(all_comments)} comments - see analyst_report.md", evidence="Analyst Agent")
        print("Brain updated with audience insight.")

def run(args):
    """Entry point for scan command."""
    if args.scan_target == 'comments':
        cmd_comments(args)
    else:
        print("Usage: contentos scan {comments}")
