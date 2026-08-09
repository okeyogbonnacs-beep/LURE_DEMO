# save_manager.py

import json
import os
import time

from config import SAVE_DIR, SAVE_FILE, DAILY_REWARD_COOLDOWN_HOURS


DEFAULT_SAVE_DATA = {
    "gold": 0,
    "diamonds": 0,
    "settings": {
        "brightness": 1.0,
        "volume": 1.0,
        "platform_mode": "mobile",  # "mobile" or "pc"
        "keybinds": {
            "move_left": "a",
            "move_right": "d",
            "move_up": "w",
            "move_down": "s",
            "shoot": "spacebar",
            "bomb": "e",
            "pause": "escape",
        },
    },
    "daily_reward": {
        "last_claimed": None,   # unix timestamp, None = never claimed
    },
    "tasks": {
        # task_id: progress/claimed state, for future persistence
    },
    "equipped_ship": "rustwing",
    "owned_ships": ["rustwing"],
    "ship_upgrades": {
        # ship_id: upgrade level (int)
    },
}


class SaveManager:
    """
    Handles loading/saving persistent player data to a JSON save file.
    """

    def __init__(self):
        self.data = {}
        self._ensure_save_dir()
        self.load()

    # --------------------------------------------------------
    # CORE LOAD / SAVE
    # --------------------------------------------------------

    def _ensure_save_dir(self):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    def load(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r") as f:
                    loaded = json.load(f)
                self.data = self._merge_defaults(DEFAULT_SAVE_DATA, loaded)
            except (json.JSONDecodeError, IOError):
                self.data = json.loads(json.dumps(DEFAULT_SAVE_DATA))
                self.save()
        else:
            self.data = json.loads(json.dumps(DEFAULT_SAVE_DATA))
            self.save()

    def save(self):
        self._ensure_save_dir()
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except IOError as e:
            print(f"[SaveManager] Failed to save: {e}")

    def _merge_defaults(self, defaults, loaded):
        """Recursively fill in any missing keys from defaults into loaded data."""
        result = dict(loaded)
        for key, value in defaults.items():
            if key not in result:
                result[key] = value
            elif isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = self._merge_defaults(value, result[key])
        return result

    def reset(self):
        """Used by New Game confirmation - wipes save back to defaults."""
        self.data = json.loads(json.dumps(DEFAULT_SAVE_DATA))
        self.save()

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    def get_gold(self):
        return self.data.get("gold", 0)

    def get_diamonds(self):
        return self.data.get("diamonds", 0)

    def add_gold(self, amount):
        self.data["gold"] = self.get_gold() + amount
        self.save()
        return self.data["gold"]

    def add_diamonds(self, amount):
        self.data["diamonds"] = self.get_diamonds() + amount
        self.save()
        return self.data["diamonds"]

    # --------------------------------------------------------
    # DAILY REWARD
    # --------------------------------------------------------

    def get_daily_reward_last_claimed(self):
        return self.data.get("daily_reward", {}).get("last_claimed")

    def is_daily_reward_available(self):
        last = self.get_daily_reward_last_claimed()
        if last is None:
            return True
        elapsed_hours = (time.time() - last) / 3600.0
        return elapsed_hours >= DAILY_REWARD_COOLDOWN_HOURS

    def get_daily_reward_seconds_remaining(self):
        last = self.get_daily_reward_last_claimed()
        if last is None:
            return 0
        elapsed = time.time() - last
        remaining = (DAILY_REWARD_COOLDOWN_HOURS * 3600) - elapsed
        return max(0, int(remaining))

    def claim_daily_reward(self):
        if "daily_reward" not in self.data:
            self.data["daily_reward"] = {}
        self.data["daily_reward"]["last_claimed"] = time.time()
        self.save()

    # --------------------------------------------------------
    # SETTINGS
    # --------------------------------------------------------

    def get_settings(self):
        return self.data.get("settings", {})

    def set_setting(self, key, value):
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"][key] = value
        self.save()

    def set_keybind(self, action, key):
        self.data["settings"].setdefault("keybinds", {})[action] = key
        self.save()

    # --------------------------------------------------------
    # SHIP OWNERSHIP / EQUIP / UPGRADE
    # --------------------------------------------------------

    def get_owned_ships(self):
        return self.data.get("owned_ships", ["rustwing"])

    def is_ship_owned(self, ship_id):
        return ship_id in self.get_owned_ships()

    def buy_ship(self, ship_id, cost):
        """
        Attempts to purchase a ship. Returns True if successful
        (or already owned), False if not enough gold.
        """
        if self.is_ship_owned(ship_id):
            return True
        if self.get_gold() < cost:
            return False

        self.data["gold"] = self.get_gold() - cost
        owned = self.data.setdefault("owned_ships", ["rustwing"])
        owned.append(ship_id)
        self.save()
        return True

    def get_equipped_ship(self):
        return self.data.get("equipped_ship", "rustwing")

    def set_equipped_ship(self, ship_id):
        self.data["equipped_ship"] = ship_id
        self.save()

    def get_ship_upgrade_level(self, ship_id):
        return self.data.get("ship_upgrades", {}).get(ship_id, 0)

    def upgrade_ship(self, ship_id, cost):
        """
        Attempts to upgrade a ship. Returns True if successful,
        False if not enough gold.
        """
        if self.get_gold() < cost:
            return False

        self.data["gold"] = self.get_gold() - cost
        upgrades = self.data.setdefault("ship_upgrades", {})
        upgrades[ship_id] = upgrades.get(ship_id, 0) + 1
        self.save()
        return True


# Singleton instance used across the whole app
save_manager = SaveManager()