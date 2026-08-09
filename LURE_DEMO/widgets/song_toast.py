# widgets/song_toast.py

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window

from config import MESSAGE_BOX, SONG_TOAST_SLIDE_TIME

SONG_TOAST_DURATION = 5.0


class SongToast(FloatLayout):
    """
    Toast notification shown every time a new song starts.

    - Uses the message_box.png art as its own background.
    - Sized at 20% of the smaller window dimension (width > height,
      fixed aspect ratio) - manually computed in _compute_size()
      rather than via Kivy's size_hint, since this widget attaches
      directly to Window rather than a parent layout.
    - Background rendered at 50% opacity; text stays fully readable.
    - Slides IN from the right edge, stays 3 seconds, slides back OUT right.
    - Shows just the song name, no "Now Playing:" prefix.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)  # manual sizing via _compute_size()
        self.opacity = 9

        self._bg = Image(
            source=MESSAGE_BOX,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1.9, 1.1),
            pos_hint={"x": -1, "y": 0},
        )
        self._bg.opacity = 0.5
        self.add_widget(self._bg)

        self._label = Label(
            text="",
            size_hint=(1.9, 0.5),
            pos_hint={"center_x": 0, "center_y": 0.6},
            font_size="16sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
        )
        self._label.bind(size=self._update_text_size)
        self.add_widget(self._label)

        self._on_screen_x = None
        self._off_screen_x = None
        self._fixed_y = None
        self._hide_event = None

    def _update_text_size(self, instance, value):
        instance.text_size = value

    def _compute_size(self):
        # 20% of the smaller window dimension, width clearly > height
        base = min(Window.width, Window.height) * 0.20
        width = base * 2.4
        height = base
        return (width, height)

    def show(self, song_name):
        if self._hide_event:
            self._hide_event.cancel()
            self._hide_event = None
        Animation.cancel_all(self)

        self.size = self._compute_size()

        margin = 16
        self._fixed_y = Window.height - self.height - margin
        self._on_screen_x = Window.width - self.width - margin
        self._off_screen_x = Window.width + 10

        self._label.text = song_name

        self.pos = (self._off_screen_x, self._fixed_y)
        self.opacity = 1

        if not self.parent:
            Window.add_widget(self)
        else:
            Window.remove_widget(self)
            Window.add_widget(self)

        slide_in = Animation(
            x=self._on_screen_x,
            duration=SONG_TOAST_SLIDE_TIME,
            t="out_cubic",
        )
        slide_in.start(self)

        self._hide_event = Clock.schedule_once(
            self._slide_out, SONG_TOAST_SLIDE_TIME + SONG_TOAST_DURATION
        )

    def _slide_out(self, dt):
        slide_out = Animation(
            x=self._off_screen_x,
            duration=SONG_TOAST_SLIDE_TIME,
            t="in_cubic",
        )
        slide_out.bind(on_complete=self._remove_self)
        slide_out.start(self)

    def _remove_self(self, *args):
        if self.parent:
            self.parent.remove_widget(self)


song_toast = SongToast()