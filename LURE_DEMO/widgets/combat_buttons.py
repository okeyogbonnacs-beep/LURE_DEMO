# widgets/combat_buttons.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.clock import Clock

from config import BTN_SHOOT, BTN_BOMB, BUTTON_PRESS_SCALE, BUTTON_PRESS_DARKEN


class ShootButton(Widget):
    """
    Pure input widget for the shoot button. input_enabled controls
    whether it responds to touch - set False when PC mode/keyboard
    controls take over instead.
    """

    def __init__(self, on_press_callback=None, on_release_callback=None, **kwargs):
        self._touch_uid = None
        self.is_held = False
        self.input_enabled = True

        self.on_press_callback = on_press_callback
        self.on_release_callback = on_release_callback

        super().__init__(size_hint=(None, None), **kwargs)

        self._img = Image(
            source=BTN_SHOOT,
            fit_mode="contain",
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))

    def on_touch_down(self, touch):
        if not self.input_enabled:
            return False
        if self._touch_uid is not None:
            return False
        if not self.collide_point(*touch.pos):
            return False
        self._touch_uid = touch.uid
        self.is_held = True
        self._img.size = (self.width * BUTTON_PRESS_SCALE, self.height * BUTTON_PRESS_SCALE)
        self._img.color = (BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, 1)
        if self.on_press_callback:
            self.on_press_callback(touch)
        return True

    def on_touch_up(self, touch):
        if not self.input_enabled:
            return False
        if touch.uid != self._touch_uid:
            return False
        self._touch_uid = None
        self.is_held = False
        self._img.size = self.size
        self._img.color = (1, 1, 1, 1)
        if self.on_release_callback:
            self.on_release_callback(touch)
        return True


class BombButton(Widget):
    """
    Pure input widget for the bomb button with cooldown tracking.
    input_enabled controls whether it responds to touch.
    """

    def __init__(self, on_press_callback=None, **kwargs):
        self._touch_uid = None
        self.is_ready = True
        self.input_enabled = True
        self._cooldown_event = None

        self.on_press_callback = on_press_callback

        super().__init__(size_hint=(None, None), **kwargs)

        self._img = Image(
            source=BTN_BOMB,
            fit_mode="contain",
            size_hint=(None, None),
            size=self.size,
            pos=self.pos,
        )
        self.add_widget(self._img)
        self.bind(size=lambda *_: setattr(self._img, "size", self.size))
        self.bind(pos=lambda *_: setattr(self._img, "pos", self.pos))

    def start_cooldown(self, seconds):
        self.is_ready = False
        self._img.color = (BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, 1)

        if self._cooldown_event is not None:
            self._cooldown_event.cancel()
        self._cooldown_event = Clock.schedule_once(self._on_cooldown_done, seconds)

    def _on_cooldown_done(self, *_):
        self.is_ready = True
        self._img.color = (1, 1, 1, 1)
        self._cooldown_event = None

    def on_touch_down(self, touch):
        if not self.input_enabled:
            return False
        if self._touch_uid is not None:
            return False
        if not self.collide_point(*touch.pos):
            return False
        if not self.is_ready:
            return True

        self._touch_uid = touch.uid
        self._img.size = (self.width * BUTTON_PRESS_SCALE, self.height * BUTTON_PRESS_SCALE)
        if self.on_press_callback:
            self.on_press_callback()
        return True

    def on_touch_up(self, touch):
        if not self.input_enabled:
            return False
        if touch.uid != self._touch_uid:
            return False
        self._touch_uid = None
        self._img.size = self.size
        return True