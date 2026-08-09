# widgets/explosion.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock


class Explosion(Widget):
    """
    One-shot explosion visual at a WORLD position, shown briefly then
    removed. Only bombs trigger this (not bullets). gameplay_screen.py
    syncs .pos each frame based on the current camera offset, so the
    explosion stays anchored in world space even if the camera pans
    while it's still visible.
    """

    DURATION = 0.35

    def __init__(self, source, world_center, size, on_finished=None, **kwargs):
        super().__init__(size_hint=(None, None), size=size, **kwargs)
        self.world_x = world_center[0] - size[0] / 2
        self.world_y = world_center[1] - size[1] / 2
        self._on_finished = on_finished

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
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))

        Clock.schedule_once(self._finish, self.DURATION)

    def _finish(self, dt):
        if self._on_finished:
            self._on_finished(self)