# widgets/message_box.py

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.properties import BooleanProperty
from kivy.animation import Animation

from config import MESSAGE_BOX


_open_boxes = []


class DragHandle(Widget):
    """
    The 2x2 white dot drag handle at the bottom center of a MessageBox.
    """

    highlighted = BooleanProperty(False)

    def __init__(self, target_box, **kwargs):
        super().__init__(**kwargs)
        self.target_box = target_box
        self.size_hint = (None, None)
        self.size = (56, 38)
        self._dragging = False
        self._touch_offset = (0, 0)

        with self.canvas:
            self._dot_color = Color(1, 1, 1, 1)
            self._dots = []
            self._build_dots()

        self.bind(pos=self._update_dots, size=self._update_dots)

    def _build_dots(self):
        dot_r = 5
        for row in range(2):
            for col in range(2):
                self._dots.append(Ellipse(size=(dot_r * 2, dot_r * 2)))
        self._update_dots()

    def _update_dots(self, *args):
        dot_r = 5
        spacing_x = 22
        spacing_y = 16
        cx, cy = self.center
        positions = [
            (cx - spacing_x / 2, cy + spacing_y / 2),
            (cx + spacing_x / 2, cy + spacing_y / 2),
            (cx - spacing_x / 2, cy - spacing_y / 2),
            (cx + spacing_x / 2, cy - spacing_y / 2),
        ]
        for dot, (dx, dy) in zip(self._dots, positions):
            dot.pos = (dx - dot_r, dy - dot_r)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self._dragging = True
            self.highlighted = True
            self._dot_color.rgba = (1, 0.85, 0.4, 1)
            touch.grab(self)
            self._touch_offset = (
                touch.x - self.target_box.x,
                touch.y - self.target_box.y,
            )
            self.target_box.bring_to_front()
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self and self._dragging:
            new_x = touch.x - self._touch_offset[0]
            new_y = touch.y - self._touch_offset[1]
            self.target_box.pos = (new_x, new_y)
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._dragging = False
            self.highlighted = False
            self._dot_color.rgba = (1, 1, 1, 1)
            return True
        return super().on_touch_up(touch)


class MessageBox(FloatLayout):
    """
    Desktop-window-style message box.
    Content area is now inset further from the box art's edges/corners
    so text never clips the beveled border, and is more evenly
    balanced vertically within the box.
    """
    CONTENT_POS_HINT = {"center_x": 0.5, "top": 0.86}
    def __init__(self, width_hint=0.78, height_hint=0.75, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)

        self._bg = Image(
            source=MESSAGE_BOX,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        self.add_widget(self._bg)

        self.content_area = BoxLayout(
            orientation="vertical",
            size_hint=(0.82, 0.68),
            
            pos_hint=dict(self.CONTENT_POS_HINT),
            spacing=12,
            padding=16,
        )
        self.add_widget(self.content_area)

        self.drag_handle = DragHandle(target_box=self)
        self.drag_handle.pos_hint = {"center_x": 0.5, "y": 0.04}
        self.add_widget(self.drag_handle)

        self._width_hint = width_hint
        self._height_hint = height_hint

    def open_on(self, parent_widget, center=True):
        pw, ph = parent_widget.size
        self.size = (pw * self._width_hint, ph * self._height_hint)

        self.pos = (
            parent_widget.x + (pw - self.width) / 2,
            parent_widget.y + (ph - self.height) / 2,
        )

        parent_widget.add_widget(self)
        _open_boxes.append(self)

        self.opacity = 0
        anim = Animation(opacity=1, duration=0.15)
        anim.start(self)

    def close(self):
        if self in _open_boxes:
            _open_boxes.remove(self)
        if self.parent:
            self.parent.remove_widget(self)

    def bring_to_front(self):
        if self.parent is None:
            return
        parent = self.parent
        parent.remove_widget(self)
        parent.add_widget(self)
        if self in _open_boxes:
            _open_boxes.remove(self)
            _open_boxes.append(self)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.bring_to_front()
        return super().on_touch_down(touch)


def close_all_message_boxes():
    for box in list(_open_boxes):
        box.close()


def any_message_box_open():
    return len(_open_boxes) > 0


def is_touch_on_any_message_box(touch):
    for box in _open_boxes:
        if box.collide_point(*touch.pos):
            return True
    return False