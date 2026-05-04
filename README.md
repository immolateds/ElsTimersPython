# Elsword Timers
 
A always-on-top timer overlay for Elsword, designed to track title cooldowns in real time using global hotkeys — no need to alt-tab or click the window.
 
This is a Python rewrite of an original Java implementation (`ElswordTimersWithGlobalKeyListener.java`), rebuilt with a full visual overhaul and several quality-of-life upgrades.
 
---
 
## From Java to Python — What Changed
 
The original Java version used Swing (`JFrame`, `JPanel`, `Graphics.drawString`) to paint timer text directly onto a black canvas, with key bindings registered via `InputMap` and `ActionMap`. It worked, but had limitations:
 
- Keys only fired when the window was in focus
- No visual feedback beyond plain white text
- No sound
- No images
The Python rewrite addresses all of these:
 
| Feature | Java Original | Python Rewrite |
|---|---|---|
| UI framework | Swing (`JPanel` + `Graphics`) | Tkinter with card-style frames |
| Key listening | `WHEN_IN_FOCUSED_WINDOW` | `pynput` — works globally, even when minimized |
| Timer display | Plain white `drawString` | Color-coded text (white → amber → red) |
| Ready state | `"X is up!"` static text | Pulsing green `✦ READY` |
| Sound | None | Distinct beep per timer on expiry |
| Icons | None | PNG icons per title |
| State indicator | None | Color-coded badge at the top |
| Window | Fixed size | Resizable |
 
---
 
## Requirements
 
- Python 3.8 or higher
- Windows (required for `winsound`)
Install dependencies:
 
```bash
pip install pynput Pillow
```
 
---
 
## Setup
 
1. Place `elsword_timers.py` in a folder of your choice
2. Drop the three title icon images into the **same folder** as the script, named exactly:
   - `Title_1840.png` — Freed Shadow icon
   - `TITLE_2050.png` — Night Parade icon
   - `TITLE_2320.png` — TSS icon
3. Run the script:
```bash
python elsword_timers.py
```
 
The window will appear and stay on top of other applications automatically.
 
> If an image file is missing the script will still run — that timer row will just show no icon.
 
---
 
## How It Works
 
Activating a timer is a **two-step process** to avoid accidental triggers:
 
1. **Press Right Ctrl** to enter `CHANGING` state — the badge at the top will update to show you're in selection mode
2. **Press an arrow key** to select which title you're activating
3. **Press the activation key** for that title to start the timer
The window does not need to be focused at any point — all keys are listened to globally.
 
---
 
## Keybinds
 
### Step 1 — Enter selection mode
| Key | Action |
|-----|--------|
| Right Ctrl | Enter `CHANGING` state |
 
### Step 2 — Select a title
| Key | Title Selected |
|-----|----------------|
| ↑ Arrow | Freed Shadow |
| ↓ Arrow | Night Parade |
| ← Arrow | TSS |
 
### Step 3 — Activate the timer
| Key | Timer Started |
|-----|---------------|
| Left Ctrl | Freed Shadow (FS) |
| F, T, R, E, Q, A, S, or D | Night Parade (NP) |
| 5 | TSS |
 
---
 
## Timers
 
| Title | Duration | Beep Pitch |
|-------|----------|------------|
| Freed Shadow (FS) | 60 seconds | 880 Hz — high |
| Night Parade (NP) | 30 seconds | 520 Hz — mid |
| TSS | 30 seconds | 300 Hz — low |
 
---
 
## Visual Reference
 
| Timer text color | Meaning |
|-----------------|---------|
| 🟢 Pulsing green | Timer is ready |
| ⬜ White | Counting down — plenty of time |
| 🟡 Amber | 15 seconds or less remaining |
| 🔴 Red | 8 seconds or less remaining |
 
The card border also brightens while a timer is actively counting down, and the state badge at the top changes color depending on which title is selected.
 
---
 
## Customization
 
All key values are near the top of the script and easy to change:
 
- **`BEEP_SIGNATURES`** — adjust frequency (Hz) and duration (ms) per timer
- **`IMAGE_PATHS`** — point to different image files
- **`IMAGE_SIZE`** — change icon dimensions (default `42x42`)
- Timer durations are set in the `_on_press` method via `.start(seconds)`
