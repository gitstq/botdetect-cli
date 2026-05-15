#!/usr/bin/env python3
"""
Bot Detector Module - Main detection engine for browser automation signals
"""

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

from botdetect_cli.scanner import (
    SignalScanner, 
    ScanResult, 
    DetectionSignal,
    SignalCategory,
    SignalSeverity
)


class DetectionMode(Enum):
    """Detection modes"""
    QUICK = "quick"           # Quick scan, essential signals only
    STANDARD = "standard"     # Standard scan, all signals
    DEEP = "deep"             # Deep scan, includes behavioral analysis
    STEALTH = "stealth"       # Stealth scan, tests evasion techniques


@dataclass
class DetectionConfig:
    """Configuration for detection"""
    mode: DetectionMode = DetectionMode.STANDARD
    browser_type: str = "chromium"
    headless: bool = True
    timeout: int = 30
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    verbose: bool = False
    output_format: str = "json"
    output_file: Optional[str] = None
    include_recommendations: bool = True
    include_references: bool = True


@dataclass
class DetectionReport:
    """Complete detection report"""
    scan_result: ScanResult
    config: DetectionConfig
    duration_seconds: float
    evasion_score: float
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "scan_result": self.scan_result.to_dict(),
            "config": {
                "mode": self.config.mode.value,
                "browser_type": self.config.browser_type,
                "headless": self.config.headless,
                "timeout": self.config.timeout
            },
            "duration_seconds": self.duration_seconds,
            "evasion_score": self.evasion_score,
            "recommendations": self.recommendations
        }


class BotDetector:
    """
    Main bot detection engine.
    Coordinates scanning, analysis, and reporting.
    """
    
    # Essential signals for quick scan
    QUICK_SCAN_SIGNALS = [
        "nav_webdriver",
        "nav_userAgent", 
        "nav_plugins",
        "wd_selenium",
        "wd_puppeteer",
        "wd_playwright",
        "cdp_runtime"
    ]
    
    # Critical signals that always indicate automation
    CRITICAL_SIGNALS = [
        "nav_webdriver",
        "nav_userAgent",
        "wd_selenium",
        "wd_puppeteer",
        "wd_playwright"
    ]
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        """
        Initialize the bot detector.
        
        Args:
            config: Detection configuration (uses defaults if not provided)
        """
        self.config = config or DetectionConfig()
        self.scanner = SignalScanner()
        self._callbacks: List[Callable[[DetectionSignal], None]] = []
    
    def add_callback(self, callback: Callable[[DetectionSignal], None]):
        """Add a callback to be called when a signal is detected"""
        self._callbacks.append(callback)
    
    def detect(self, target_url: Optional[str] = None) -> DetectionReport:
        """
        Perform bot detection analysis.
        
        Args:
            target_url: Optional URL to analyze (for live testing)
            
        Returns:
            DetectionReport with complete analysis
        """
        start_time = time.time()
        
        # Perform scan based on mode
        if self.config.mode == DetectionMode.QUICK:
            result = self._quick_scan(target_url)
        elif self.config.mode == DetectionMode.DEEP:
            result = self._deep_scan(target_url)
        elif self.config.mode == DetectionMode.STEALTH:
            result = self._stealth_scan(target_url)
        else:
            result = self._standard_scan(target_url)
        
        # Calculate evasion score (inverse of detection score)
        evasion_score = 100 - result.detection_score
        
        # Generate recommendations
        recommendations = self._generate_recommendations(result)
        
        duration = time.time() - start_time
        
        return DetectionReport(
            scan_result=result,
            config=self.config,
            duration_seconds=round(duration, 2),
            evasion_score=round(evasion_score, 2),
            recommendations=recommendations
        )
    
    def _quick_scan(self, target_url: Optional[str]) -> ScanResult:
        """Perform quick scan of essential signals only"""
        result = self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=self.config.headless
        )
        
        # Filter to essential signals
        essential_signals = [
            s for s in result.signals 
            if s.id in self.QUICK_SCAN_SIGNALS
        ]
        result.signals = essential_signals
        result.total_signals = len(essential_signals)
        result.detected_signals = len([s for s in essential_signals if s.detected])
        
        return result
    
    def _standard_scan(self, target_url: Optional[str]) -> ScanResult:
        """Perform standard scan of all signals"""
        return self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=self.config.headless
        )
    
    def _deep_scan(self, target_url: Optional[str]) -> ScanResult:
        """Perform deep scan with behavioral analysis"""
        result = self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=self.config.headless
        )
        
        # Add additional behavioral analysis
        # In a real implementation, this would include:
        # - Mouse movement pattern analysis
        # - Keyboard timing analysis
        # - Scroll behavior analysis
        # - Click timing analysis
        
        return result
    
    def _stealth_scan(self, target_url: Optional[str]) -> ScanResult:
        """
        Perform stealth scan testing evasion techniques.
        Tests various stealth configurations to find optimal settings.
        """
        # Test with different configurations
        results = []
        
        # Test 1: Standard headless
        result1 = self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=True
        )
        results.append(("headless", result1))
        
        # Test 2: Headed mode
        result2 = self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=False
        )
        results.append(("headed", result2))
        
        # Return the best result (lowest detection score)
        best_mode, best_result = min(results, key=lambda x: x[1].detection_score)
        
        if self.config.verbose:
            print(f"Best configuration: {best_mode} (detection score: {best_result.detection_score})")
        
        return best_result
    
    def _generate_recommendations(self, result: ScanResult) -> List[str]:
        """Generate recommendations based on detected signals"""
        recommendations = []
        
        detected_signals = result.detected_signals
        
        # Group by category for organized recommendations
        category_recommendations = {}
        
        for signal in [s for s in result.signals if s.detected]:
            cat = signal.category.value
            if cat not in category_recommendations:
                category_recommendations[cat] = []
            category_recommendations[cat].append(signal)
        
        # Generate category-specific recommendations
        if "navigator" in category_recommendations:
            nav_signals = category_recommendations["navigator"]
            if any(s.id == "nav_webdriver" for s in nav_signals):
                recommendations.append(
                    "🚨 CRITICAL: Override navigator.webdriver property using stealth patches"
                )
            if any(s.id == "nav_userAgent" for s in nav_signals):
                recommendations.append(
                    "🚨 CRITICAL: Remove 'HeadlessChrome' from user agent string"
                )
            if any(s.id == "nav_plugins" for s in nav_signals):
                recommendations.append(
                    "⚠️ HIGH: Inject realistic plugin objects to avoid headless detection"
                )
        
        if "webdriver" in category_recommendations:
            recommendations.append(
                "🚨 CRITICAL: Use stealth plugins (puppeteer-extra, undetected-chromedriver) "
                "or consider CloakBrowser for source-level stealth"
            )
        
        if "cdp" in category_recommendations:
            recommendations.append(
                "⚠️ HIGH: Disable Chrome DevTools Protocol or use stealth mode"
            )
        
        if "fingerprint" in category_recommendations:
            recommendations.append(
                "ℹ️ MEDIUM: Add noise to canvas/WebGL/audio operations for fingerprint resistance"
            )
        
        if "behavior" in category_recommendations:
            recommendations.append(
                "ℹ️ MEDIUM: Implement human-like mouse movements, keyboard timing, and scroll patterns"
            )
        
        if "tls" in category_recommendations:
            recommendations.append(
                "⚠️ HIGH: Ensure TLS fingerprint matches the browser version being simulated"
            )
        
        # Add general recommendations
        if result.detection_score > 50:
            recommendations.append(
                "💡 Consider using CloakBrowser (https://github.com/CloakHQ/CloakBrowser) "
                "for source-level Chromium stealth patches"
            )
        
        if result.detection_score > 30:
            recommendations.append(
                "💡 Use humanize=True option for human-like interaction patterns"
            )
        
        return recommendations
    
    def check_critical_signals(self) -> Dict[str, bool]:
        """
        Quick check for critical automation signals.
        
        Returns:
            Dictionary mapping signal ID to detection status
        """
        result = self.scanner.scan(
            browser_type=self.config.browser_type,
            headless=self.config.headless
        )
        
        return {
            signal_id: any(s.id == signal_id and s.detected for s in result.signals)
            for signal_id in self.CRITICAL_SIGNALS
        }
    
    def get_detection_score(self, target_url: Optional[str] = None) -> float:
        """
        Get the detection score for a target.
        
        Args:
            target_url: Optional URL to analyze
            
        Returns:
            Detection score (0-100, higher = more likely detected as bot)
        """
        result = self.scanner.scan(
            target_url=target_url,
            browser_type=self.config.browser_type,
            headless=self.config.headless
        )
        
        return result.detection_score
    
    def compare_browsers(self, target_url: Optional[str] = None) -> Dict[str, float]:
        """
        Compare detection scores across different browser types.
        
        Args:
            target_url: Optional URL to analyze
            
        Returns:
            Dictionary mapping browser type to detection score
        """
        results = {}
        
        for browser in ["chromium", "firefox", "webkit"]:
            result = self.scanner.scan(
                target_url=target_url,
                browser_type=browser,
                headless=self.config.headless
            )
            results[browser] = result.detection_score
        
        return results
    
    def export_results(self, report: DetectionReport, format: str = "json") -> str:
        """
        Export detection results in specified format.
        
        Args:
            report: Detection report to export
            format: Output format (json, markdown, html)
            
        Returns:
            Formatted string of results
        """
        if format == "json":
            return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            return self._export_markdown(report)
        
        elif format == "html":
            return self._export_html(report)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self, report: DetectionReport) -> str:
        """Export results as Markdown"""
        lines = [
            "# 🔍 BotDetect-CLI Detection Report",
            "",
            f"**Timestamp**: {report.scan_result.timestamp}",
            f"**Duration**: {report.duration_seconds}s",
            f"**Detection Score**: {report.scan_result.detection_score}%",
            f"**Risk Level**: {report.scan_result.risk_level}",
            f"**Evasion Score**: {report.evasion_score}%",
            "",
            "## 📊 Summary",
            "",
            f"- **Total Signals**: {report.scan_result.total_signals}",
            f"- **Detected Signals**: {report.scan_result.detected_signals}",
            "",
            "## 🚨 Detected Signals",
            ""
        ]
        
        for signal in [s for s in report.scan_result.signals if s.detected]:
            severity_emoji = {
                "critical": "🚨",
                "high": "⚠️",
                "medium": "ℹ️",
                "low": "💡",
                "info": "📌"
            }.get(signal.severity.value, "📌")
            
            lines.append(f"### {severity_emoji} {signal.name}")
            lines.append(f"- **Category**: {signal.category.value}")
            lines.append(f"- **Severity**: {signal.severity.value}")
            lines.append(f"- **Description**: {signal.description}")
            if signal.recommendation:
                lines.append(f"- **Recommendation**: {signal.recommendation}")
            lines.append("")
        
        if report.recommendations:
            lines.append("## 💡 Recommendations")
            lines.append("")
            for rec in report.recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _export_html(self, report: DetectionReport) -> str:
        """Export results as HTML"""
        # Color coding for severity
        severity_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#20c997",
            "info": "#0dcaf0"
        }
        
        # Risk level color
        risk_colors = {
            "CRITICAL": "#dc3545",
            "HIGH": "#fd7e14",
            "MEDIUM": "#ffc107",
            "LOW": "#20c997",
            "MINIMAL": "#198754"
        }
        
        detected_signals = [s for s in report.scan_result.signals if s.detected]
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BotDetect-CLI Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 30px; }}
        h1 {{ color: #333; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #4a90d9; }}
        .stat-label {{ color: #666; font-size: 0.9em; }}
        .signal {{ background: #f8f9fa; margin: 10px 0; padding: 15px; border-radius: 8px; border-left: 4px solid; }}
        .signal.critical {{ border-color: {severity_colors['critical']}; }}
        .signal.high {{ border-color: {severity_colors['high']}; }}
        .signal.medium {{ border-color: {severity_colors['medium']}; }}
        .signal.low {{ border-color: {severity_colors['low']}; }}
        .signal-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .signal-name {{ font-weight: bold; color: #333; }}
        .signal-severity {{ padding: 3px 10px; border-radius: 4px; font-size: 0.8em; color: white; }}
        .recommendation {{ background: #e7f3ff; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .risk-badge {{ display: inline-block; padding: 5px 15px; border-radius: 4px; color: white; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 BotDetect-CLI Detection Report</h1>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{report.scan_result.detection_score}%</div>
                <div class="stat-label">Detection Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.evasion_score}%</div>
                <div class="stat-label">Evasion Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{report.scan_result.detected_signals}</div>
                <div class="stat-label">Detected Signals</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="background: {risk_colors.get(report.scan_result.risk_level, '#666')}; color: white; padding: 10px; border-radius: 4px;">{report.scan_result.risk_level}</div>
                <div class="stat-label">Risk Level</div>
            </div>
        </div>
        
        <h2>🚨 Detected Signals ({len(detected_signals)})</h2>
"""
        
        for signal in detected_signals:
            color = severity_colors.get(signal.severity.value, "#666")
            html += f"""
        <div class="signal {signal.severity.value}">
            <div class="signal-header">
                <span class="signal-name">{signal.name}</span>
                <span class="signal-severity" style="background: {color};">{signal.severity.value.upper()}</span>
            </div>
            <p><strong>Category:</strong> {signal.category.value}</p>
            <p>{signal.description}</p>
            {f'<p><strong>Recommendation:</strong> {signal.recommendation}</p>' if signal.recommendation else ''}
        </div>
"""
        
        if report.recommendations:
            html += """
        <h2>💡 Recommendations</h2>
"""
            for rec in report.recommendations:
                html += f"""
        <div class="recommendation">{rec}</div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
