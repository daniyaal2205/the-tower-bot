import cv2
import numpy as np
import subprocess
import time
import os
import sys
import random

# --- SETUP: Ensure ADB is found ---
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir) 

adb_dir = os.path.join(script_dir, "platform-tools")
if os.path.isdir(adb_dir):
    os.environ["PATH"] = adb_dir + os.pathsep + os.environ["PATH"]

# --- CONFIGURATION ---
IMAGES_DIR = "The Tower Buttons"
THRESHOLD = 0.7
DEVICE_ID = None

# Timers (seconds)
GEM_INTERVAL_MIN = 180
GEM_INTERVAL_MAX = 200
DEFENCE_INTERVAL = 120
ATTACK_INTERVAL = 120
QUEST_INTERVAL = 180 # Check quests every 3 minutes (Chill mode)
LOOP_INTERVAL = 30   # Capture screen every 30 seconds (Ultra Chill)

# State - Set to 0 so they trigger IMMEDIATELY on start for testing
last_gem_time = 0
last_defence_time = 0
last_attack_time = 0
last_quest_time = 0

# --- ADB & UTILS ---

def get_connected_device():
    try:
        result = subprocess.run("adb devices", shell=True, capture_output=True, text=True)
        lines = result.stdout.strip().split("\n")
        for line in lines[1:]: 
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                return parts[0]
    except Exception as e:
        print(f"Error checking devices: {e}")
    return None

def refresh_connection():
    """Forces a refresh of the device ID."""
    global DEVICE_ID
    print("Connection lost? Searching for device...")
    DEVICE_ID = None
    while not DEVICE_ID:
        DEVICE_ID = get_connected_device()
        if DEVICE_ID:
            print(f"Reconnected: {DEVICE_ID}")
            return True
        print("Waiting for device...")
        time.sleep(5)
    return True

def run_adb(command):
    global DEVICE_ID
    if not DEVICE_ID:
        if not refresh_connection(): return False
    
    full_cmd = f"adb -s {DEVICE_ID} {command}"
    try:
        subprocess.run(full_cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        print("ADB command failed. Device might be disconnected.")
        DEVICE_ID = None # Force re-check next time
        return False

def get_screen():
    global DEVICE_ID
    if not DEVICE_ID: 
        if not refresh_connection(): return None
        
    try:
        if not DEVICE_ID: return None
        
        # Throttling: Wait a bit to let ADB/Emulator breathe
        time.sleep(0.5)
        
        # RAM Capture: adb exec-out screencap -p
        cmd = f"adb -s {DEVICE_ID} exec-out screencap -p"
        
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if proc.returncode != 0:
            print("ADB capture failed. forcing reconnect.")
            DEVICE_ID = None
            return None
            
        return cv2.imdecode(np.frombuffer(proc.stdout, np.uint8), cv2.IMREAD_COLOR)
        
    except subprocess.CalledProcessError:
        print("Failed to capture screen.")
        DEVICE_ID = None # Force re-check
        return None

def tap_random(x, y, w, h):
    margin_w = int(w * 0.1)
    margin_h = int(h * 0.1)
    rand_x = x + random.randint(margin_w, w - margin_w)
    rand_y = y + random.randint(margin_h, h - margin_h)
    print(f" > Clicking ({rand_x}, {rand_y})")
    run_adb(f"shell input tap {rand_x} {rand_y}")

def swipe(x1, y1, x2, y2, duration=500):
    print(f" > Swiping ({x1},{y1}) -> ({x2},{y2})")
    run_adb(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")

def random_sleep(min_s=1.0, max_s=2.0):
    time.sleep(random.uniform(min_s, max_s))

# --- CORE LOGIC ---

def find_image(screen, image_name, threshold=0.8):
    """Finds an image on the screen. Returns (x, y, w, h) or None."""
    if screen is None: return None
    
    path = os.path.join(IMAGES_DIR, image_name)
    if not os.path.exists(path):
        # Silent warning to avoid spamming console
        return None
        
    template = cv2.imread(path)
    if template is None: return None
    
    # Safety Check: Ensure dimensions and type match
    if screen.shape[2] != template.shape[2]:
        # Convert both to BGR if needed, but usually this means one has alpha channel
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR) if template.shape[2] == 4 else template
        screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR) if screen.shape[2] == 4 else screen
        
    try:
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.6: # Debug info
             print(f"Checking {image_name}: {max_val:.2f}")

        
        if max_val >= threshold:
            h, w = template.shape[:2]
            return (max_loc[0], max_loc[1], w, h)
            
    except cv2.error as e:
        print(f"OpenCV Error matching {image_name}: {e}")
        
    return None



def click_image(image_name, threshold=0.8):
    """Takes a screenshot, finds, and clicks the image."""
    screen = get_screen()
    if screen is None: return False

    
    match = find_image(screen, image_name, threshold)
    if match:
        x, y, w, h = match
        print(f"Found {image_name} ({x},{y})")
        tap_random(x, y, w, h)
        return True
    return False

def handle_defence_upgrade():
    print("running defence upgrade sequence...")
    # 1. Click Defence Tab
    if not click_image("Defence.png"):
        print("Could not find Defence button.")
        return
    
    random_sleep(1.5, 2.5) # Wait for panel
    
    # 2. Find Health Label
    screen = get_screen()
    if screen is None: return
    
    # Use EXACT logic for Health to anchor
    health = find_image(screen, "Health.png", 0.7) 
    if health:
        print("Found Health label. Searching for Upgrade button...")
        hx, hy, hw, hh = health
        
        path = os.path.join(IMAGES_DIR, "Generic Upgrade.png")
        if not os.path.exists(path): return
        template = cv2.imread(path)
        
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"Generic Upgrade best match: {max_val:.2f}")
        
        h, w = template.shape[:2]
        
        locs = np.where(res >= 0.5)
        points = list(zip(*locs[::-1]))
        
        best_btn = None
        min_dist = 99999
        
        for pt in points:
            dist = ((pt[0] - hx)**2 + (pt[1] - hy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                best_btn = (pt[0], pt[1], w, h)
        
        if best_btn:
             if min_dist < 600:
                print(f"Found Upgrade button {int(min_dist)}px from Health.")
                tap_random(*best_btn)
             else:
                print(f"Nearest upgrade button was too far ({int(min_dist)}px).")
        else:
            print("No Generic Upgrade buttons found.")
            
        # Final confirmation click on the Tab (Only if we were actually inside)
        random_sleep(0.5, 1.0)
        click_image("Defence.png")
            
    else:
        print("Health label not found.")

def has_red_dot(screen, x, y, w, h):
    """Checks if the region contains red pixels (Notification Dot)."""
    # Crop the button area
    roi = screen[y:y+h, x:x+w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    
    # Red has two ranges in HSV (wrap around 0/180)
    # Range 1: 0-10 (Hue), Sat > 100, Val > 100
    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    
    # Range 2: 170-180 (Hue)
    lower2 = np.array([170, 100, 100])
    upper2 = np.array([180, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = mask1 + mask2
    
    red_pixels = cv2.countNonZero(mask)
    if red_pixels > 0:
        print(f" > Red Pixels found: {red_pixels}")
    
    # If we see enough red pixels, it's a notification
    return red_pixels > 20

def handle_quests(screen):
    """Complex Quest Sequence: Expand -> Quests -> Claim -> Scroll -> Return"""
    
    # screen = get_screen() <-- Removed! Use passed screen
    if screen is None: return

    # 1. Check Expand Trigger
    # Using normal threshold to finding the BUTTON
    expand_btn = find_image(screen, "Expand.png", threshold=0.7)
    if not expand_btn: 
        return
        
    ex, ey, ew, eh = expand_btn
    ex, ey, ew, eh = expand_btn
    
    # User Request: "click expand on whatever timer... then check for red dot on quests"
    # No Red Dot check for Expand anymore.
    print("Clicking Expand (Scheduled)...")
    tap_random(ex, ey, ew, eh)
    random_sleep(1.5, 2.5)

    # 2. Click Quests
    # Note: We need a fresh screen here because the menu just opened
    screen = get_screen() 
    if screen is None: return

    quests_btn = find_image(screen, "Quests.png", threshold=0.7)
    
    if not quests_btn:
        print("Quests button not found.")
        # Try to close whatever opened
        click_image("X.png")
        return
        
    qx, qy, qw, qh = quests_btn
    print("Found Quests button. Checking for Red Dot...")
    
    # Check red dot on Quests button
    if not has_red_dot(screen, qx, qy, qw, qh):
        print(" > No Red Dot on Quests. Closing...")
        click_image("X.png") 
        return
        
    print("Red Dot Confirmed! Clicking Quests...")
    tap_random(qx, qy, qw, qh)
    
    print("Entered Quests menu.")
    random_sleep(2.0, 3.0)

    # Helper to claim all visible rewards
    def collect_visible():
        found_any = False
        # Loop until no more Claim buttons
        while True:
            if click_image("Claim.png", threshold=0.7):
                print("Clicked Claim!")
                found_any = True
                random_sleep(0.5, 1.0)
            # Also check for 'Reward' buttons
            elif click_image("Reward.png", threshold=0.7):
                print("Clicked Reward!")
                found_any = True
                random_sleep(0.5, 1.0)
            else:
                break
        return found_any

    # 3. Collect Initial Rewards
    collect_visible()
    
    # 4. Scroll to find more
    # "click and drag the reward scroll button to scroll to the right"
    screen = get_screen()
    scroll_btn = find_image(screen, "Reward Scroll.png", threshold=0.7)
    if scroll_btn:
        x, y, w, h = scroll_btn
        print("Found Scroll button. Dragging right...")
        # Swipe from center of button to right
        start_x = x + w // 2
        start_y = y + h // 2
        
        # Scroll Right (Reveal content on Right) = Drag Finger LEFT
        # User said: "move to the left side"
        end_x = start_x - 500 
        swipe(start_x, start_y, end_x, start_y, duration=1500)
        
        # Double swipe just in case
        random_sleep(0.5, 1.0)
        swipe(start_x, start_y, end_x, start_y, duration=1500)
        
        random_sleep(1.5, 2.5)
        
        # 5. Collect again after scroll
        collect_visible()
    else:
        print("Reward Scroll button not found.")

    # 6. Skip (Handle Ads if they appeared during claiming)
    if click_image("Skip.png"):
        print("Clicked Skip (Quest Sequence).")
        random_sleep(1.0, 2.0)

    # 7. Return to Game
    if click_image("Return to Game.png"):
        print("Returned to Game.")
        
    # 8. Close X (If any remnants remain)
    random_sleep(0.5, 1.0)
    if click_image("X.png"):
        print("Clicked X button.")

def handle_attack_upgrade():
    print("running attack upgrade sequence...")
    # 1. Click Attack Tab
    if not click_image("Attack.png"):
        print("Could not find Attack button.")
        return
    
    random_sleep(1.5, 2.5) # Wait for panel
    
    # 2. Find Damage Label
    screen = get_screen()
    if screen is None: return
    
    # Use EXACT logic for Damage to anchor
    damage = find_image(screen, "Damage.png", 0.7) 
    if damage:
        print("Found Damage label. Searching for Upgrade button...")
        dx, dy, dw, dh = damage
        
        # Use the specific button the user created for Damage
        path = os.path.join(IMAGES_DIR, "generic damage upgrade button.png")
        if not os.path.exists(path): return
        template = cv2.imread(path)
        if template is None: return
        
        res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"Damage Upgrade best match: {max_val:.2f}")

        h, w = template.shape[:2]
        
        # Use a lower threshold (0.5) because the price text changes significantly
        locs = np.where(res >= 0.5)
        points = list(zip(*locs[::-1]))
        
        best_btn = None
        min_dist = 99999
        
        for pt in points:
            dist = ((pt[0] - dx)**2 + (pt[1] - dy)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                best_btn = (pt[0], pt[1], w, h)
        
        if best_btn:
             # Relax distance check slightly for Attack tab
             if min_dist < 800:
                print(f"Found Upgrade button {int(min_dist)}px from Damage.")
                tap_random(*best_btn)
             else:
                print(f"Nearest upgrade button was too far ({int(min_dist)}px).")
        else:
            print("No Generic Upgrade buttons found.")

        # Final confirmation click on the Tab (Only if we were actually inside)
        random_sleep(0.5, 1.0)
        click_image("Attack.png")
            
    else:
        print("Damage label not found.")

def main():
    print(f"Bot starting in: {script_dir}")
    print(f"Images folder: {IMAGES_DIR}")
    print("Press Ctrl+C to stop.")
    
    global DEVICE_ID, last_gem_time, last_defence_time, last_attack_time, last_quest_time, last_x_time, last_action_time
    DEVICE_ID = get_connected_device()
    if DEVICE_ID: print(f"Connected: {DEVICE_ID}")
    else: return

    # Stagger Upgrades so they happen 1 minute apart
    # Defence triggers immediately (0), Attack triggers in 60s (current - 60 < 120 check)
    current_t = time.time()
    last_action_time = 0 # Track when the LAST major upgrade happened
    round_start_time = current_t # Track when this SPECIFIC round started
    
    # Initialize normally - the "Gap" logic will handle the staggering naturally
    last_defence_time = 0 
    last_attack_time = 0 
    last_x_time = 0 

    while True:
        try:
            current_time = time.time()
            
            # Get screen ONCE per loop to be efficient
            screen = get_screen()
            if screen is None: continue 

            # --- 1. CRITICAL: Game Over / Restart ---
            if find_image(screen, "Game Over.png"):
                print("Game Over detected!")
                if click_image("Home.png"):
                    print("Going Home...")
                    random_sleep(2.0, 3.0)
                    click_image("Start Battle.png")
                    print("Battle Started. Resetting Round Timer.")
                    round_start_time = time.time() # Reset logic info
                    random_sleep(2.0, 3.0)
                    continue 
            
            if find_image(screen, "Start Battle.png"):
                 click_image("Start Battle.png")
                 print("Battle Started. Resetting Round Timer.")
                 round_start_time = time.time()
                 random_sleep(2.0, 3.0)
            



            
            # --- 2. GEMS ---
            if current_time - last_gem_time > random.randint(GEM_INTERVAL_MIN, GEM_INTERVAL_MAX):
                if click_image("Claim Gems.png", threshold=0.8):
                    print("Gems Claimed!")
                # Add slight fuzz (-5s to +5s) to the reset time so it drifts
                last_gem_time = current_time + random.randint(-5, 5)
            
            # --- 3. DEFENCE UPGRADES (Priority 1) ---
            # Run if Interval passed AND we haven't done another action recently (Gap > 60s)
            if (current_time - last_defence_time > DEFENCE_INTERVAL) and \
               (current_time - last_action_time > 60):
                handle_defence_upgrade()
                # Drift the next check by +/- 5 seconds
                last_defence_time = current_time + random.randint(-5, 5)
                last_action_time = current_time

            # --- 4. ATTACK UPGRADES (Priority 2) ---
            # Run if Interval passed AND Gap > 60s
            # AND: Only runs for the first hour (3600s) of the round
            if (current_time - last_attack_time > ATTACK_INTERVAL) and \
               (current_time - last_action_time > 60):
               
               if (current_time - round_start_time < 3600):
                   handle_attack_upgrade()
                   # Drift the next check by +/- 5 seconds
                   last_attack_time = current_time + random.randint(-5, 5)
                   last_action_time = current_time
               else:
                   print(" > 1 Hour Limit reached: Skipping Attack Upgrade.")
                   # Still update the timer so we don't spam this message every loop
                   # But DO NOT update last_action_time, so Defence can run freely
                   last_attack_time = current_time + 120 # Check again in 2 mins
            
            # --- 5. QUESTS (Way more chill - check every few mins) ---
            if current_time - last_quest_time > QUEST_INTERVAL:
                handle_quests(screen)
                last_quest_time = current_time + random.randint(-10, 10)

            # --- 6. X BUTTON (Check every 1 minute) ---
            if current_time - last_x_time > 60:
                if click_image("X.png"):
                    print("Clicked X (Scheduled).")
                last_x_time = current_time + random.randint(-5, 5)

            time.sleep(LOOP_INTERVAL)

        except KeyboardInterrupt:
            print("\nStopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
