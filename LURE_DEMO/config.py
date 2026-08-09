# config.py

import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS                          # bundled read-only assets
    ROOT_DIR = os.path.dirname(sys.executable)        # folder the .exe lives in
    ASSETS_DIR = os.path.join(BASE_DIR, "ASSETS")     # bundled directly under _MEIPASS/ASSETS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # .../Lure/LURE_DEMO
    ROOT_DIR = os.path.dirname(BASE_DIR)                     # .../Lure
    ASSETS_DIR = os.path.join(ROOT_DIR, "ASSETS")            # .../Lure/ASSETS (sibling folder)


def asset_path(*parts):
    return os.path.join(ASSETS_DIR, *parts)


BG_LOADING = asset_path("background", "loading_screen.png")
BG_HOME = asset_path("background", "home_screenbg.png")
BG_HANGAR = asset_path("background", "hanger.png")
BG_STORE = asset_path("background", "store.png")
BG_SUPPORT = asset_path("background", "support.png")
BG_SETTINGS = asset_path("background", "settings.png")
BG_CREDITS = asset_path("background", "credits.png")
BG_GAMEPLAY = asset_path("background", "gameplay.png")
BG_PAUSE = asset_path("background", "pause.png")

BTN_BOMB = asset_path("UI", "buttons", "bomb.png")
BTN_RESUME = asset_path("UI", "buttons", "resume_btn.png")
BTN_HOME_ICON = asset_path("UI", "buttons", "home_btn.png")
BTN_CLAIM = asset_path("UI", "buttons", "claim_btn.png")
BTN_PLAY = asset_path("UI", "buttons", "play_btn.png")
BTN_STORE = asset_path("UI", "buttons", "store_btn.png")
BTN_SUPPORT = asset_path("UI", "buttons", "support_btn.png")
BTN_BACK = asset_path("UI", "buttons", "back_btn.png")
BTN_SETTINGS = asset_path("UI", "buttons", "settings_btn.png")
BTN_TASKS = asset_path("UI", "buttons", "tasks.png")
BTN_DAILY_REWARD = asset_path("UI", "buttons", "daily_reward.png")
BTN_SCALER = asset_path("UI", "buttons", "scaler.png")
BTN_YES = asset_path("UI", "buttons", "yes_btn.png")
BTN_NO = asset_path("UI", "buttons", "no_btn.png")
BTN_BUY = asset_path("UI", "buttons", "buy_btn.png")
BTN_EQUIP = asset_path("UI", "buttons", "equip_btn.png")
BTN_UPGRADE = asset_path("UI", "buttons", "upgrade_btn.png")
BTN_PAUSE = asset_path("UI", "buttons", "pause_btn.png")
BTN_SHOOT = asset_path("UI", "buttons", "shoot_btn.png")
BTN_NEW_GAME = asset_path("UI", "buttons", "new_game.png")
BTN_CREDITS = asset_path("UI", "buttons", "credits.png")

OUTER_JOYSTICK = asset_path("UI", "buttons", "outer_joystick.png")
INNER_JOYSTICK = asset_path("UI", "buttons", "inner_joystick.png")

PAUSE_BTN_ANI_FRAMES = [
    asset_path("UI", "buttons", f"pause_btnani{i}.png") for i in range(1, 7)
]

MESSAGE_BOX = asset_path("UI", "Dialogue", "message_box.png")
DIALOGUE_FACE = asset_path("UI", "Dialogue", "dialogue_face.png")

COIN_HOLDER = asset_path("UI", "icons", "coin_holder.png")
DIAMOND_HOLDER = asset_path("UI", "icons", "diamond_holder.png")

COIN_PACK_ICONS = [
    asset_path("UI", "icons", f"coin{i}_btn.png") for i in range(1, 6)
]
DIAMOND_PACK_ICONS = [
    asset_path("UI", "icons", f"diamond{i}_btn.png") for i in range(1, 6)
]

PLAYER_ICON = asset_path("UI", "HUD", "player_icon.png")
HEALTH_BAR = asset_path("UI", "bars", "health_bar.png")
ARMOUR_BAR = asset_path("UI", "bars", "armour_bar.png")
UPPER_BAR = asset_path("UI", "bars", "upper_bar.png")
ENEMY_HEALTHBAR = asset_path("UI", "bars", "enemy_healthbar.png")

ENABLE_AUTOSHOOT = asset_path("UI", "Toggles", "enable_autoshoot.png")
DISABLE_AUTOSHOOT = asset_path("UI", "Toggles", "disable_autoshoot.png")
C_SLIDER = asset_path("UI", "Toggles", "c_slider.png")
P_SLIDER = asset_path("UI", "Toggles", "p_slider.png")

STAT_DAMAGE = asset_path("UI", "Inventory", "damage.png")
STAT_SPEED = asset_path("UI", "Inventory", "speed.png")
STAT_STRENGTH = asset_path("UI", "Inventory", "strength.png")
STAT_ENERGY = asset_path("UI", "Inventory", "energy.png")
STAT_HANDLING = asset_path("UI", "Inventory", "handling.png")

# ============================================================
# AUDIO
# ============================================================

AUDIO_DIR = asset_path("audio")
GAME_SONGS_DIR = os.path.join(AUDIO_DIR, "game song")
SFX_DIR = os.path.join(AUDIO_DIR, "sfx")

SONG_FILES = [
    os.path.join(GAME_SONGS_DIR, "Don't Give Me the Green Lyt.mp3"),
    os.path.join(GAME_SONGS_DIR, "Floatin'.mp3"),
    os.path.join(GAME_SONGS_DIR, "VVS.mp3"),
    os.path.join(GAME_SONGS_DIR, "Boy Đ Lyk Stress.mp3"),
]

SFX_BUTTON = os.path.join(SFX_DIR, "button_sound.mp3")
SFX_MOVEMENT = os.path.join(SFX_DIR, "movement_flight.mp3")
SFX_SHOOTING = os.path.join(SFX_DIR, "shooting.mp3")
# NOTE: expects a file named exactly "explosion.mp3" inside
# ASSETS/audio/sfx/. If the name differs even slightly, this will be
# skipped silently (no crash) rather than play.
SFX_EXPLOSION = os.path.join(SFX_DIR, "explosion.mp3")


# ============================================================
# SAVE FILE
# ============================================================

SAVE_DIR = os.path.join(ROOT_DIR, "save")
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")


# ============================================================
# SHIP DATA
# ============================================================

SHIPS_JSON_PATH = os.path.join(BASE_DIR, "data", "ships.json")


# ============================================================
# GLOBAL UI CONSTANTS
# ============================================================

BUTTON_PRESS_SCALE = 1
BUTTON_PRESS_DARKEN = 1
FADE_TRANSITION_DURATION = 0.25

LOADING_SCREEN_DURATION = 2.0

SONG_TOAST_DURATION = 2.0
SONG_TOAST_SLIDE_TIME = 0.55

ICON_SHUFFLE_INTERVAL = 2.0

DAILY_REWARD_COOLDOWN_HOURS = 24

TOP_RIGHT_ICON_SIZE_HINT = (0.1082, 0.2513)
TOP_RIGHT_ICON_POS_HINT = {"x": 0.88, "y": 0.78}

# ============================================================
# ENEMIES
# ============================================================

ENEMY_DIR = asset_path("characters", "enemies")
ENEMY_WEAPONS_DIR = asset_path("characters", "enemy weapons")

ENEMY_DEFS = [
    {
        "sprite": asset_path("characters", "enemies", "brute_scout.png"),
        "bullet": asset_path("characters", "enemy weapons", "brute_scout_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "brute_scout_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "brute_scout_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "digger_rig.png"),
        "bullet": asset_path("characters", "enemy weapons", "digger_rig_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "digger_rig_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "digger_rig_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "grinder.png"),
        "bullet": asset_path("characters", "enemy weapons", "grinder_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "grinder_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "grinder_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "long_fang.png"),
        "bullet": asset_path("characters", "enemy weapons", "long_fang.png"),
        "bomb": asset_path("characters", "enemy weapons", "long_fang_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "long_fang_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "mine_caster.png"),
        "bullet": asset_path("characters", "enemy weapons", "mine_caster_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "mine_caster_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "mine_caster_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "shade_craft.png"),
        "bullet": asset_path("characters", "enemy weapons", "shade_craft_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "shade_craft_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "shade_craft_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "shock_barge.png"),
        "bullet": asset_path("characters", "enemy weapons", "shock_barge_bullet.png"),
        "bomb": asset_path("characters", "enemy weapons", "shock_barge_bomb.png"),
        "explosion": asset_path("characters", "enemy weapons", "shock_barge_explosion.png"),
    },
    {
        "sprite": asset_path("characters", "enemies", "scrapling.png"),
        "bullet": asset_path("characters", "enemy weapons", "scrapling_bullet.png"),
        "bomb": None,
        "explosion": asset_path("characters", "enemy weapons", "shade_craft_explosion.png"),
    },
]