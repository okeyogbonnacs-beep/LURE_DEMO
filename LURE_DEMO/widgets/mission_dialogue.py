# widgets/mission_dialogue.py

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.clock import Clock

from config import MESSAGE_BOX, DIALOGUE_FACE

SPEAKER_NAME = "Commander Rix"


class MissionDialogue(Widget):
    """
    Reusable modal mission dialogue.

    Box and face positions/sizes come from layout_data.json
    ("Gameplay" section) as proportional hints of the window.
    Name + text reflow to fill the remaining space inside the box,
    to the right of the face.

    - Tap anywhere to skip typing / close once fully typed.
    """

    BOX_HINT = {
        "size": (0.8843, 0.5377),
        "pos": (0.0861, 0.0123),
    }
    FACE_HINT = {
        "size": (0.2122, 0.3307),
        "pos": (0.105, 0.126),
    }

    PADDING = 15
    NAME_HEIGHT = 32
    TYPE_INTERVAL = 0.02  # seconds per character

    def __init__(self, text, on_close_callback=None, **kwargs):
        super().__init__(size=(Window.width, Window.height), pos=(0, 0), **kwargs)

        self.on_close_callback = on_close_callback
        self._full_text = text
        self._char_index = 0
        self._type_event = None

        W, H = Window.width, Window.height

        box_w = W * self.BOX_HINT["size"][0]
        box_h = H * self.BOX_HINT["size"][1]
        box_x = W * self.BOX_HINT["pos"][0]
        box_y = H * self.BOX_HINT["pos"][1]

        self._box = Image(
            source=MESSAGE_BOX,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(None, None),
            size=(box_w, box_h),
            pos=(box_x, box_y),
        )
        self.add_widget(self._box)

        face_w = W * self.FACE_HINT["size"][0]
        face_h = H * self.FACE_HINT["size"][1]
        face_x = W * self.FACE_HINT["pos"][0]
        face_y = H * self.FACE_HINT["pos"][1]

        self._face = Image(
            source=DIALOGUE_FACE,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            size=(face_w, face_h),
            pos=(face_x, face_y),
        )
        self.add_widget(self._face)

        pad = self.PADDING

        # Name + text block: fills remaining space inside the box,
        # to the right of the face
        text_x = face_x + face_w + pad
        text_w = (box_x + box_w) - pad - text_x

        name_y = box_y + box_h - pad - self.NAME_HEIGHT
        self._name_lbl = Label(
            text=f"[b]{SPEAKER_NAME}[/b]",
            markup=True,
            font_size="18sp",
            color=(1, 0.8, 0.3, 1),
            size_hint=(None, None),
            size=(text_w, self.NAME_HEIGHT),
            pos=(text_x, name_y),
            halign="left",
            valign="middle",
        )
        self._name_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.add_widget(self._name_lbl)

        text_h = name_y - pad - (box_y + pad)
        self._label = Label(
            text="",
            font_size="16sp",
            size_hint=(None, None),
            size=(text_w, text_h),
            pos=(text_x, box_y + pad),
            text_size=(text_w, text_h),
            halign="left",
            valign="top",
            color=(1, 1, 1, 1),
        )
        self.add_widget(self._label)

        self._start_typewriter()

    def _start_typewriter(self):
        self._char_index = 0
        self._type_event = Clock.schedule_interval(self._type_next_char, self.TYPE_INTERVAL)

    def _type_next_char(self, dt):
        if self._char_index >= len(self._full_text):
            self._type_event.cancel()
            self._type_event = None
            return
        self._char_index += 1
        self._label.text = self._full_text[: self._char_index]

    def _finish_typing_instantly(self):
        self._char_index = len(self._full_text)
        self._label.text = self._full_text
        if self._type_event is not None:
            self._type_event.cancel()
            self._type_event = None

    def on_touch_down(self, touch):
        if self._type_event is not None:
            self._finish_typing_instantly()
        else:
            self._close()
        return True

    def _close(self):
        if self._type_event is not None:
            self._type_event.cancel()
            self._type_event = None
        if self.parent:
            self.parent.remove_widget(self)
        if self.on_close_callback:
            self.on_close_callback()