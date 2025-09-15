# NQ Master v3 Setup Guide

## Prerequisites

### 1. Install Python 3.8+
Download and install Python from [python.org](https://python.org)

### 2. Install Tesseract OCR
- **Windows**: Download from [GitHub Tesseract releases](https://github.com/tesseract-ocr/tesseract/releases)
- **Default install path**: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- **Mac**: `brew install tesseract`
- **Linux**: `sudo apt-get install tesseract-ocr`

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Tesseract Path (Windows)
If Tesseract is not in your PATH, edit `core/data_feeds.py` and uncomment/modify:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### 3. Run the Application
```bash
python main.py
```

## First Time Setup

### 1. Configure DOM Region
- Open your TopstepX trading platform
- In NQ Master v3, use **Tools > Auto-locate DOM** or press **Ctrl+A**
- Alternatively, use **Tools > Manual DOM Selection** or press **Ctrl+M**

### 2. Verify OCR Detection
- Check the status bar for "OCR: Active" (green)
- The price should show with "[OCR]" tag when working
- Falls back to "[YAHOO]" when OCR is unavailable

## Features Overview

### OCR + Yahoo Fusion Engine
- Real-time price capture from TopstepX DOM
- Yahoo Finance fallback for guaranteed data continuity
- Automatic switching between sources

### Signal Generation
- **Neutral/Bullish/Bearish** signals with confidence percentages
- Multi-timeframe confluence analysis (1m/5m/15m/60m/4h)
- Transparent reasoning for all signals

### GUI Panels
1. **Price & Signal**: Current price, live signal, key indicators
2. **Confluence Analysis**: Weighted scoring with contributing factors  
3. **Chart**: Price chart with signal markers and EMAs
4. **Signal History**: Timeline of recent signal changes
5. **News**: ForexFactory news feed with market sentiment

### Keyboard Shortcuts
- **Ctrl+A**: Auto-locate DOM
- **Ctrl+M**: Manual DOM selection  
- **F5**: Refresh data
- **Ctrl+Q**: Quit application

## Configuration

Settings are stored in `config.json` and auto-saved:
- OCR polling frequency
- Yahoo refresh interval
- Opening Range minutes
- News update frequency
- UI refresh rate

## Troubleshooting

### OCR Not Working
1. Verify Tesseract installation
2. Check TopstepX is visible on screen
3. Try manual DOM selection if auto-locate fails
4. Ensure DOM shows price column clearly

### No Yahoo Data
1. Check internet connection
2. Verify symbol "NQ=F" is correct
3. May need VPN if geographically restricted

### Performance Issues
1. Increase polling intervals in config
2. Close unnecessary applications
3. Ensure adequate system resources

## Building Executable

To create a standalone .exe:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "NQ_Master_v3" main.py
```

The executable will be in the `dist/` folder.