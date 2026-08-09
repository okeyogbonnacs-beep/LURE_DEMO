# widgets/enemy_ship.py

import random
from kivy.uix.widget import Widget
from kivy.uix.image import Image


class EnemyShip(Widget):
    """
    A single enemy. world_x/world_y hold its position in the game
    WORLD (larger than the screen). gameplay_screen.py updates these
    directly and syncs .pos each frame from the current camera offset.
    """

    def __init__(self, enemy_def, size, pos, health, **kwargs):
        super().__init__(size_hint=(None, None), size=size, pos=pos, **kwargs)
        self.enemy_def = enemy_def
        self.max_health = health
        self.health = health

        # "pos" here is the initial WORLD position, not screen position
        self.world_x, self.world_y = pos

        self.state = "wander"
        self.wander_angle = random.uniform(0, 360)
        self.wander_timer = random.uniform(0, 2.0)

        self.shoot_timer = random.uniform(0.5, 2.0)
        self.bomb_timer = random.uniform(1.0, 4.0)
        self.contact_timer = 0.0

        self._img = Image(
            source=enemy_def["sprite"],
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0