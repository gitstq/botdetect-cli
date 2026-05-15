#!/usr/bin/env python3
"""
TUI Module - Terminal User Interface Dashboard
Uses curses for a lightweight terminal dashboard
"""

import curses
import time
from typing import Optional, Dict, List
from datetime import datetime

from botdetect_cli import __version__
from botdetect_cli.detector import BotDetector, DetectionConfig, DetectionMode
from botdetect_cli.scanner import SignalScanner, DetectionSignal, SignalCategory, SignalSeverity


class TUIDashboard:
    """
    Terminal User Interface Dashboard for BotDetect-CLI.
    Provides an interactive curses-based interface.
    """
    
    # Color pairs
    COLOR_DEFAULT = 0
    COLOR_CRITICAL = 1
    COLOR_HIGH = 2
    COLOR_MEDIUM = 3
    COLOR_LOW = 4
    COLOR_INFO = 5
    COLOR_SUCCESS = 6
    COLOR_HEADER = 7
    
    def __init__(self, stdscr, browser_type: str = "chromium"):
        """
        Initialize the TUI dashboard.
        
        Args:
            stdscr: curses standard screen
            browser_type: Browser type to test
        """
        self.stdscr = stdscr
        self.browser_type = browser_type
        self.scanner = SignalScanner()
        self.detector = BotDetector(DetectionConfig(browser_type=browser_type))
        
        self.current_view = "main"
        self.selected_index = 0
        self.signals_list: List[DetectionSignal] = []
        self.scroll_offset = 0
        
        self._setup_colors()
        self._setup_curses()
    
    def _setup_colors(self):
        """Setup color pairs"""
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            
            curses.init_pair(1, curses.COLOR_RED, -1)      # Critical
            curses.init_pair(2, curses.COLOR_YELLOW, -1)   # High
            curses.init_pair(3, curses.COLOR_CYAN, -1)     # Medium
            curses.init_pair(4, curses.COLOR_GREEN, -1)    # Low
            curses.init_pair(5, curses.COLOR_BLUE, -1)     # Info
            curses.init_pair(6, curses.COLOR_GREEN, -1)    # Success
            curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Header
    
    def _setup_curses(self):
        """Setup curses settings"""
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.curs_set(0)  # Hide cursor
    
    def run(self):
        """Run the main TUI loop"""
        while True:
            self._draw()
            
            key = self.stdscr.getch()
            
            if key == ord('q') or key == ord('Q'):
                break
            elif key == ord('s') or key == ord('S'):
                self._run_scan()
            elif key == ord('l') or key == ord('L'):
                self._show_signals_list()
            elif key == ord('c') or key == ord('C'):
                self._compare_browsers()
            elif key == ord('h') or key == ord('H'):
                self._show_help()
            elif key == curses.KEY_UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == curses.KEY_DOWN:
                self.selected_index = min(len(self.signals_list) - 1, self.selected_index + 1)
            elif key == curses.KEY_RESIZE:
                self._handle_resize()
    
    def _draw(self):
        """Draw the current view"""
        self.stdscr.clear()
        
        height, width = self.stdscr.getmaxyx()
        
        # Draw header
        self._draw_header(width)
        
        # Draw content based on view
        if self.current_view == "main":
            self._draw_main_view(height, width)
        elif self.current_view == "signals":
            self._draw_signals_view(height, width)
        elif self.current_view == "compare":
            self._draw_compare_view(height, width)
        elif self.current_view == "help":
            self._draw_help_view(height, width)
        
        # Draw footer
        self._draw_footer(height, width)
        
        self.stdscr.refresh()
    
    def _draw_header(self, width: int):
        """Draw the header"""
        header = f" 🔍 BotDetect-CLI v{__version__} - Browser Automation Detection Engine "
        padding = (width - len(header)) // 2
        
        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.addstr(0, 0, " " * width)
        self.stdscr.addstr(0, max(0, padding), header[:width])
        self.stdscr.attroff(curses.color_pair(7))
    
    def _draw_footer(self, height: int, width: int):
        """Draw the footer with controls"""
        footer = " [S] Scan  [L] Signals  [C] Compare  [H] Help  [Q] Quit "
        
        self.stdscr.attron(curses.color_pair(7))
        self.stdscr.addstr(height - 1, 0, " " * width)
        self.stdscr.addstr(height - 1, 0, footer[:width])
        self.stdscr.attroff(curses.color_pair(7))
    
    def _draw_main_view(self, height: int, width: int):
        """Draw the main view"""
        y = 2
        
        # Draw browser info
        self.stdscr.addstr(y, 2, f"Browser: {self.browser_type}")
        y += 2
        
        # Draw menu options
        options = [
            ("S", "Run Detection Scan"),
            ("L", "View All Detection Signals"),
            ("C", "Compare Browsers"),
            ("H", "Help & Documentation"),
            ("Q", "Quit")
        ]
        
        self.stdscr.addstr(y, 2, "Quick Actions:")
        y += 1
        
        for key, desc in options:
            self.stdscr.addstr(y, 4, f"[{key}] {desc}")
            y += 1
        
        y += 2
        
        # Draw signal categories
        self.stdscr.addstr(y, 2, "Detection Categories:")
        y += 1
        
        category_icons = {
            SignalCategory.NAVIGATOR: "🌐",
            SignalCategory.WEBDRIVER: "🤖",
            SignalCategory.CDP: "🔧",
            SignalCategory.FINGERPRINT: "👆",
            SignalCategory.BEHAVIOR: "🎯",
            SignalCategory.TLS: "🔐",
            SignalCategory.NETWORK: "📡",
            SignalCategory.DOM: "📄"
        }
        
        for category in SignalCategory:
            count = len(self.scanner.get_signals_by_category(category))
            icon = category_icons.get(category, "📌")
            self.stdscr.addstr(y, 4, f"{icon} {category.value:25} ({count} signals)")
            y += 1
    
    def _draw_signals_view(self, height: int, width: int):
        """Draw the signals list view"""
        y = 2
        
        self.stdscr.addstr(y, 2, f"All Detection Signals ({len(self.signals_list)} total)")
        y += 2
        
        severity_colors = {
            SignalSeverity.CRITICAL: 1,
            SignalSeverity.HIGH: 2,
            SignalSeverity.MEDIUM: 3,
            SignalSeverity.LOW: 4,
            SignalSeverity.INFO: 5
        }
        
        visible_height = height - y - 2
        
        for i, signal in enumerate(self.signals_list[self.scroll_offset:self.scroll_offset + visible_height]):
            idx = i + self.scroll_offset
            
            if idx == self.selected_index:
                self.stdscr.attron(curses.A_REVERSE)
            
            color = severity_colors.get(signal.severity, 0)
            self.stdscr.attron(curses.color_pair(color))
            
            line = f"  [{signal.severity.value.upper():8}] {signal.name:30} ({signal.category.value})"
            self.stdscr.addstr(y + i, 2, line[:width - 4])
            
            self.stdscr.attroff(curses.color_pair(color))
            self.stdscr.attroff(curses.A_REVERSE)
        
        # Draw selected signal details
        if self.signals_list and 0 <= self.selected_index < len(self.signals_list):
            signal = self.signals_list[self.selected_index]
            detail_y = height - 8
            
            self.stdscr.addstr(detail_y, 2, "─" * (width - 4))
            self.stdscr.addstr(detail_y + 1, 2, f"Name: {signal.name}")
            self.stdscr.addstr(detail_y + 2, 2, f"Description: {signal.description[:width - 20]}")
            self.stdscr.addstr(detail_y + 3, 2, f"Recommendation: {signal.recommendation[:width - 20]}")
    
    def _draw_compare_view(self, height: int, width: int):
        """Draw the browser comparison view"""
        y = 2
        
        self.stdscr.addstr(y, 2, "Browser Detection Score Comparison")
        y += 2
        
        # Get comparison results
        results = self.detector.compare_browsers()
        
        max_score = max(results.values()) if results else 100
        
        for browser, score in sorted(results.items(), key=lambda x: x[1]):
            bar_width = int((score / max_score) * (width - 30))
            bar = "█" * bar_width
            
            # Color based on score
            if score >= 70:
                color = 1  # Red
            elif score >= 50:
                color = 2  # Yellow
            elif score >= 30:
                color = 3  # Cyan
            else:
                color = 4  # Green
            
            self.stdscr.addstr(y, 2, f"{browser:10} ")
            self.stdscr.attron(curses.color_pair(color))
            self.stdscr.addstr(y, 13, bar)
            self.stdscr.attroff(curses.color_pair(color))
            self.stdscr.addstr(y, 13 + bar_width + 1, f" {score:.1f}%")
            y += 1
        
        y += 2
        
        best = min(results.items(), key=lambda x: x[1])
        self.stdscr.addstr(y, 2, f"✅ Best browser: {best[0]} ({best[1]:.1f}% detection score)")
    
    def _draw_help_view(self, height: int, width: int):
        """Draw the help view"""
        y = 2
        
        help_text = [
            "BotDetect-CLI Help",
            "",
            "BotDetect-CLI is a lightweight browser automation detection signal",
            "analysis engine. It helps developers understand their website's",
            "bot detection capabilities.",
            "",
            "Commands:",
            "  [S] Scan     - Run a detection scan",
            "  [L] Signals  - View all detection signals",
            "  [C] Compare  - Compare detection scores across browsers",
            "  [H] Help     - Show this help screen",
            "  [Q] Quit     - Exit the application",
            "",
            "Detection Categories:",
            "  🌐 Navigator     - Browser navigator properties",
            "  🤖 WebDriver     - WebDriver automation signals",
            "  🔧 CDP           - Chrome DevTools Protocol",
            "  👆 Fingerprint   - Browser fingerprint signals",
            "  🎯 Behavior      - Behavioral pattern detection",
            "  🔐 TLS           - TLS fingerprint analysis",
            "  📡 Network       - Network timing and headers",
            "  📄 DOM           - DOM property detection",
            "",
            "For more information:",
            "  https://github.com/gitstq/botdetect-cli"
        ]
        
        for line in help_text:
            if y < height - 2:
                self.stdscr.addstr(y, 2, line[:width - 4])
                y += 1
    
    def _run_scan(self):
        """Run a detection scan"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        self.stdscr.addstr(height // 2, (width - 20) // 2, "Running scan...")
        self.stdscr.refresh()
        
        report = self.detector.detect()
        
        # Store results
        self.signals_list = [s for s in report.scan_result.signals if s.detected]
        
        # Show results
        self.stdscr.clear()
        y = 2
        
        self.stdscr.addstr(y, 2, "Scan Results")
        y += 2
        
        self.stdscr.addstr(y, 2, f"Detection Score: {report.scan_result.detection_score}%")
        y += 1
        self.stdscr.addstr(y, 2, f"Evasion Score: {report.evasion_score}%")
        y += 1
        self.stdscr.addstr(y, 2, f"Risk Level: {report.scan_result.risk_level}")
        y += 1
        self.stdscr.addstr(y, 2, f"Detected Signals: {report.scan_result.detected_signals}/{report.scan_result.total_signals}")
        y += 2
        
        if self.signals_list:
            self.stdscr.addstr(y, 2, "Detected Signals:")
            y += 1
            
            for signal in self.signals_list[:10]:
                self.stdscr.addstr(y, 4, f"• {signal.name} [{signal.severity.value}]")
                y += 1
        
        self.stdscr.addstr(height - 3, 2, "Press any key to continue...")
        self.stdscr.getch()
        
        self.current_view = "main"
    
    def _show_signals_list(self):
        """Show all signals list"""
        self.signals_list = self.scanner.signals
        self.selected_index = 0
        self.scroll_offset = 0
        self.current_view = "signals"
    
    def _compare_browsers(self):
        """Show browser comparison"""
        self.current_view = "compare"
    
    def _show_help(self):
        """Show help screen"""
        self.current_view = "help"
    
    def _handle_resize(self):
        """Handle terminal resize"""
        curses.resizeterm(*self.stdscr.getmaxyx())
        self._draw()


def run_tui(browser_type: str = "chromium"):
    """
    Run the TUI dashboard.
    
    Args:
        browser_type: Browser type to test
    """
    def main(stdscr):
        dashboard = TUIDashboard(stdscr, browser_type)
        dashboard.run()
    
    curses.wrapper(main)
