#!/usr/bin/env python3
"""
Analyze Bookmap level response statistics.

Generates stats-report.md with:
- Success rate per level type
- Average move size per type
- Time-of-day correlation
- Confluence effect analysis
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_stats(path: Path) -> dict:
    if not path.exists():
        return {"logs": []}
    return json.loads(path.read_text())

def analyze(logs: list) -> dict:
    if not logs:
        return {}
    
    results = {
        "total_logs": len(logs),
        "by_level_type": defaultdict(lambda: {"count": 0, "bounces": 0, "moves": []}),
        "by_symbol": defaultdict(lambda: {"count": 0, "bounces": 0}),
        "by_time": defaultdict(lambda: {"count": 0, "bounces": 0}),
        "confluence_effect": {"single": {"count": 0, "bounces": 0}, "multiple": {"count": 0, "bounces": 0}},
    }
    
    for log in logs:
        response = log.get("response")
        is_success = response in ["bounce", "rejection"]
        
        # By level type
        level_type = log.get("level_type", "unknown")
        results["by_level_type"][level_type]["count"] += 1
        if is_success:
            results["by_level_type"][level_type]["bounces"] += 1
        if "move_size" in log:
            results["by_level_type"][level_type]["moves"].append(log["move_size"])
        
        # By symbol
        symbol = log.get("symbol", "unknown")
        results["by_symbol"][symbol]["count"] += 1
        if is_success:
            results["by_symbol"][symbol]["bounces"] += 1
        
        # By time context
        time_ctx = log.get("time_context", "other")
        results["by_time"][time_ctx]["count"] += 1
        if is_success:
            results["by_time"][time_ctx]["bounces"] += 1
        
        # Confluence
        confluence = log.get("confluence", [])
        if len(confluence) <= 1:
            results["confluence_effect"]["single"]["count"] += 1
            if is_success:
                results["confluence_effect"]["single"]["bounces"] += 1
        else:
            results["confluence_effect"]["multiple"]["count"] += 1
            if is_success:
                results["confluence_effect"]["multiple"]["bounces"] += 1
    
    return results

def generate_report(results: dict) -> str:
    lines = [
        "# Bookmap Level Statistics Report",
        f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"\n## Overview\n",
        f"Total logged responses: **{results.get('total_logs', 0)}**",
    ]
    
    # Success rate by level type
    lines.append("\n## Success Rate by Level Type\n")
    lines.append("| Level Type | Count | Bounces | Success % | Avg Move |")
    lines.append("|------------|-------|---------|-----------|----------|")
    
    by_type = results.get("by_level_type", {})
    sorted_types = sorted(by_type.items(), key=lambda x: x[1]["bounces"] / max(x[1]["count"], 1), reverse=True)
    
    for level_type, data in sorted_types:
        count = data["count"]
        bounces = data["bounces"]
        success_pct = (bounces / count * 100) if count > 0 else 0
        avg_move = sum(data["moves"]) / len(data["moves"]) if data["moves"] else 0
        lines.append(f"| {level_type} | {count} | {bounces} | {success_pct:.1f}% | {avg_move:.1f} |")
    
    # By symbol
    lines.append("\n## Success Rate by Symbol\n")
    lines.append("| Symbol | Count | Bounces | Success % |")
    lines.append("|--------|-------|---------|-----------|")
    
    by_symbol = results.get("by_symbol", {})
    for symbol, data in sorted(by_symbol.items()):
        count = data["count"]
        bounces = data["bounces"]
        success_pct = (bounces / count * 100) if count > 0 else 0
        lines.append(f"| {symbol} | {count} | {bounces} | {success_pct:.1f}% |")
    
    # Time context
    lines.append("\n## Time-of-Day Effect\n")
    lines.append("| Context | Count | Bounces | Success % |")
    lines.append("|---------|-------|---------|-----------|")
    
    by_time = results.get("by_time", {})
    for time_ctx, data in sorted(by_time.items()):
        count = data["count"]
        bounces = data["bounces"]
        success_pct = (bounces / count * 100) if count > 0 else 0
        lines.append(f"| {time_ctx} | {count} | {bounces} | {success_pct:.1f}% |")
    
    # Confluence effect
    lines.append("\n## Confluence Effect\n")
    conf = results.get("confluence_effect", {})
    
    single = conf.get("single", {})
    single_pct = (single.get("bounces", 0) / max(single.get("count", 1), 1) * 100)
    
    multiple = conf.get("multiple", {})
    multiple_pct = (multiple.get("bounces", 0) / max(multiple.get("count", 1), 1) * 100)
    
    lines.append(f"- **Single level:** {single.get('count', 0)} logs, {single_pct:.1f}% success")
    lines.append(f"- **Multiple confluence:** {multiple.get('count', 0)} logs, {multiple_pct:.1f}% success")
    
    if multiple_pct > single_pct:
        improvement = multiple_pct - single_pct
        lines.append(f"\n✅ **Confluence improves success rate by {improvement:.1f} percentage points**")
    
    lines.append("\n---\n*Update statistics with `python3 analyze_stats.py`*")
    
    return "\n".join(lines)

def main():
    stats_path = Path(__file__).parent / "level-stats.json"
    data = load_stats(stats_path)
    logs = data.get("logs", [])
    
    if not logs:
        print("⚠ No log entries found. Add entries with log_level.py first.")
        return
    
    results = analyze(logs)
    report = generate_report(results)
    
    report_path = Path(__file__).parent / "stats-report.md"
    report_path.write_text(report)
    
    print(f"✓ Generated report: {report_path}")
    print(f"  Analyzed {len(logs)} log entries")

if __name__ == "__main__":
    main()
