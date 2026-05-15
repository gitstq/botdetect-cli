#!/usr/bin/env python3
"""
Signal Scanner Module - Scans and collects browser automation detection signals
"""

import json
import platform
import sys
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum


class SignalCategory(Enum):
    """Categories of detection signals"""
    NAVIGATOR = "navigator"
    WEBDRIVER = "webdriver"
    CDP = "chrome_devtools_protocol"
    FINGERPRINT = "browser_fingerprint"
    BEHAVIOR = "behavioral_patterns"
    TLS = "tls_fingerprint"
    NETWORK = "network_signals"
    DOM = "dom_properties"


class SignalSeverity(Enum):
    """Severity levels for detection signals"""
    CRITICAL = "critical"      # 100% bot detection
    HIGH = "high"             # Strong bot indicator
    MEDIUM = "medium"         # Moderate indicator
    LOW = "low"               # Weak indicator
    INFO = "info"             # Informational only


@dataclass
class DetectionSignal:
    """Represents a single detection signal"""
    id: str
    name: str
    category: SignalCategory
    severity: SignalSeverity
    description: str
    detected: bool = False
    value: Any = None
    expected_value: Any = None
    recommendation: str = ""
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        result = asdict(self)
        result['category'] = self.category.value
        result['severity'] = self.severity.value
        return result


@dataclass
class ScanResult:
    """Result of a complete scan"""
    timestamp: str
    platform_info: Dict[str, str]
    signals: List[DetectionSignal]
    total_signals: int
    detected_signals: int
    detection_score: float
    risk_level: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp,
            "platform_info": self.platform_info,
            "signals": [s.to_dict() for s in self.signals],
            "total_signals": self.total_signals,
            "detected_signals": self.detected_signals,
            "detection_score": self.detection_score,
            "risk_level": self.risk_level
        }


class SignalScanner:
    """
    Scans browser automation detection signals.
    Analyzes various signals that can be used to detect automated browsers.
    """
    
    # Signal definitions with detection logic
    SIGNAL_DEFINITIONS = [
        # Navigator signals
        {
            "id": "nav_webdriver",
            "name": "navigator.webdriver",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.CRITICAL,
            "description": "navigator.webdriver property indicates automation",
            "expected_value": "undefined",
            "recommendation": "Use stealth patches to override navigator.webdriver",
            "references": ["https://developer.mozilla.org/en-US/docs/Web/API/Navigator/webdriver"]
        },
        {
            "id": "nav_plugins",
            "name": "navigator.plugins.length",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.HIGH,
            "description": "Empty plugins array indicates headless browser",
            "expected_value": "> 0",
            "recommendation": "Inject realistic plugin objects"
        },
        {
            "id": "nav_languages",
            "name": "navigator.languages",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.MEDIUM,
            "description": "Missing or unusual languages array",
            "expected_value": "Non-empty array",
            "recommendation": "Set realistic language preferences"
        },
        {
            "id": "nav_hardwareConcurrency",
            "name": "navigator.hardwareConcurrency",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.LOW,
            "description": "Unusual CPU core count",
            "expected_value": "2-64 cores",
            "recommendation": "Set realistic hardware concurrency value"
        },
        {
            "id": "nav_deviceMemory",
            "name": "navigator.deviceMemory",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.LOW,
            "description": "Unusual device memory value",
            "expected_value": "4-32 GB",
            "recommendation": "Set realistic device memory value"
        },
        {
            "id": "nav_userAgent",
            "name": "navigator.userAgent",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.CRITICAL,
            "description": "HeadlessChrome in user agent string",
            "expected_value": "No 'HeadlessChrome' substring",
            "recommendation": "Override user agent to remove headless indicators"
        },
        {
            "id": "nav_platform",
            "name": "navigator.platform",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.MEDIUM,
            "description": "Inconsistent platform string",
            "expected_value": "Matches OS",
            "recommendation": "Ensure platform matches actual OS"
        },
        {
            "id": "nav_vendor",
            "name": "navigator.vendor",
            "category": SignalCategory.NAVIGATOR,
            "severity": SignalSeverity.LOW,
            "description": "Unusual vendor string",
            "expected_value": "'Google Inc.' for Chrome",
            "recommendation": "Set correct vendor string"
        },
        
        # WebDriver signals
        {
            "id": "wd_selenium",
            "name": "Selenium Detection",
            "category": SignalCategory.WEBDRIVER,
            "severity": SignalSeverity.CRITICAL,
            "description": "Selenium-specific properties detected",
            "recommendation": "Use undetected-chromedriver or stealth plugins"
        },
        {
            "id": "wd_puppeteer",
            "name": "Puppeteer Detection",
            "category": SignalCategory.WEBDRIVER,
            "severity": SignalSeverity.CRITICAL,
            "description": "Puppeteer-specific properties detected",
            "recommendation": "Use puppeteer-extra with stealth plugin"
        },
        {
            "id": "wd_playwright",
            "name": "Playwright Detection",
            "category": SignalCategory.WEBDRIVER,
            "severity": SignalSeverity.CRITICAL,
            "description": "Playwright-specific properties detected",
            "recommendation": "Apply stealth patches or use CloakBrowser"
        },
        
        # CDP signals
        {
            "id": "cdp_runtime",
            "name": "CDP Runtime Detection",
            "category": SignalCategory.CDP,
            "severity": SignalSeverity.HIGH,
            "description": "Chrome DevTools Protocol runtime enabled",
            "recommendation": "Disable CDP or use stealth mode"
        },
        {
            "id": "cdp_connection",
            "name": "CDP Connection Detection",
            "category": SignalCategory.CDP,
            "severity": SignalSeverity.HIGH,
            "description": "CDP connection detected via window.cdc_adoQpoasnfa76pfcZLmcfl_Array",
            "recommendation": "Remove CDP connection indicators"
        },
        
        # Fingerprint signals
        {
            "id": "fp_canvas",
            "name": "Canvas Fingerprint",
            "category": SignalCategory.FINGERPRINT,
            "severity": SignalSeverity.MEDIUM,
            "description": "Canvas fingerprint consistency check",
            "recommendation": "Add noise to canvas operations"
        },
        {
            "id": "fp_webgl",
            "name": "WebGL Fingerprint",
            "category": SignalCategory.FINGERPRINT,
            "severity": SignalSeverity.MEDIUM,
            "description": "WebGL renderer and vendor consistency",
            "recommendation": "Override WebGL parameters to match real GPU"
        },
        {
            "id": "fp_audio",
            "name": "Audio Fingerprint",
            "category": SignalCategory.FINGERPRINT,
            "severity": SignalSeverity.MEDIUM,
            "description": "Audio context fingerprint",
            "recommendation": "Add noise to audio processing"
        },
        {
            "id": "fp_fonts",
            "name": "Font Fingerprint",
            "category": SignalCategory.FINGERPRINT,
            "severity": SignalSeverity.LOW,
            "description": "Font enumeration fingerprint",
            "recommendation": "Limit font enumeration or use standard fonts"
        },
        {
            "id": "fp_screen",
            "name": "Screen Properties",
            "category": SignalCategory.FINGERPRINT,
            "severity": SignalSeverity.MEDIUM,
            "description": "Unusual screen dimensions or color depth",
            "recommendation": "Set realistic screen properties"
        },
        
        # Behavioral signals
        {
            "id": "beh_mouse",
            "name": "Mouse Movement Patterns",
            "category": SignalCategory.BEHAVIOR,
            "severity": SignalSeverity.HIGH,
            "description": "Non-human mouse movement detected",
            "recommendation": "Use human-like mouse movement curves"
        },
        {
            "id": "beh_keyboard",
            "name": "Keyboard Input Patterns",
            "category": SignalCategory.BEHAVIOR,
            "severity": SignalSeverity.MEDIUM,
            "description": "Non-human keyboard timing detected",
            "recommendation": "Add random delays between keystrokes"
        },
        {
            "id": "beh_scroll",
            "name": "Scroll Behavior",
            "category": SignalCategory.BEHAVIOR,
            "severity": SignalSeverity.LOW,
            "description": "Instant or linear scroll detected",
            "recommendation": "Implement smooth, human-like scrolling"
        },
        {
            "id": "beh_click",
            "name": "Click Timing",
            "category": SignalCategory.BEHAVIOR,
            "severity": SignalSeverity.MEDIUM,
            "description": "Unusual click timing patterns",
            "recommendation": "Add random delays before clicks"
        },
        
        # TLS signals
        {
            "id": "tls_ja3",
            "name": "JA3 Fingerprint",
            "category": SignalCategory.TLS,
            "severity": SignalSeverity.HIGH,
            "description": "TLS client hello fingerprint mismatch",
            "recommendation": "Use browser with matching TLS fingerprint"
        },
        {
            "id": "tls_ja4",
            "name": "JA4 Fingerprint",
            "category": SignalCategory.TLS,
            "severity": SignalSeverity.HIGH,
            "description": "JA4 TLS fingerprint analysis",
            "recommendation": "Ensure TLS fingerprint matches browser version"
        },
        
        # Network signals
        {
            "id": "net_timing",
            "name": "Network Timing",
            "category": SignalCategory.NETWORK,
            "severity": SignalSeverity.MEDIUM,
            "description": "Unusual network timing patterns",
            "recommendation": "Add realistic network latency"
        },
        {
            "id": "net_headers",
            "name": "HTTP Headers",
            "category": SignalCategory.NETWORK,
            "severity": SignalSeverity.HIGH,
            "description": "Suspicious HTTP headers detected",
            "recommendation": "Remove automation-related headers"
        },
        
        # DOM signals
        {
            "id": "dom_window_chrome",
            "name": "window.chrome",
            "category": SignalCategory.DOM,
            "severity": SignalSeverity.MEDIUM,
            "description": "Missing window.chrome object",
            "expected_value": "Present in Chrome",
            "recommendation": "Add window.chrome object"
        },
        {
            "id": "dom_permissions",
            "name": "Permissions API",
            "category": SignalCategory.DOM,
            "severity": SignalSeverity.LOW,
            "description": "Unusual permissions behavior",
            "recommendation": "Implement standard permissions behavior"
        },
        {
            "id": "dom_iframe_contentWindow",
            "name": "iframe contentWindow",
            "category": SignalCategory.DOM,
            "severity": SignalSeverity.MEDIUM,
            "description": "iframe contentWindow detection",
            "recommendation": "Handle iframe access consistently"
        },
    ]
    
    def __init__(self):
        """Initialize the signal scanner"""
        self.signals: List[DetectionSignal] = []
        self._initialize_signals()
    
    def _initialize_signals(self):
        """Initialize signal objects from definitions"""
        self.signals = []
        for sig_def in self.SIGNAL_DEFINITIONS:
            signal = DetectionSignal(
                id=sig_def["id"],
                name=sig_def["name"],
                category=sig_def["category"],
                severity=sig_def["severity"],
                description=sig_def["description"],
                expected_value=sig_def.get("expected_value"),
                recommendation=sig_def.get("recommendation", ""),
                references=sig_def.get("references", [])
            )
            self.signals.append(signal)
    
    def scan(self, target_url: Optional[str] = None, 
             browser_type: str = "chromium",
             headless: bool = True) -> ScanResult:
        """
        Perform a complete scan of detection signals.
        
        Args:
            target_url: Optional URL to scan (for live testing)
            browser_type: Browser type to simulate (chromium, firefox, webkit)
            headless: Whether to run in headless mode
            
        Returns:
            ScanResult object with all detected signals
        """
        # Simulate detection (in real implementation, this would use Playwright/Selenium)
        self._simulate_detection(browser_type, headless)
        
        # Calculate scores
        detected = [s for s in self.signals if s.detected]
        total = len(self.signals)
        detected_count = len(detected)
        
        # Calculate detection score (weighted by severity)
        severity_weights = {
            SignalSeverity.CRITICAL: 100,
            SignalSeverity.HIGH: 75,
            SignalSeverity.MEDIUM: 50,
            SignalSeverity.LOW: 25,
            SignalSeverity.INFO: 10
        }
        
        total_weight = sum(severity_weights[s.severity] for s in self.signals)
        detected_weight = sum(severity_weights[s.severity] for s in detected)
        detection_score = (detected_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Determine risk level
        if detection_score >= 70:
            risk_level = "CRITICAL"
        elif detection_score >= 50:
            risk_level = "HIGH"
        elif detection_score >= 30:
            risk_level = "MEDIUM"
        elif detection_score >= 10:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return ScanResult(
            timestamp=datetime.now().isoformat(),
            platform_info=self._get_platform_info(),
            signals=self.signals,
            total_signals=total,
            detected_signals=detected_count,
            detection_score=round(detection_score, 2),
            risk_level=risk_level
        )
    
    def _simulate_detection(self, browser_type: str, headless: bool):
        """
        Simulate detection results based on browser configuration.
        In a real implementation, this would use actual browser testing.
        """
        import random
        
        # Reset all signals
        for signal in self.signals:
            signal.detected = False
            signal.value = None
        
        # Simulate detection based on browser type and headless mode
        if headless:
            # Headless browsers trigger more signals
            for signal in self.signals:
                if signal.category == SignalCategory.NAVIGATOR:
                    # Navigator signals are more likely detected in headless
                    if signal.id in ["nav_webdriver", "nav_userAgent", "nav_plugins"]:
                        signal.detected = random.random() > 0.1
                        signal.value = f"detected_{signal.id}"
                    elif signal.id in ["nav_languages", "nav_hardwareConcurrency"]:
                        signal.detected = random.random() > 0.5
                        signal.value = f"unusual_{signal.id}"
                
                elif signal.category == SignalCategory.WEBDRIVER:
                    signal.detected = random.random() > 0.3
                    signal.value = "webdriver_detected"
                
                elif signal.category == SignalCategory.CDP:
                    signal.detected = random.random() > 0.2
                    signal.value = "cdp_enabled"
                
                elif signal.category == SignalCategory.BEHAVIOR:
                    signal.detected = random.random() > 0.4
                    signal.value = "non_human_behavior"
        else:
            # Headed browsers trigger fewer signals
            for signal in self.signals:
                signal.detected = random.random() > 0.7
        
        # Browser-specific signals
        if browser_type == "chromium":
            for signal in self.signals:
                if signal.id == "dom_window_chrome":
                    signal.detected = False  # Should be present in Chrome
                    signal.value = "present"
        
        elif browser_type == "firefox":
            for signal in self.signals:
                if signal.id == "dom_window_chrome":
                    signal.detected = True  # Should not be present in Firefox
                    signal.value = "missing"
    
    def _get_platform_info(self) -> Dict[str, str]:
        """Get platform information"""
        return {
            "system": platform.system(),
            "node": platform.node(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation()
        }
    
    def get_signals_by_category(self, category: SignalCategory) -> List[DetectionSignal]:
        """Get all signals in a specific category"""
        return [s for s in self.signals if s.category == category]
    
    def get_signals_by_severity(self, severity: SignalSeverity) -> List[DetectionSignal]:
        """Get all signals with a specific severity"""
        return [s for s in self.signals if s.severity == severity]
    
    def get_detected_signals(self) -> List[DetectionSignal]:
        """Get all detected signals"""
        return [s for s in self.signals if s.detected]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the scan results"""
        detected = self.get_detected_signals()
        
        by_category = {}
        for category in SignalCategory:
            cat_signals = self.get_signals_by_category(category)
            detected_in_cat = [s for s in cat_signals if s.detected]
            by_category[category.value] = {
                "total": len(cat_signals),
                "detected": len(detected_in_cat)
            }
        
        by_severity = {}
        for severity in SignalSeverity:
            sev_signals = self.get_signals_by_severity(severity)
            detected_in_sev = [s for s in sev_signals if s.detected]
            by_severity[severity.value] = {
                "total": len(sev_signals),
                "detected": len(detected_in_sev)
            }
        
        return {
            "total_signals": len(self.signals),
            "detected_signals": len(detected),
            "by_category": by_category,
            "by_severity": by_severity
        }
