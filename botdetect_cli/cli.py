#!/usr/bin/env python3
"""
BotDetect-CLI - Main CLI Entry Point
Lightweight Browser Automation Detection Signal Analysis Engine
"""

import argparse
import json
import sys
import os
from datetime import datetime
from typing import Optional

from botdetect_cli import __version__, __description__
from botdetect_cli.detector import BotDetector, DetectionConfig, DetectionMode
from botdetect_cli.reporter import ReportGenerator
from botdetect_cli.scanner import SignalScanner


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser"""
    parser = argparse.ArgumentParser(
        prog="botdetect",
        description="🔍 BotDetect-CLI - Lightweight Browser Automation Detection Signal Analysis Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  botdetect scan                    # Run standard scan
  botdetect scan --mode quick       # Quick scan (essential signals only)
  botdetect scan --mode deep        # Deep scan with behavioral analysis
  botdetect scan --browser firefox  # Test Firefox detection
  botdetect scan --headed           # Test in headed mode
  botdetect report --format html    # Generate HTML report
  botdetect tui                     # Launch TUI dashboard

For more information: https://github.com/gitstq/botdetect-cli
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Scan command
    scan_parser = subparsers.add_parser(
        "scan",
        help="Run detection scan",
        description="Run a detection scan to analyze browser automation signals"
    )
    scan_parser.add_argument(
        "--mode", "-m",
        choices=["quick", "standard", "deep", "stealth"],
        default="standard",
        help="Detection mode (default: standard)"
    )
    scan_parser.add_argument(
        "--browser", "-b",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser type to test (default: chromium)"
    )
    scan_parser.add_argument(
        "--headed",
        action="store_true",
        help="Run in headed mode (non-headless)"
    )
    scan_parser.add_argument(
        "--url", "-u",
        help="Target URL to analyze"
    )
    scan_parser.add_argument(
        "--output", "-o",
        help="Output file path (without extension)"
    )
    scan_parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "html", "text"],
        default="json",
        help="Output format (default: json)"
    )
    scan_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Report command
    report_parser = subparsers.add_parser(
        "report",
        help="Generate report",
        description="Generate a formatted report from scan results"
    )
    report_parser.add_argument(
        "--format", "-f",
        choices=["json", "markdown", "html", "text"],
        default="html",
        help="Report format (default: html)"
    )
    report_parser.add_argument(
        "--output", "-o",
        help="Output file path (without extension)"
    )
    
    # TUI command
    tui_parser = subparsers.add_parser(
        "tui",
        help="Launch TUI dashboard",
        description="Launch the terminal user interface dashboard"
    )
    tui_parser.add_argument(
        "--browser", "-b",
        choices=["chromium", "firefox", "webkit"],
        default="chromium",
        help="Browser type to test (default: chromium)"
    )
    
    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List available signals",
        description="List all available detection signals"
    )
    list_parser.add_argument(
        "--category", "-c",
        help="Filter by category"
    )
    list_parser.add_argument(
        "--severity", "-s",
        help="Filter by severity"
    )
    
    # Compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare browsers",
        description="Compare detection scores across different browsers"
    )
    compare_parser.add_argument(
        "--url", "-u",
        help="Target URL to analyze"
    )
    
    return parser


def cmd_scan(args) -> int:
    """Execute scan command"""
    mode_map = {
        "quick": DetectionMode.QUICK,
        "standard": DetectionMode.STANDARD,
        "deep": DetectionMode.DEEP,
        "stealth": DetectionMode.STEALTH
    }
    
    config = DetectionConfig(
        mode=mode_map[args.mode],
        browser_type=args.browser,
        headless=not args.headed,
        verbose=args.verbose,
        output_format=args.format,
        output_file=args.output
    )
    
    detector = BotDetector(config)
    
    print(f"🔍 BotDetect-CLI v{__version__}")
    print(f"   Mode: {args.mode}")
    print(f"   Browser: {args.browser}")
    print(f"   Headless: {not args.headed}")
    print()
    
    if args.verbose:
        print("Running detection scan...")
    
    report = detector.detect(args.url)
    
    # Print summary
    print("=" * 60)
    print("                    DETECTION RESULTS")
    print("=" * 60)
    print(f"  Detection Score:  {report.scan_result.detection_score}%")
    print(f"  Evasion Score:    {report.evasion_score}%")
    print(f"  Risk Level:       {report.scan_result.risk_level}")
    print(f"  Detected Signals: {report.scan_result.detected_signals}/{report.scan_result.total_signals}")
    print(f"  Duration:         {report.duration_seconds}s")
    print("=" * 60)
    print()
    
    # Print detected signals
    detected = [s for s in report.scan_result.signals if s.detected]
    if detected:
        print("🚨 DETECTED SIGNALS:")
        print("-" * 60)
        
        # Group by severity
        severity_order = ["critical", "high", "medium", "low", "info"]
        severity_emoji = {
            "critical": "🚨",
            "high": "⚠️",
            "medium": "ℹ️",
            "low": "💡",
            "info": "📌"
        }
        
        for severity in severity_order:
            signals = [s for s in detected if s.severity.value == severity]
            if signals:
                emoji = severity_emoji.get(severity, "📌")
                print(f"\n{emoji} {severity.upper()} ({len(signals)})")
                for signal in signals:
                    print(f"  • {signal.name}: {signal.description[:50]}...")
        
        print()
    
    # Print recommendations
    if report.recommendations:
        print("💡 RECOMMENDATIONS:")
        print("-" * 60)
        for rec in report.recommendations:
            print(f"  {rec}")
        print()
    
    # Save report
    if args.output:
        generator = ReportGenerator()
        filepath = generator.generate(report, args.format, args.output)
        print(f"📄 Report saved to: {filepath}")
    else:
        # Print JSON to stdout
        print("\n📄 JSON Output:")
        print("-" * 60)
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    
    return 0


def cmd_report(args) -> int:
    """Execute report command"""
    print(f"🔍 BotDetect-CLI v{__version__}")
    print("   Running scan to generate report...")
    print()
    
    config = DetectionConfig(
        output_format=args.format,
        output_file=args.output
    )
    
    detector = BotDetector(config)
    report = detector.detect()
    
    generator = ReportGenerator()
    filepath = generator.generate(report, args.format, args.output)
    
    print(f"✅ Report generated: {filepath}")
    return 0


def cmd_tui(args) -> int:
    """Execute TUI command"""
    try:
        from botdetect_cli.tui import run_tui
        run_tui(args.browser)
        return 0
    except ImportError:
        print("❌ TUI mode requires curses support.")
        print("   Please ensure your terminal supports curses.")
        return 1


def cmd_list(args) -> int:
    """Execute list command"""
    scanner = SignalScanner()
    
    print(f"🔍 BotDetect-CLI v{__version__}")
    print(f"   Available Detection Signals: {len(scanner.signals)}")
    print()
    
    # Filter signals
    signals = scanner.signals
    
    if args.category:
        from botdetect_cli.scanner import SignalCategory
        try:
            cat = SignalCategory(args.category.lower())
            signals = [s for s in signals if s.category == cat]
        except ValueError:
            print(f"❌ Invalid category: {args.category}")
            print(f"   Valid categories: {[c.value for c in SignalCategory]}")
            return 1
    
    if args.severity:
        from botdetect_cli.scanner import SignalSeverity
        try:
            sev = SignalSeverity(args.severity.lower())
            signals = [s for s in signals if s.severity == sev]
        except ValueError:
            print(f"❌ Invalid severity: {args.severity}")
            print(f"   Valid severities: {[s.value for s in SignalSeverity]}")
            return 1
    
    # Print signals
    severity_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "medium": "ℹ️",
        "low": "💡",
        "info": "📌"
    }
    
    category_icons = {
        "navigator": "🌐",
        "webdriver": "🤖",
        "chrome_devtools_protocol": "🔧",
        "browser_fingerprint": "👆",
        "behavioral_patterns": "🎯",
        "tls_fingerprint": "🔐",
        "network_signals": "📡",
        "dom_properties": "📄"
    }
    
    for signal in signals:
        emoji = severity_emoji.get(signal.severity.value, "📌")
        icon = category_icons.get(signal.category.value, "📌")
        print(f"{emoji} [{signal.severity.value.upper():8}] {icon} {signal.name}")
        print(f"           Category: {signal.category.value}")
        print(f"           {signal.description[:60]}...")
        print()
    
    return 0


def cmd_compare(args) -> int:
    """Execute compare command"""
    print(f"🔍 BotDetect-CLI v{__version__}")
    print("   Comparing detection scores across browsers...")
    print()
    
    detector = BotDetector()
    results = detector.compare_browsers(args.url)
    
    print("=" * 50)
    print("         BROWSER COMPARISON RESULTS")
    print("=" * 50)
    
    for browser, score in sorted(results.items(), key=lambda x: x[1]):
        bar_length = int(score / 2)
        bar = "█" * bar_length + "░" * (50 - bar_length)
        print(f"  {browser:10} [{bar}] {score:.1f}%")
    
    print("=" * 50)
    
    best = min(results.items(), key=lambda x: x[1])
    print(f"\n✅ Best browser: {best[0]} ({best[1]:.1f}% detection)")
    
    return 0


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    commands = {
        "scan": cmd_scan,
        "report": cmd_report,
        "tui": cmd_tui,
        "list": cmd_list,
        "compare": cmd_compare
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
