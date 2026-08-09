# widgets/scrolling_background.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image

from config import BG_GAMEPLAY


class ScrollingBackground(Widget):
    """
    A single large static background image sized to the game WORLD
    (bigger than the screen). It does NOT move/scroll itself - it
    stays exactly where placed. gameplay_screen.py repositions it
    each frame via .pos = (-camera_x, -camera_y), so as the camera
    pans, different parts of this large image become visible. No
    looping/tiling - panning is clamped to the image's real edges.
    """

    def __init__(self, world_size, **kwargs):
        super().__init__(size_hint=(None, None), size=world_size, **kwargs)

        self._img = Image(
            source=BG_GAMEPLAY,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))