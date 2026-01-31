# The Tower - Auto Clicker Bot 🤖

A high-performance, intelligent auto-clicker for "The Tower" (Android), custom-built to run 24/7 on emulators with minimal resource usage and human-like behavior.

## 🧠 Technical Architecture

The bot runs on a **Python 3** core and interfaces with the Android Emulator via **ADB (Android Debug Bridge)**.

### Core Technologies
*   **OpenCV (cv2)**: Uses `SIFT`-like Template Matching (`cv2.matchTemplate`) to recognize game buttons and notification dots with variable confidence thresholds (0.5 - 0.9).
*   **ADB Shell**: Sends touch events (`input tap`, `input swipe`) and captures screen data.
*   **Direct-to-RAM Capture**: 
    *   *Old Method*: Save to disk -> Read file (Slow, SSD wear).
    *   *Current Method*: `adb exec-out screencap -p` pipes raw binary data directly to Python's `stdin`. We decode this in memory using `numpy` and `cv2`. **Zero SSD writes, <50ms latency.**

## ⚙️ The "Child Mode" Logic Engine

To prevent detection and emulator crashes, the bot does **not** check everything every frame. Instead, it uses a **Staggered Interval System**:

| Routine | Interval | Priority | Description |
| :--- | :--- | :--- | :--- |
| **Main Loop** | 30s | Low | The bot sleeps for 30s between full cycles. |
| **Gems** | 180s | Med | Checks for floating gems or the "Claim Gems" button. |
| **Defense** | 120s | High | Upgrades Defense stats (Health, etc). |
| **Attack** | 120s | High | Upgrades Attack stats (Damage, etc). |
| **Quests** | 180s | Low | complex sub-routine to collect mission rewards. |
| **X Button** | 60s | High | Checks for random "Close" (X) buttons to clear ads/popups. |

**Randomization**: All timers have a random "drift" (+/- 5-10s) and all clicks have random spatial offsets (+/- 10%) to mime human inaccuracy.

---

## 🛡️ Game Strategies

### 1. "The Survivalist" (Time-Based Cutoff)
Deep runs require switching focus from Attack to pure Defense.
*   **0 - 60 Minutes**: The bot upgrades **BOTH** Attack and Defense evenly (staggered by 60s so they never overlap).
*   **60+ Minutes**: The bot **HARD STOPS** upgrading Attack. All resources are funnelled 100% into Defense/Health to survive higher waves.
*   **Reset**: Detects "Game Over" or "Start Battle" to automatically reset the internal round timer.

### 2. Maintenance & Recovery
*   **Start Battle**: Auto-detects the main menu and starts a new round.
*   **Game Over**: Clicks "Home" -> "Start" to loop indefinitely.
*   **Global Recovery**: If a menu fails to open (network lag), the bot aborts the sequence and retry's later instead of clicking blindly.

---

## 📂 Sub-Routines Detailed

### 💎 Gem Collection (`Claim Gems.png`)
*   **Trigger**: Every ~3 mins.
*   **Logic**: Scans the screen for the specific "Claim" button.
*   **Threshold**: 0.8 (High precision) to avoid false positives.

### ⚔️ Upgrade Logic (Attack & Defense)
1.  **Open Tab**: Clicks the "Sword" (Attack) or "Shield" (Defense) icon.
2.  **Verify**: Checks if the "Damage" or "Health" text label is visible. If not, it assumes the menu failed to open and aborts.
3.  **Find Button**: Scans for the generic "Buy Upgrade" button *specifically near* the Label.
4.  **Confirm**: After buying, it clicks the Tab icon again to ensure the UI is reset.

### 📜 Quest Automation (The Complex One)
1.  **Expand**: Checks every 3 mins. Clicks the "Expand" arrow.
2.  **Red Dot Check**: Analyzes the pixels of the "Quests" button.
    *   **No Red Dot**: Immediately clicks **X** to close.
    *   **Red Dot Found**: Clicks to open.
3.  **Claim Loop**: Spam-clicks the "Claim" button until none are left.
4.  **Scroll**: Performs a "Swipe Left" gesture (simulating dragging the list right) to reveal hidden rewards.
5.  **Skip/Close**: Handles "Skip" buttons (for ads) and "Return to Game".

---

## �️ Installation & Usage

1.  **Install**: `pip install opencv-python numpy`
2.  **Connect**: Open Emulator, ensure ADB is on.
3.  **Run**: `python bot.py`
4.  **Stop**: `Ctrl+C` in the terminal.

Created by **Antigravity**. 🚀
