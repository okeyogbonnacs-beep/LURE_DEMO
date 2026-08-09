# widgets/bullet.py

import math
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Rotate


class Projectile(Widget):
    """
    A moving bullet or bomb. world_x/world_y hold its position in the
    game WORLD; gameplay_screen.py syncs .pos each frame based on the
    current camera offset. Rotates to visually face its travel
    direction. is_bomb distinguishes bombs (which explode on impact)
    from bullets (which don't).
    """

    def __init__(self, source, size, world_pos, vx, vy, damage, owner,
                 is_bomb=False, explosion_source=None, **kwargs):
        super().__init__(size_hint=(None, None), size=size, pos=world_pos, **kwargs)
        self.world_x, self.world_y = world_pos
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.owner = owner  # "player" or "enemy"
        self.is_bomb = is_bomb
        self.explosion_source = explosion_source

        with self.canvas.before:
            PushMatrix()
            self._rotate = Rotate(angle=0, origin=self.center)

        self._img = Image(
            source=source,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=self._on_pos_change)

        with self.canvas.after:
            PopMatrix()

        angle_deg = math.degrees(math.atan2(vy, vx))
        self._rotate.angle = angle_deg - 90

    def _on_pos_change(self, *args):
        self._img.pos = self.pos
        self._rotate.origin = self.center

    def update(self, dt):
        self.world_x += self.vx * dt
        self.world_y += self.vy * dt

    def is_off_view(self, camera_x, camera_y, view_w, view_h, margin=150):
        sx = self.world_x - camera_x
        sy = self.world_y - camera_y
        return sx < -margin or sx > view_w + margin or sy < -margin or sy > view_h + margin