#!/usr/bin/env python3
"""
Tests for BotDetect-CLI
"""

import pytest
import json
from botdetect_cli.scanner import SignalScanner, SignalCategory, SignalSeverity
from botdetect_cli.detector import BotDetector, DetectionConfig, DetectionMode
from botdetect_cli.reporter import ReportGenerator


class TestSignalScanner:
    """Tests for SignalScanner"""
    
    def test_scanner_initialization(self):
        """Test scanner initializes correctly"""
        scanner = SignalScanner()
        assert scanner is not None
        assert len(scanner.signals) > 0
    
    def test_signal_count(self):
        """Test that scanner has expected number of signals"""
        scanner = SignalScanner()
        assert len(scanner.signals) >= 30  # At least 30 signals
    
    def test_signal_categories(self):
        """Test that signals have valid categories"""
        scanner = SignalScanner()
        for signal in scanner.signals:
            assert signal.category in SignalCategory
    
    def test_signal_severities(self):
        """Test that signals have valid severities"""
        scanner = SignalScanner()
        for signal in scanner.signals:
            assert signal.severity in SignalSeverity
    
    def test_scan_returns_result(self):
        """Test that scan returns a valid result"""
        scanner = SignalScanner()
        result = scanner.scan()
        
        assert result is not None
        assert result.total_signals > 0
        assert 0 <= result.detection_score <= 100
        assert result.risk_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "MINIMAL"]
    
    def test_get_signals_by_category(self):
        """Test filtering signals by category"""
        scanner = SignalScanner()
        
        for category in SignalCategory:
            signals = scanner.get_signals_by_category(category)
            for signal in signals:
                assert signal.category == category
    
    def test_get_signals_by_severity(self):
        """Test filtering signals by severity"""
        scanner = SignalScanner()
        
        for severity in SignalSeverity:
            signals = scanner.get_signals_by_severity(severity)
            for signal in signals:
                assert signal.severity == severity
    
    def test_scan_result_to_dict(self):
        """Test that scan result can be converted to dict"""
        scanner = SignalScanner()
        result = scanner.scan()
        
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "timestamp" in result_dict
        assert "signals" in result_dict
        assert "detection_score" in result_dict


class TestBotDetector:
    """Tests for BotDetector"""
    
    def test_detector_initialization(self):
        """Test detector initializes correctly"""
        detector = BotDetector()
        assert detector is not None
        assert detector.config is not None
    
    def test_detector_with_config(self):
        """Test detector with custom config"""
        config = DetectionConfig(
            mode=DetectionMode.QUICK,
            browser_type="firefox",
            headless=False
        )
        detector = BotDetector(config)
        
        assert detector.config.mode == DetectionMode.QUICK
        assert detector.config.browser_type == "firefox"
        assert detector.config.headless is False
    
    def test_detect_returns_report(self):
        """Test that detect returns a valid report"""
        detector = BotDetector()
        report = detector.detect()
        
        assert report is not None
        assert report.scan_result is not None
        assert report.evasion_score >= 0
    
    def test_quick_scan(self):
        """Test quick scan mode"""
        config = DetectionConfig(mode=DetectionMode.QUICK)
        detector = BotDetector(config)
        report = detector.detect()
        
        assert report is not None
        # Quick scan should have fewer signals
        assert report.scan_result.total_signals <= len(detector.scanner.signals)
    
    def test_compare_browsers(self):
        """Test browser comparison"""
        detector = BotDetector()
        results = detector.compare_browsers()
        
        assert isinstance(results, dict)
        assert "chromium" in results
        assert "firefox" in results
        assert "webkit" in results
        
        for score in results.values():
            assert 0 <= score <= 100
    
    def test_export_json(self):
        """Test JSON export"""
        detector = BotDetector()
        report = detector.detect()
        
        json_output = detector.export_results(report, "json")
        assert isinstance(json_output, str)
        
        # Should be valid JSON
        data = json.loads(json_output)
        assert "scan_result" in data
    
    def test_export_markdown(self):
        """Test Markdown export"""
        detector = BotDetector()
        report = detector.detect()
        
        md_output = detector.export_results(report, "markdown")
        assert isinstance(md_output, str)
        assert "# " in md_output  # Should have headers
    
    def test_export_html(self):
        """Test HTML export"""
        detector = BotDetector()
        report = detector.detect()
        
        html_output = detector.export_results(report, "html")
        assert isinstance(html_output, str)
        assert "<!DOCTYPE html>" in html_output


class TestReportGenerator:
    """Tests for ReportGenerator"""
    
    def test_generator_initialization(self):
        """Test generator initializes correctly"""
        generator = ReportGenerator()
        assert generator is not None
    
    def test_generate_json_report(self):
        """Test JSON report generation"""
        detector = BotDetector()
        report = detector.detect()
        
        generator = ReportGenerator()
        content = generator._generate_json(report)
        
        assert isinstance(content, str)
        data = json.loads(content)
        assert "scan_result" in data
    
    def test_generate_markdown_report(self):
        """Test Markdown report generation"""
        detector = BotDetector()
        report = detector.detect()
        
        generator = ReportGenerator()
        content = generator._generate_markdown(report)
        
        assert isinstance(content, str)
        assert "# " in content
    
    def test_generate_html_report(self):
        """Test HTML report generation"""
        detector = BotDetector()
        report = detector.detect()
        
        generator = ReportGenerator()
        content = generator._generate_html(report)
        
        assert isinstance(content, str)
        assert "<!DOCTYPE html>" in content
    
    def test_generate_text_report(self):
        """Test text report generation"""
        detector = BotDetector()
        report = detector.detect()
        
        generator = ReportGenerator()
        content = generator._generate_text(report)
        
        assert isinstance(content, str)
        assert "BotDetect-CLI" in content


class TestDetectionSignal:
    """Tests for DetectionSignal"""
    
    def test_signal_to_dict(self):
        """Test signal conversion to dict"""
        from botdetect_cli.scanner import DetectionSignal
        
        signal = DetectionSignal(
            id="test_signal",
            name="Test Signal",
            category=SignalCategory.NAVIGATOR,
            severity=SignalSeverity.HIGH,
            description="Test description"
        )
        
        signal_dict = signal.to_dict()
        
        assert signal_dict["id"] == "test_signal"
        assert signal_dict["name"] == "Test Signal"
        assert signal_dict["category"] == "navigator"
        assert signal_dict["severity"] == "high"


class TestDetectionConfig:
    """Tests for DetectionConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = DetectionConfig()
        
        assert config.mode == DetectionMode.STANDARD
        assert config.browser_type == "chromium"
        assert config.headless is True
        assert config.timeout == 30
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = DetectionConfig(
            mode=DetectionMode.DEEP,
            browser_type="firefox",
            headless=False,
            timeout=60
        )
        
        assert config.mode == DetectionMode.DEEP
        assert config.browser_type == "firefox"
        assert config.headless is False
        assert config.timeout == 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
