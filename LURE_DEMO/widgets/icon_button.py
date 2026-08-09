# widgets/icon_button.py

from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.animation import Animation
from kivy.properties import ObjectProperty

from config import BUTTON_PRESS_SCALE, BUTTON_PRESS_DARKEN
from audio_manager import audio_manager


class IconButton(ButtonBehavior, Image):
    """
    Global button used everywhere in the app.

    Behaviour (per spec):
      - On press: scale down slightly, darken slightly, play button sound.
      - On release: return to normal, THEN execute assigned action.
      - Action never fires while still held down.
      - If finger/mouse drags off the button before releasing, the
        press is cancelled (no action fires), matching standard button UX.

    Usage:
        btn = IconButton(source=asset_path("UI","buttons","play_btn.png"),
                          on_release_action=my_callback)
    """

    on_release_action = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        # pull out our custom kwarg before passing to super
        self._release_action = kwargs.pop("on_release_action", None)

        super().__init__(**kwargs)

        self.allow_stretch = True
        self.keep_ratio = True

        self._normal_scale = 1.0
        self._pressed = False

        # anchor for scale animation - use a BoxLayout-free approach via
        # size/pos manipulation through a bound scale transform
        self._base_size = None

    # --------------------------------------------------------
    # PRESS
    # --------------------------------------------------------

    def on_press(self):
        if self.disabled:
            return
        self._pressed = True
        audio_manager.play_button_sfx()
        self._animate_press()

    def _animate_press(self):
        Animation.cancel_all(self, "color", "size")

        if self._base_size is None:
            self._base_size = tuple(self.size)

        target_w = self._base_size[0] * BUTTON_PRESS_SCALE
        target_h = self._base_size[1] * BUTTON_PRESS_SCALE

        anim = Animation(
            size=(target_w, target_h),
            color=(BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, BUTTON_PRESS_DARKEN, 1),
            duration=0.08,
        )
        anim.start(self)

    # --------------------------------------------------------
    # RELEASE
    # --------------------------------------------------------

    def on_release(self):
        if self.disabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._animate_release(fire_action=was_pressed)

    def _animate_release(self, fire_action):
        Animation.cancel_all(self, "color", "size")

        if self._base_size is None:
            self._base_size = tuple(self.size)

        anim = Animation(
            size=self._base_size,
            color=(1, 1, 1, 1),
            duration=0.08,
        )

        if fire_action:
            anim.bind(on_complete=lambda *a: self._fire_action())

        anim.start(self)

    def _fire_action(self):
        if self._release_action:
            self._release_action()

    # --------------------------------------------------------
    # CANCEL ON DRAG-OFF (standard button behaviour)
    # --------------------------------------------------------

    def on_touch_move(self, touch):
        if self._pressed and not self.collide_point(*touch.pos):
            # finger dragged off the button - cancel press, no action fires
            self._pressed = False
            self._animate_release(fire_action=False)
        return super().on_touch_move(touch)