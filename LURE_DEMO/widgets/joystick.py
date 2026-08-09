# widgets/joystick.py

import math
from kivy.uix.widget import Widget
from kivy.uix.image import Image

from config import OUTER_JOYSTICK, INNER_JOYSTICK

SNAP_ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]


class Joystick(Widget):
    """
    Smooth 360° analog joystick. input_enabled controls whether it
    responds to touch at all - set False (and opacity=0) when the
    platform is PC mode and keyboard controls take over instead.
    """

    def __init__(self, **kwargs):
        self._inner = None
        self._outer = None
        self._touch_uid = None

        self.active = False
        self.magnitude = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self.angle_deg = 90.0
        self.snapped_angle_deg = 90.0
        self.input_enabled = True

        super().__init__(size_hint=(None, None), **kwargs)

        self._outer = Image(
            source=OUTER_JOYSTICK,
            fit_mode="contain",
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._outer)
        self.bind(size=lambda *_: setattr(self._outer, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._outer, "pos", self.pos))

        nub = self.width * 0.42 if self.width > 0 else 40
        self._inner = Image(
            source=INNER_JOYSTICK,
            fit_mode="contain",
            size_hint=(None, None),
            size=(nub, nub),
        )
        self.add_widget(self._inner)

        self._center_inner()
        self.bind(pos=self._center_inner, size=self._on_size_change)

    def _on_size_change(self, *_):
        if self._inner is None:
            return
        nub = self.width * 0.42
        self._inner.size = (nub, nub)
        self._center_inner()

    def _center_inner(self, *_):
        if self._inner is None:
            return
        self._inner.center = self.center

    def on_touch_down(self, touch):
        if not self.input_enabled:
            return False
        if self._touch_uid is not None:
            return False
        if not self.collide_point(*touch.pos):
            return False
        self._touch_uid = touch.uid
        self.active = True
        self._move(touch.x, touch.y)
        return True

    def on_touch_move(self, touch):
        if not self.input_enabled:
            return False
        if touch.uid != self._touch_uid:
            return False
        self._move(touch.x, touch.y)
        return True

    def on_touch_up(self, touch):
        if not self.input_enabled:
            return False
        if touch.uid != self._touch_uid:
            return False
        self._touch_uid = None
        self.active = False
        self.magnitude = 0.0
        self.dx = 0.0
        self.dy = 0.0
        self._center_inner()
        return True

    def _move(self, tx, ty):
        cx, cy = self.center
        raw_dx = tx - cx
        raw_dy = ty - cy
        dist = math.sqrt(raw_dx * raw_dx + raw_dy * raw_dy)

        if dist == 0:
            self.magnitude = 0.0
            self.dx = 0.0
            self.dy = 0.0
            self._inner.center = (cx, cy)
            return

        max_r = (self.width - self._inner.width) / 2
        norm_dx = raw_dx / dist
        norm_dy = raw_dy / dist

        self.magnitude = min(dist / max_r, 1.0) if max_r > 0 else 0.0
        self.dx = norm_dx
        self.dy = norm_dy

        raw_angle = math.degrees(math.atan2(norm_dy, norm_dx))
        self.angle_deg = raw_angle % 360
        self.snapped_angle_deg = Joystick._snap(raw_angle)

        clamped_dist = min(dist, max_r)
        self._inner.center = (
            cx + norm_dx * clamped_dist,
            cy + norm_dy * clamped_dist,
        )

    @staticmethod
    def _snap(angle):
        angle = angle % 360
        best, best_diff = SNAP_ANGLES[0], 360
        for a in SNAP_ANGLES:
            diff = abs(angle - a)
            if diff > 180:
                diff = 360 - diff
            if diff < best_diff:
                best_diff = diff
                best = a
        return float(best)