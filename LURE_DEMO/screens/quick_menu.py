# screens/quick_menu.py

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation

from config import BTN_SETTINGS, BTN_TASKS, BTN_DAILY_REWARD, TOP_RIGHT_ICON_SIZE_HINT
from widgets.icon_button import IconButton


class QuickMenu(FloatLayout):
    """
    Reveals the two non-active icons (Settings/Tasks/Daily Reward,
    minus whichever is currently showing) in a horizontal row to the
    LEFT of the shuffling icon that opened it.

    No panel/background graphic - just the buttons themselves,
    fading/sliding in.
    """

    BUTTON_SIZE_HINT = TOP_RIGHT_ICON_SIZE_HINT
    SPACING = 10
    ANIM_DURATION = 0.22

    ALL_ICONS = {
        "settings": BTN_SETTINGS,
        "tasks": BTN_TASKS,
        "daily_reward": BTN_DAILY_REWARD,
    }

    def __init__(self, on_settings=None, on_tasks=None, on_daily_reward=None,
                 anchor_widget=None, **kwargs):
        super().__init__(**kwargs)

        self._on_settings_cb = on_settings
        self._on_tasks_cb = on_tasks
        self._on_daily_reward_cb = on_daily_reward
        self.anchor_widget = anchor_widget

        self.is_open = False
        self.size_hint = (0.16, 0.16)
        self.size = (0, 0)

        self._row = BoxLayout(
            orientation="horizontal",
            spacing=self.SPACING,
            size_hint=(0.16, 0.16),
        )
        self.add_widget(self._row)

    # --------------------------------------------------------
    # BUILD BUTTONS BASED ON WHICH ICON IS CURRENTLY ACTIVE
    # --------------------------------------------------------

    def _rebuild_buttons(self, active_icon_key):
        self._row.clear_widgets()

        for key, source in self.ALL_ICONS.items():
            if key == active_icon_key:
                continue  # already visible as the button that opened this

            if key == "settings":
                action = self._settings_pressed
            elif key == "tasks":
                action = self._tasks_pressed
            else:
                action = self._daily_reward_pressed

            btn = IconButton(
                source=source,
                size_hint=(None, None),
                on_release_action=action,
            )
            self._row.add_widget(btn)

    def _position_near_anchor(self):
        """
        Position this whole row so its RIGHT edge sits just to the LEFT
        of the anchor icon, vertically centered with it.
        """
        if not self.anchor_widget:
            return

        # compute button pixel size from hint, relative to window
        from kivy.core.window import Window
        btn_w = Window.width * self.BUTTON_SIZE_HINT[0]
        btn_h = Window.height * self.BUTTON_SIZE_HINT[1]

        for child in self._row.children:
            child.size = (btn_w, btn_h)

        num_buttons = len(self._row.children)
        total_width = (btn_w * num_buttons) + (self.SPACING * max(0, num_buttons - 1))
        self._row.size = (total_width, btn_h)
        self.size = (total_width, btn_h)

        gap = 16
        anchor_x, anchor_y = self.anchor_widget.pos
        anchor_center_y = anchor_y + self.anchor_widget.height / 2

        self.pos = (
            anchor_x - gap - total_width,
            anchor_center_y - (btn_h / 2),
        )
        self._row.pos = self.pos

    # --------------------------------------------------------
    # OPEN / CLOSE / TOGGLE
    # --------------------------------------------------------

    def toggle(self, active_icon_key=None):
        if self.is_open:
            self.close()
        else:
            self.open(active_icon_key)

    def open(self, active_icon_key):
        if self.is_open:
            return

        self._rebuild_buttons(active_icon_key)
        self._position_near_anchor()

        self.is_open = True
        self.opacity = 0

        Animation.cancel_all(self)
        anim = Animation(opacity=1, duration=self.ANIM_DURATION)
        anim.start(self)

    def close(self):
        if not self.is_open:
            return
        self.is_open = False

        Animation.cancel_all(self)
        anim = Animation(opacity=0, duration=self.ANIM_DURATION)
        anim.bind(on_complete=self._on_close_complete)
        anim.start(self)

    def _on_close_complete(self, *args):
        self._row.clear_widgets()

    def collide_point(self, x, y):
        # so home_screen's "tap empty space closes everything" check
        # correctly treats this row's buttons as "not empty space"
        if not self.is_open:
            return False
        return super().collide_point(x, y)

    # --------------------------------------------------------
    # BUTTON ACTIONS
    # --------------------------------------------------------

    def _settings_pressed(self):
        if self._on_settings_cb:
            self._on_settings_cb()

    def _tasks_pressed(self):
        if self._on_tasks_cb:
            self._on_tasks_cb()

    def _daily_reward_pressed(self):
        if self._on_daily_reward_cb:
            self._on_daily_reward_cb()