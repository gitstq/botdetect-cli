#!/usr/bin/env python3
"""
BotDetect-CLI - Lightweight Browser Automation Detection Signal Analysis Engine
轻量级浏览器自动化检测信号分析引擎

A CLI tool for analyzing browser automation detection signals.
Helps developers understand their website's bot detection capabilities.
"""

__version__ = "1.0.0"
__author__ = "gitstq"
__description__ = "Lightweight Browser Automation Detection Signal Analysis Engine"

from botdetect_cli.detector import BotDetector
from botdetect_cli.reporter import ReportGenerator
from botdetect_cli.scanner import SignalScanner

__all__ = ["BotDetector", "ReportGenerator", "SignalScanner"]
