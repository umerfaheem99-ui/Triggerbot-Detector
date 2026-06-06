# CPS Counter — by r3mu

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

**A clean, real-time CPS (Clicks Per Second) counter with keystrokes overlay**  
*Works with any game — Minecraft, Valorant, CS2, and more*

[▶ YouTube](https://www.youtube.com/@r3mu2) • [◈ Discord](https://discord.com/invite/isvault)

</div>

---

## Features

- **Real-time CPS tracking** — Left and Right mouse button separately
- **Works with any game** — fullscreen overlay stays on top no matter what you're playing
- **Keystrokes overlay** — W A S D + LMB + RMB + SPACE with smooth animations
- **Auto fullscreen detection** — switches to compact overlay when you go fullscreen
- **Always on top** — stays visible over any game
- **Smooth animations** — key press/release fade effects
- **Peak CPS tracking** — tracks your highest CPS
- **Total click counter** — counts all clicks in session
- **Draggable** — move anywhere on screen
- **Size options** — S / M / L window sizes
- **Opacity control** — adjust overlay transparency
- **Splash screen + loading animation**

---

## Requirements

- Windows 10 / 11
- Python 3.11+

---

## Installation & Usage

**1. Clone the repo**
```bash
git clone https://github.com/r3mu2/cps-counter.git
cd cps-counter
```

**2. Install dependencies**
```bash
pip install pynput
```

**3. Run**
```bash
python cps_counter_r3mu.py
```

---

## Build EXE (optional)

> ⚠️ Compiled executables may trigger antivirus false positives due to `pynput` using global mouse/keyboard hooks. The source code is fully open for inspection. Running the `.py` directly is recommended.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed cps_counter_r3mu.py
```

---

## How it works

| Mode | Trigger | What you see |
|---|---|---|
| **Main UI** | Normal desktop | Full window with CPS cards, links, size controls |
| **Compact overlay** | Any fullscreen game | Keystrokes mod style mini overlay |

The app checks every second if a fullscreen window is active and auto-switches between modes with a smooth fade transition.

---

## Antivirus Notice

Some antiviruses may flag the compiled `.exe` as suspicious. This is a **false positive** caused by `pynput` using global mouse & keyboard hooks. The source code is 100% open — feel free to inspect every line. Running `python cps_counter_r3mu.py` directly will never trigger any antivirus.

---

## Links

- 📺 YouTube — [youtube.com/@r3mu2](https://www.youtube.com/@r3mu2)
- 💬 Discord — [discord.com/invite/isvault](https://discord.com/invite/isvault)

---

<div align="center">
made with ❤️ by <b>r3mu</b>
</div>
