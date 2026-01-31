# The Tower - Auto Clicker Bot 🤖

A robust, Python-based auto-clicker for "The Tower" game, designed to run on Android Emulators (BlueStacks/LDPlayer) via ADB.

## 🚀 Features

*   **"Chill Mode" Architecture**: Smart intervals to check Quests (3 mins), Ads (1 min), and Upgrades (2 mins) to avoid detection and reduce CPU usage.
*   **RAM-Only Capture**: Uses `adb exec-out` to pipe screenshots directly to memory. **Zero SSD wear.**
*   **"The Survivalist" Strategy**: 
    *   Automatically manages upgrades for both Attack and Defence.
    *   **Smart Cutoff**: Stops upgrading Attack after 1 hour to focus purely on Defence for deep runs.
*   **Robust Recovery**: Handles game crashes, "Game Over" screens, and random popups (Skip/X buttons).
*   **Staggered Actions**: Ensures upgrades never overlap, keeping the bot human-like.

## 📋 Prerequisites

1.  **Python 3.x**
2.  **Android Emulator** (BlueStacks / LDPlayer)
3.  **ADB** (Android Debug Bridge) enabled on the emulator.

## ⚙️ Setup

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/the-tower-bot.git
    cd the-tower-bot
    ```

2.  **Install Dependencies**:
    ```bash
    pip install opencv-python numpy
    ```

3.  **Connect ADB**:
    *   Make sure your emulator is running.
    *   The bot will attempt to auto-connect.
    *   If needed, update the `platform-tools` path in `bot.py`.

4.  **Run**:
    ```bash
    python bot.py
    ```

## 🎮 Configuration

Edit the constants at the top of `bot.py` to tune the bot:

```python
GEM_INTERVAL_MIN = 180   # Gem Collection (seconds)
DEFENCE_INTERVAL = 120   # Defence Upgrades
ATTACK_INTERVAL = 120    # Attack Upgrades
QUEST_INTERVAL = 180     # Quest Sequence
LOOP_INTERVAL = 30       # Main Loop Delay
```

## 📝 License

This project is for educational purposes only. Use at your own risk.
