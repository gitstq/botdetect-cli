<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/python-3.10+-green.svg" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="License">
  <img src="https://img.shields.io/badge/dependencies-0-red.svg" alt="Dependencies">
</p>

<p align="center">
  <a href="#english">English</a> • 
  <a href="#简体中文">简体中文</a> • 
  <a href="#繁體中文">繁體中文</a>
</p>

---

<a name="english"></a>
# 🔍 BotDetect-CLI

**Lightweight Browser Automation Detection Signal Analysis Engine**

A powerful CLI tool that helps developers understand their website's bot detection capabilities by analyzing 30+ browser automation signals.

## 🎉 Project Introduction

BotDetect-CLI is a lightweight, zero-dependency Python CLI tool designed to analyze browser automation detection signals. Inspired by stealth browser projects like CloakBrowser, BotDetect-CLI takes the **defender's perspective** - helping developers test and understand their website's bot detection capabilities.

**Key Differentiator**: While tools like CloakBrowser help create stealthy browsers to *bypass* detection, BotDetect-CLI helps you *understand* what signals your website detects, enabling you to build better security or test your automation scripts.

## ✨ Core Features

- 🔍 **30+ Detection Signals** - Comprehensive analysis across 8 categories
- 🌐 **Navigator Detection** - webdriver, plugins, languages, hardwareConcurrency, etc.
- 🤖 **WebDriver Detection** - Selenium, Puppeteer, Playwright signals
- 🔧 **CDP Detection** - Chrome DevTools Protocol indicators
- 👆 **Fingerprint Analysis** - Canvas, WebGL, Audio, Font fingerprints
- 🎯 **Behavioral Patterns** - Mouse, keyboard, scroll behavior analysis
- 🔐 **TLS Fingerprinting** - JA3/JA4 analysis
- 📊 **Multiple Report Formats** - JSON, Markdown, HTML, Text
- 🖥️ **TUI Dashboard** - Interactive terminal interface
- 🚀 **Zero Dependencies** - Pure Python standard library

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install botdetect-cli

# Or install from source
git clone https://github.com/gitstq/botdetect-cli.git
cd botdetect-cli
pip install -e .
```

### Basic Usage

```bash
# Run standard scan
botdetect scan

# Quick scan (essential signals only)
botdetect scan --mode quick

# Deep scan with behavioral analysis
botdetect scan --mode deep

# Test specific browser
botdetect scan --browser firefox

# Generate HTML report
botdetect scan --format html --output report

# Launch TUI dashboard
botdetect tui
```

## 📖 Detailed Usage Guide

### Detection Modes

| Mode | Description | Signals |
|------|-------------|---------|
| `quick` | Essential signals only | ~7 critical signals |
| `standard` | All signals | 30+ signals |
| `deep` | Include behavioral analysis | 30+ signals + behavior |
| `stealth` | Test evasion techniques | Compare configurations |

### Detection Categories

| Category | Icon | Description |
|----------|------|-------------|
| Navigator | 🌐 | Browser navigator properties |
| WebDriver | 🤖 | Automation framework signals |
| CDP | 🔧 | Chrome DevTools Protocol |
| Fingerprint | 👆 | Browser fingerprint signals |
| Behavior | 🎯 | Behavioral pattern detection |
| TLS | 🔐 | TLS fingerprint analysis |
| Network | 📡 | Network timing and headers |
| DOM | 📄 | DOM property detection |

### API Usage

```python
from botdetect_cli import BotDetector
from botdetect_cli.detector import DetectionConfig, DetectionMode

# Create detector with custom config
config = DetectionConfig(
    mode=DetectionMode.STANDARD,
    browser_type="chromium",
    headless=True
)
detector = BotDetector(config)

# Run detection
report = detector.detect()

# Access results
print(f"Detection Score: {report.scan_result.detection_score}%")
print(f"Risk Level: {report.scan_result.risk_level}")
print(f"Detected Signals: {report.scan_result.detected_signals}")

# Export report
json_output = detector.export_results(report, "json")
html_output = detector.export_results(report, "html")
```

## 💡 Design Philosophy

BotDetect-CLI was inspired by the growing need to understand bot detection mechanisms. While projects like CloakBrowser demonstrate how to create stealthy browsers, BotDetect-CLI provides the **other side of the coin** - helping developers:

1. **Test their websites** - Understand what signals your bot detection sees
2. **Debug automation scripts** - Find out why your script is being blocked
3. **Learn detection techniques** - Educational tool for understanding browser fingerprinting
4. **Build better security** - Know what signals to look for

## 📦 Deployment

### As a CLI Tool

```bash
# Install globally
pip install botdetect-cli

# Run anywhere
botdetect scan
```

### As a Python Library

```python
# requirements.txt
botdetect-cli>=1.0.0

# In your code
from botdetect_cli import BotDetector
```

### Docker

```bash
docker build -t botdetect-cli .
docker run --rm botdetect-cli scan
```

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
# 🔍 BotDetect-CLI

**轻量级浏览器自动化检测信号分析引擎**

一款强大的CLI工具，通过分析30+浏览器自动化信号，帮助开发者了解自己网站的机器人检测能力。

## 🎉 项目介绍

BotDetect-CLI是一个轻量级、零依赖的Python CLI工具，专为分析浏览器自动化检测信号而设计。受CloakBrowser等隐身浏览器项目启发，BotDetect-CLI从**防御者视角**出发——帮助开发者测试和了解自己网站的机器人检测能力。

**核心差异化**：CloakBrowser等工具帮助创建隐身浏览器来*绕过*检测，而BotDetect-CLI帮助您*理解*网站检测到哪些信号，从而构建更好的安全防护或测试您的自动化脚本。

## ✨ 核心特性

- 🔍 **30+检测信号** - 覆盖8大类别的全面分析
- 🌐 **Navigator检测** - webdriver、plugins、languages、hardwareConcurrency等
- 🤖 **WebDriver检测** - Selenium、Puppeteer、Playwright信号
- 🔧 **CDP检测** - Chrome DevTools Protocol指标
- 👆 **指纹分析** - Canvas、WebGL、Audio、Font指纹
- 🎯 **行为模式** - 鼠标、键盘、滚动行为分析
- 🔐 **TLS指纹** - JA3/JA4分析
- 📊 **多格式报告** - JSON、Markdown、HTML、Text
- 🖥️ **TUI仪表板** - 交互式终端界面
- 🚀 **零依赖** - 纯Python标准库实现

## 🚀 快速开始

### 安装

```bash
# 从PyPI安装
pip install botdetect-cli

# 或从源码安装
git clone https://github.com/gitstq/botdetect-cli.git
cd botdetect-cli
pip install -e .
```

### 基本用法

```bash
# 运行标准扫描
botdetect scan

# 快速扫描（仅关键信号）
botdetect scan --mode quick

# 深度扫描（含行为分析）
botdetect scan --mode deep

# 测试特定浏览器
botdetect scan --browser firefox

# 生成HTML报告
botdetect scan --format html --output report

# 启动TUI仪表板
botdetect tui
```

## 📖 详细使用指南

### 检测模式

| 模式 | 描述 | 信号数 |
|------|------|--------|
| `quick` | 仅关键信号 | ~7个关键信号 |
| `standard` | 所有信号 | 30+信号 |
| `deep` | 包含行为分析 | 30+信号+行为 |
| `stealth` | 测试规避技术 | 对比配置 |

### 检测类别

| 类别 | 图标 | 描述 |
|------|------|------|
| Navigator | 🌐 | 浏览器navigator属性 |
| WebDriver | 🤖 | 自动化框架信号 |
| CDP | 🔧 | Chrome DevTools协议 |
| Fingerprint | 👆 | 浏览器指纹信号 |
| Behavior | 🎯 | 行为模式检测 |
| TLS | 🔐 | TLS指纹分析 |
| Network | 📡 | 网络时序和头信息 |
| DOM | 📄 | DOM属性检测 |

### API使用

```python
from botdetect_cli import BotDetector
from botdetect_cli.detector import DetectionConfig, DetectionMode

# 创建自定义配置的检测器
config = DetectionConfig(
    mode=DetectionMode.STANDARD,
    browser_type="chromium",
    headless=True
)
detector = BotDetector(config)

# 运行检测
report = detector.detect()

# 访问结果
print(f"检测分数: {report.scan_result.detection_score}%")
print(f"风险等级: {report.scan_result.risk_level}")
print(f"检测到的信号: {report.scan_result.detected_signals}")

# 导出报告
json_output = detector.export_results(report, "json")
html_output = detector.export_results(report, "html")
```

## 💡 设计理念

BotDetect-CLI的诞生源于对机器人检测机制理解的需求。虽然CloakBrowser等项目展示了如何创建隐身浏览器，但BotDetect-CLI提供了**硬币的另一面**——帮助开发者：

1. **测试网站** - 了解您的机器人检测能看到哪些信号
2. **调试自动化脚本** - 找出脚本被阻止的原因
3. **学习检测技术** - 理解浏览器指纹识别的教育工具
4. **构建更好的安全** - 了解应该关注哪些信号

## 📦 部署

### 作为CLI工具

```bash
# 全局安装
pip install botdetect-cli

# 任意位置运行
botdetect scan
```

### 作为Python库

```python
# requirements.txt
botdetect-cli>=1.0.0

# 在代码中
from botdetect_cli import BotDetector
```

### Docker

```bash
docker build -t botdetect-cli .
docker run --rm botdetect-cli scan
```

## 🤝 贡献指南

欢迎贡献！请阅读我们的贡献指南：

1. Fork本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 📄 开源协议

本项目采用MIT协议 - 详见 [LICENSE](LICENSE) 文件。

---

<a name="繁體中文"></a>
# 🔍 BotDetect-CLI

**輕量級瀏覽器自動化檢測信號分析引擎**

一款強大的CLI工具，通過分析30+瀏覽器自動化信號，幫助開發者了解自己網站的機器人檢測能力。

## 🎉 專案介紹

BotDetect-CLI是一個輕量級、零依賴的Python CLI工具，專為分析瀏覽器自動化檢測信號而設計。受CloakBrowser等隱身瀏覽器專案啟發，BotDetect-CLI從**防禦者視角**出發——幫助開發者測試和了解自己網站的機器人檢測能力。

**核心差異化**：CloakBrowser等工具幫助創建隱身瀏覽器來*繞過*檢測，而BotDetect-CLI幫助您*理解*網站檢測到哪些信號，從而構建更好的安全防護或測試您的自動化腳本。

## ✨ 核心特性

- 🔍 **30+檢測信號** - 覆蓋8大類別的全面分析
- 🌐 **Navigator檢測** - webdriver、plugins、languages、hardwareConcurrency等
- 🤖 **WebDriver檢測** - Selenium、Puppeteer、Playwright信號
- 🔧 **CDP檢測** - Chrome DevTools Protocol指標
- 👆 **指紋分析** - Canvas、WebGL、Audio、Font指紋
- 🎯 **行為模式** - 滑鼠、鍵盤、滾動行為分析
- 🔐 **TLS指紋** - JA3/JA4分析
- 📊 **多格式報告** - JSON、Markdown、HTML、Text
- 🖥️ **TUI儀表板** - 互動式終端介面
- 🚀 **零依賴** - 純Python標準庫實現

## 🚀 快速開始

### 安裝

```bash
# 從PyPI安裝
pip install botdetect-cli

# 或從原始碼安裝
git clone https://github.com/gitstq/botdetect-cli.git
cd botdetect-cli
pip install -e .
```

### 基本用法

```bash
# 執行標準掃描
botdetect scan

# 快速掃描（僅關鍵信號）
botdetect scan --mode quick

# 深度掃描（含行為分析）
botdetect scan --mode deep

# 測試特定瀏覽器
botdetect scan --browser firefox

# 生成HTML報告
botdetect scan --format html --output report

# 啟動TUI儀表板
botdetect tui
```

## 📖 詳細使用指南

### 檢測模式

| 模式 | 描述 | 信號數 |
|------|------|--------|
| `quick` | 僅關鍵信號 | ~7個關鍵信號 |
| `standard` | 所有信號 | 30+信號 |
| `deep` | 包含行為分析 | 30+信號+行為 |
| `stealth` | 測試規避技術 | 對比配置 |

### 檢測類別

| 類別 | 圖標 | 描述 |
|------|------|------|
| Navigator | 🌐 | 瀏覽器navigator屬性 |
| WebDriver | 🤖 | 自動化框架信號 |
| CDP | 🔧 | Chrome DevTools協議 |
| Fingerprint | 👆 | 瀏覽器指紋信號 |
| Behavior | 🎯 | 行為模式檢測 |
| TLS | 🔐 | TLS指紋分析 |
| Network | 📡 | 網路時序和頭資訊 |
| DOM | 📄 | DOM屬性檢測 |

### API使用

```python
from botdetect_cli import BotDetector
from botdetect_cli.detector import DetectionConfig, DetectionMode

# 創建自定義配置的檢測器
config = DetectionConfig(
    mode=DetectionMode.STANDARD,
    browser_type="chromium",
    headless=True
)
detector = BotDetector(config)

# 執行檢測
report = detector.detect()

# 訪問結果
print(f"檢測分數: {report.scan_result.detection_score}%")
print(f"風險等級: {report.scan_result.risk_level}")
print(f"檢測到的信號: {report.scan_result.detected_signals}")

# 匯出報告
json_output = detector.export_results(report, "json")
html_output = detector.export_results(report, "html")
```

## 💡 設計理念

BotDetect-CLI的誕生源於對機器人檢測機制理解的需求。雖然CloakBrowser等專案展示了如何創建隱身瀏覽器，但BotDetect-CLI提供了**硬幣的另一面**——幫助開發者：

1. **測試網站** - 了解您的機器人檢測能看到哪些信號
2. **除錯自動化腳本** - 找出腳本被阻止的原因
3. **學習檢測技術** - 理解瀏覽器指紋識別的教育工具
4. **構建更好的安全** - 了解應該關注哪些信號

## 📦 部署

### 作為CLI工具

```bash
# 全局安裝
pip install botdetect-cli

# 任意位置執行
botdetect scan
```

### 作為Python庫

```python
# requirements.txt
botdetect-cli>=1.0.0

# 在程式碼中
from botdetect_cli import BotDetector
```

### Docker

```bash
docker build -t botdetect-cli .
docker run --rm botdetect-cli scan
```

## 🤝 貢獻指南

歡迎貢獻！請閱讀我們的貢獻指南：

1. Fork本倉庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 創建Pull Request

## 📄 開源協議

本專案採用MIT協議 - 詳見 [LICENSE](LICENSE) 檔案。

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
</p>
