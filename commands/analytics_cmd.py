"""
ContentOS: Analytics Command
Fetch and display deep analytics for the active channel.

Usage:
    python contentos.py analytics fetch
    python contentos.py analytics report
    python contentos.py analytics compare
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analytics import AnalyticsFetcher
from core.context import context_manager


def cmd_fetch(args):
    """Fetch latest analytics for active channel."""
    ctx = context_manager.get_current_context()
    print(f"\n📊 Fetching analytics for {ctx.name}...")
    
    fetcher = AnalyticsFetcher(ctx.path)
    days = int(args.days) if hasattr(args, 'days') and args.days else 30
    
    summary = fetcher.get_summary(days)
    print(summary)
    
    # Save to strategy file
    output_path = ctx.strategy_path / f"{ctx.name}_analytics_deep.md"
    with open(output_path, 'w') as f:
        f.write(f"# Deep Analytics Report\n\n**Generated:** {__import__('datetime').datetime.now().isoformat()}\n\n")
        f.write(summary)
    
    print(f"📁 Saved to: {output_path.relative_to(ctx.path.parent.parent)}")


def cmd_report(args):
    """Generate detailed analytics report."""
    ctx = context_manager.get_current_context()
    fetcher = AnalyticsFetcher(ctx.path)
    
    print(f"\n📈 Generating report for {ctx.name}...")
    
    # Fetch per-video metrics
    videos = fetcher.fetch_video_metrics(30)
    
    if videos:
        print("\n🎬 Top Videos (Last 30 Days):\n")
        print("| Video ID | Views | Watch Time (min) | Avg. Duration |")
        print("|----------|-------|------------------|---------------|")
        for v in videos[:10]:
            print(f"| {v.get('video', 'N/A')[:11]} | {v.get('views', 0):,} | {v.get('estimatedMinutesWatched', 0):,.0f} | {v.get('averageViewDuration', 0):.1f}s |")
    else:
        print("❌ No video data found.")


def cmd_compare(args):
    """Compare analytics across all channels."""
    from pathlib import Path
    channels_dir = Path(__file__).parent.parent / "channels"
    
    print("\n📊 Cross-Channel Comparison (30 Days)\n")
    print("| Channel | Views | Watch Time | Subs Gained |")
    print("|---------|-------|------------|-------------|")
    
    for channel_path in channels_dir.iterdir():
        if not (channel_path / ".channel.json").exists():
            continue
        
        try:
            fetcher = AnalyticsFetcher(channel_path)
            metrics = fetcher.fetch_channel_metrics(30)
            totals = metrics.get('totals', {})
            print(f"| {channel_path.name} | {totals.get('views', 0):,} | {totals.get('estimatedMinutesWatched', 0):,.0f}m | +{totals.get('subscribersGained', 0)} |")
        except Exception as e:
            print(f"| {channel_path.name} | Error: {e} |")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ContentOS Analytics")
    subparsers = parser.add_subparsers(dest='command')
    
    # fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch analytics')
    fetch_parser.add_argument('--days', type=int, default=30, help='Number of days')
    
    # report command
    subparsers.add_parser('report', help='Generate detailed report')
    
    # compare command
    subparsers.add_parser('compare', help='Compare all channels')
    
    args = parser.parse_args()
    
    if args.command == 'fetch':
        cmd_fetch(args)
    elif args.command == 'report':
        cmd_report(args)
    elif args.command == 'compare':
        cmd_compare(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
