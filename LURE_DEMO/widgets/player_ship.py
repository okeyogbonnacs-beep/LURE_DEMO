# widgets/player_ship.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import PushMatrix, PopMatrix, Rotate


class PlayerShip(Widget):
    """
    Owns the player's ship sprite and its rotation.
    world_x/world_y hold the ship's true position in the game WORLD
    (which is larger than the screen). gameplay_screen.py updates
    these directly on movement, then syncs .pos each frame based on
    the current camera offset.
    """

    DEFAULT_SIZE = (90, 90)

    def __init__(self, sprite_path, size=None, **kwargs):
        super().__init__(size_hint=(None, None), **kwargs)
        self.size = size if size else self.DEFAULT_SIZE

        self.world_x = 0.0
        self.world_y = 0.0

        with self.canvas.before:
            PushMatrix()
            self._rotate = Rotate(angle=0, origin=self.center)

        self._img = Image(
            source=sprite_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))

        with self.canvas.after:
            PopMatrix()

        self.bind(pos=self._sync_rotate_origin, size=self._sync_rotate_origin)
        self.set_angle(90)

    def _sync_rotate_origin(self, *args):
        self._rotate.origin = self.center

    def set_angle(self, angle_deg):
        self._rotate.angle = angle_deg - 90

    def set_sprite(self, sprite_path):
        self._img.source = sprite_path
        self._img.reload()