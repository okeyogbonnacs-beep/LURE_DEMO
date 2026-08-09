# ship_utils.py

import json

from config import SHIPS_JSON_PATH


def load_ship_sprite_filename(ship_id):
    """
    Look up the actual sprite filename for a ship id from ships.json,
    since some ids don't match their filename exactly (e.g. viper_x's
    sprite file is viperx.png, no underscore).
    """
    with open(SHIPS_JSON_PATH, "r") as f:
        ships = json.load(f)["ships"]
    for s in ships:
        if s["id"] == ship_id:
            return s["sprite"]
    return f"{ship_id}.png"