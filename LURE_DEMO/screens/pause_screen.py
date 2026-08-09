# screens/pause_screen.py

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

from config import BG_PAUSE, BTN_RESUME, BTN_HOME_ICON
from widgets.icon_button import IconButton


class PauseOverlay(FloatLayout):
    """
    Shown over gameplay when paused. Not a Screen/nav destination -
    gameplay must stay mounted underneath so Resume can return to it
    exactly where it left off. Resume closes this overlay; Home exits
    gameplay entirely back to the Home screen.
    """

    def __init__(self, on_resume, on_home, **kwargs):
        super().__init__(size_hint=(1, 1), pos_hint={"x": 0, "y": 0}, **kwargs)

        bg = Image(
            source=BG_PAUSE, allow_stretch=True, keep_ratio=False,
            size_hint=(1, 1),
        )
        self.add_widget(bg)

        resume_btn = IconButton(
            source=BTN_RESUME,
            size_hint=(0.4, 0.16),
            pos_hint={"center_x": 0.5, "top": 0.62},
            on_release_action=on_resume,
        )
        self.add_widget(resume_btn)

        home_btn = IconButton(
            source=BTN_HOME_ICON,
            size_hint=(0.4, 0.16),
            pos_hint={"center_x": 0.5, "top": 0.42},
            on_release_action=on_home,
        )
        self.add_widget(home_btn)