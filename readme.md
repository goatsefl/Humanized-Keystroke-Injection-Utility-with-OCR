---
# Undetectable AI Autotyper ![Python](https://img.shields.io/badge/python-3.x-blue.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

A stealthy, cross-platform desktop application designed to simulate human typing patterns. It converts text or images into keystrokes with variable speeds, distinct pause logic, and artificial errors to bypass anti-paste detection mechanisms.
---

## Overview

This tool solves the problem of "paste blocking" or "bot detection" in text fields. Instead of instantly dumping text, the Undetectable AI Autotyper acts as a virtual keyboard controller. It uses advanced randomization algorithms to vary keystroke delays, simulate typos, and perform backspace corrections, making the output indistinguishable from a human typist. It also includes OCR capabilities to type text directly from images.

---

## Features

### Modern UI

- Built with **CustomTkinter** for a clean, modern dark-mode interface.
- Responsive layout with intuitive controls.

### Human-Like Typing Simulation

- **Variable WPM:** Adjust typing speed from 20 to 300 Words Per Minute.
- **Artificial Accuracy:** Intentionally introduces typos based on a percentage slider.
- **Auto-Correction:** Simulates realizing a mistake, pausing, backspacing, and re-typing correctly.
- **Jitter/Variation:** Adds millisecond-level random variations to every key press.

### Optical Character Recognition (OCR)

- **Load from Image:** Extract text automatically from `.png`, `.jpg`, or `.bmp` files.
- Powered by Tesseract-OCR for high-accuracy reading.

### Playback Control

- **Smart Pausing:** Detects punctuation (., !, ?) and adds longer "thinking" pauses.
- **Flow Control:** Start, Pause, Resume, and Emergency Stop functionality.
- **Countdown Timer:** Gives you 3 seconds to switch focus to your target application before typing begins.

---

## Tech Stack

- **Python 3.10+**
- **CustomTkinter** (Modern GUI framework)
- **Pynput** (Keyboard event simulation)
- **Pytesseract** (OCR wrapper)
- **Pillow (PIL)** (Image processing)
- **Threading** (Non-blocking background execution)

---

## Prerequisites

### 1. Python

Ensure you have Python installed.

- **Windows:** Ensure "Add Python to PATH" is checked during installation.

### 2. Tesseract OCR (Critical)

This application requires the Tesseract engine to read text from images.

- **Windows:** [Download the installer here](https://github.com/UB-Mannheim/tesseract/wiki).
  - _Important:_ During installation, note the installation path (usually `C:\Program Files\Tesseract-OCR`). You may need to add this path to your System Environment Variables.
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/undetectable-autotyper.git
cd undetectable-autotyper
```

### 2. Create and Activate a Virtual Environment

**On Windows:**

```bash
python -m venv venv
.\venv\Scripts\activate
```

**On macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Create a file named `requirements.txt` with the content below, or install them manually.

**requirements.txt content:**

```text
customtkinter
Pillow
pytesseract
pynput
packaging
```

**Install command:**

```bash
pip install -r requirements.txt
```

---

## How to Run

1.  Navigate to the project directory.

BEFORE RUNNING : ALWAYS try running ```.\venv\Scripts\activate``` this before ```python app.py```
2.  Run the application:
    ```bash
    python app.py
    ```
3.  **Usage:**
    - Paste text into the main box OR click "Load Text from Image".
    - Adjust the sliders (WPM, Accuracy, Variation) to your preference.
    - Click **Start**.
    - You have **3 seconds** to click into the window (Notepad, Word, Browser, etc.) where you want the text typed.

---

## Future Roadmap

- **Global Hotkeys:** Ability to Start/Stop typing using F-keys (e.g., F6 to start) without clicking the app interface.
- **Preset Profiles:** Save configuration profiles (e.g., "Fast & Accurate" vs "Slow & Clumsy") for quick loading.
- **Rich Text Support:** Better handling of special characters and emojis.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
