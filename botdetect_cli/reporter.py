#!/usr/bin/env python3
"""
Report Generator Module - Generates reports in various formats
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from botdetect_cli.scanner import ScanResult, DetectionSignal, SignalCategory, SignalSeverity
from botdetect_cli.detector import DetectionReport


class ReportGenerator:
    """
    Generates formatted reports from detection results.
    Supports JSON, Markdown, HTML, and plain text formats.
    """
    
    def __init__(self, output_dir: str = "."):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, report: DetectionReport, 
                 format: str = "json",
                 filename: Optional[str] = None) -> str:
        """
        Generate a report in the specified format.
        
        Args:
            report: Detection report to generate
            format: Output format (json, markdown, html, text)
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to the generated report file
        """
        if format == "json":
            content = self._generate_json(report)
            ext = "json"
        elif format == "markdown":
            content = self._generate_markdown(report)
            ext = "md"
        elif format == "html":
            content = self._generate_html(report)
            ext = "html"
        elif format == "text":
            content = self._generate_text(report)
            ext = "txt"
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"botdetect_report_{timestamp}"
        
        filepath = os.path.join(self.output_dir, f"{filename}.{ext}")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def _generate_json(self, report: DetectionReport) -> str:
        """Generate JSON format report"""
        return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
    
    def _generate_markdown(self, report: DetectionReport) -> str:
        """Generate Markdown format report"""
        lines = [
            "# 🔍 BotDetect-CLI Detection Report",
            "",
            f"> Generated: {report.scan_result.timestamp}",
            "",
            "---",
            "",
            "## 📊 Executive Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Detection Score | **{report.scan_result.detection_score}%** |",
            f"| Evasion Score | **{report.evasion_score}%** |",
            f"| Risk Level | **{report.scan_result.risk_level}** |",
            f"| Total Signals | {report.scan_result.total_signals} |",
            f"| Detected Signals | {report.scan_result.detected_signals} |",
            f"| Scan Duration | {report.duration_seconds}s |",
            "",
            "---",
            "",
            "## 🚨 Detected Signals",
            ""
        ]
        
        detected = [s for s in report.scan_result.signals if s.detected]
        
        if not detected:
            lines.append("*No automation signals detected. Your browser configuration appears stealthy.*")
        else:
            # Group by severity
            by_severity = {}
            for signal in detected:
                sev = signal.severity.value
                if sev not in by_severity:
                    by_severity[sev] = []
                by_severity[sev].append(signal)
            
            # Display in severity order
            severity_order = ["critical", "high", "medium", "low", "info"]
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "ℹ️",
                "low": "💡",
                "info": "📌"
            }
            
            for severity in severity_order:
                if severity in by_severity:
                    emoji = severity_emoji.get(severity, "📌")
                    lines.append(f"### {emoji} {severity.upper()} ({len(by_severity[severity])})")
                    lines.append("")
                    
                    for signal in by_severity[severity]:
                        lines.append(f"#### `{signal.name}`")
                        lines.append("")
                        lines.append(f"- **Category**: {signal.category.value}")
                        lines.append(f"- **Description**: {signal.description}")
                        if signal.value:
                            lines.append(f"- **Detected Value**: `{signal.value}`")
                        if signal.expected_value:
                            lines.append(f"- **Expected Value**: `{signal.expected_value}`")
                        if signal.recommendation:
                            lines.append(f"- **Recommendation**: {signal.recommendation}")
                        lines.append("")
        
        # Recommendations section
        if report.recommendations:
            lines.append("---")
            lines.append("")
            lines.append("## 💡 Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        # Platform info
        lines.append("---")
        lines.append("")
        lines.append("## 🖥️ Platform Information")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(report.scan_result.platform_info, indent=2))
        lines.append("```")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by [BotDetect-CLI](https://github.com/gitstq/botdetect-cli)*")
        
        return "\n".join(lines)
    
    def _generate_html(self, report: DetectionReport) -> str:
        """Generate HTML format report"""
        # Similar to detector's _export_html but more comprehensive
        detected = [s for s in report.scan_result.signals if s.detected]
        
        severity_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#20c997",
            "info": "#0dcaf0"
        }
        
        risk_colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#20c997",
            "MINIMAL": "#198754"
        }
        
        # Category icons
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
        
        # Build signals HTML
        signals_html = ""
        for signal in detected:
            color = severity_colors.get(signal.severity.value, "#666")
            icon = category_icons.get(signal.category.value, "📌")
            
            signals_html += f"""
            <div class="signal-card {signal.severity.value}">
                <div class="signal-header">
                    <span class="signal-icon">{icon}</span>
                    <span class="signal-name">{signal.name}</span>
                    <span class="signal-severity" style="background-color: {color};">{signal.severity.value.upper()}</span>
                </div>
                <div class="signal-body">
                    <p><strong>Category:</strong> {signal.category.value}</p>
                    <p>{signal.description}</p>
                    {f'<p class="recommendation"><strong>💡 Recommendation:</strong> {signal.recommendation}</p>' if signal.recommendation else ''}
                </div>
            </div>
"""
        
        # Build recommendations HTML
        recommendations_html = ""
        for rec in report.recommendations:
            recommendations_html += f'<div class="recommendation-item">{rec}</div>\n'
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BotDetect-CLI Report</title>
    <style>
        :root {{
            --primary: #4a90d9;
            --critical: #dc3545;
            --high: #fd7e14;
            --medium: #ffc107;
            --low: #20c997;
            --info: #0dcaf0;
            --bg: #f5f7fa;
            --card: #ffffff;
            --text: #333333;
            --text-light: #666666;
        }}
        
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            background: linear-gradient(135deg, var(--primary), #357abd);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        header .timestamp {{
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: var(--card);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: var(--primary);
        }}
        
        .stat-label {{
            color: var(--text-light);
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .risk-critical .stat-value {{ color: var(--critical); }}
        .risk-high .stat-value {{ color: var(--high); }}
        .risk-medium .stat-value {{ color: var(--medium); }}
        .risk-low .stat-value {{ color: var(--low); }}
        
        .section {{
            background: var(--card);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        
        .section h2 {{
            color: var(--text);
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--bg);
        }}
        
        .signal-card {{
            background: var(--bg);
            margin: 15px 0;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
        }}
        
        .signal-card.critical {{ border-color: var(--critical); }}
        .signal-card.high {{ border-color: var(--high); }}
        .signal-card.medium {{ border-color: var(--medium); }}
        .signal-card.low {{ border-color: var(--low); }}
        .signal-card.info {{ border-color: var(--info); }}
        
        .signal-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        
        .signal-icon {{
            font-size: 1.5em;
        }}
        
        .signal-name {{
            font-weight: bold;
            flex-grow: 1;
        }}
        
        .signal-severity {{
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            color: white;
            text-transform: uppercase;
        }}
        
        .signal-body {{
            color: var(--text-light);
        }}
        
        .signal-body .recommendation {{
            margin-top: 10px;
            padding: 10px;
            background: rgba(74, 144, 217, 0.1);
            border-radius: 4px;
            color: var(--text);
        }}
        
        .recommendation-item {{
            padding: 15px;
            margin: 10px 0;
            background: #e7f3ff;
            border-radius: 8px;
            border-left: 4px solid var(--primary);
        }}
        
        .progress-bar {{
            height: 20px;
            background: var(--bg);
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            color: var(--text-light);
            font-size: 0.9em;
        }}
        
        footer a {{
            color: var(--primary);
            text-decoration: none;
        }}
        
        @media (max-width: 768px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 BotDetect-CLI Report</h1>
            <p class="timestamp">Generated: {report.scan_result.timestamp}</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card risk-{report.scan_result.risk_level.lower()}">
                <div class="stat-value">{report.scan_result.detection_score}%</div>
                <div class="stat-label">Detection Score</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {report.scan_result.detection_score}%; background: {risk_colors.get(report.scan_result.risk_level, '#666')};"></div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">{report.evasion_score}%</div>
                <div class="stat-label">Evasion Score</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {report.evasion_score}%; background: var(--low);"></div>
                </div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">{report.scan_result.detected_signals}</div>
                <div class="stat-label">Detected Signals</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value" style="font-size: 1.5em; color: {risk_colors.get(report.scan_result.risk_level, '#666')};">{report.scan_result.risk_level}</div>
                <div class="stat-label">Risk Level</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🚨 Detected Signals ({len(detected)})</h2>
            {signals_html if detected else '<p style="color: var(--low);">✅ No automation signals detected. Your browser configuration appears stealthy.</p>'}
        </div>
        
        {f'<div class="section"><h2>💡 Recommendations</h2>{recommendations_html}</div>' if report.recommendations else ''}
        
        <footer>
            Generated by <a href="https://github.com/gitstq/botdetect-cli">BotDetect-CLI</a> | 
            Duration: {report.duration_seconds}s
        </footer>
    </div>
</body>
</html>
"""
    
    def _generate_text(self, report: DetectionReport) -> str:
        """Generate plain text format report"""
        lines = [
            "=" * 60,
            "BotDetect-CLI Detection Report",
            "=" * 60,
            "",
            f"Timestamp: {report.scan_result.timestamp}",
            f"Duration: {report.duration_seconds}s",
            "",
            "-" * 60,
            "SUMMARY",
            "-" * 60,
            f"Detection Score: {report.scan_result.detection_score}%",
            f"Evasion Score: {report.evasion_score}%",
            f"Risk Level: {report.scan_result.risk_level}",
            f"Total Signals: {report.scan_result.total_signals}",
            f"Detected Signals: {report.scan_result.detected_signals}",
            "",
            "-" * 60,
            "DETECTED SIGNALS",
            "-" * 60,
        ]
        
        detected = [s for s in report.scan_result.signals if s.detected]
        
        if not detected:
            lines.append("No automation signals detected.")
        else:
            for signal in detected:
                lines.extend([
                    "",
                    f"[{signal.severity.value.upper()}] {signal.name}",
                    f"  Category: {signal.category.value}",
                    f"  Description: {signal.description}",
                ])
                if signal.recommendation:
                    lines.append(f"  Recommendation: {signal.recommendation}")
        
        if report.recommendations:
            lines.extend([
                "",
                "-" * 60,
                "RECOMMENDATIONS",
                "-" * 60,
            ])
            for rec in report.recommendations:
                lines.append(f"  • {rec}")
        
        lines.extend([
            "",
            "=" * 60,
            "Generated by BotDetect-CLI",
            "=" * 60,
        ])
        
        return "\n".join(lines)
    
    def generate_summary_table(self, report: DetectionReport) -> str:
        """Generate a compact summary table"""
        lines = [
            "┌─────────────────────────────────────────────────────────────┐",
            "│                    BotDetect-CLI Summary                    │",
            "├─────────────────────────────────────────────────────────────┤",
            f"│ Detection Score:  {report.scan_result.detection_score:>5}%                              │",
            f"│ Evasion Score:    {report.evasion_score:>5}%                              │",
            f"│ Risk Level:       {report.scan_result.risk_level:<10}                       │",
            f"│ Detected Signals: {report.scan_result.detected_signals:>5} / {report.scan_result.total_signals:<5}                      │",
            "├─────────────────────────────────────────────────────────────┤",
            "│ By Severity:                                                │",
        ]
        
        # Count by severity
        severity_counts = {}
        for signal in report.scan_result.signals:
            if signal.detected:
                sev = signal.severity.value
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        for sev in ["critical", "high", "medium", "low", "info"]:
            count = severity_counts.get(sev, 0)
            if count > 0:
                lines.append(f"│   {sev.upper():<10}: {count:>3}                                      │")
        
        lines.extend([
            "└─────────────────────────────────────────────────────────────┘",
        ])
        
        return "\n".join(lines)
