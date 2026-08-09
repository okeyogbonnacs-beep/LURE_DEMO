# screens/home_screen.py

import random

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock

from config import (
    BG_HOME,
    BTN_PLAY,
    BTN_STORE,
    BTN_SUPPORT,
    BTN_SETTINGS,
    BTN_TASKS,
    BTN_DAILY_REWARD,
    ICON_SHUFFLE_INTERVAL,
    TOP_RIGHT_ICON_SIZE_HINT,
    TOP_RIGHT_ICON_POS_HINT,
)
from widgets.icon_button import IconButton
from widgets.song_toast import song_toast
from widgets.message_box import close_all_message_boxes, is_touch_on_any_message_box, any_message_box_open
from audio_manager import audio_manager
from screens.quick_menu import QuickMenu


class HomeScreen(Screen):
    """
    Home Screen.

    - Background: home_screenbg.png
    - Bottom-center: Play (press effect only, no nav yet)
    - Bottom-left: Store (press effect only, no nav yet)
    - Bottom-right: Support (press effect only, no nav yet)
    - Top-right: single icon that auto-cycles between
      settings_btn.png / tasks.png / daily_reward.png every 2s,
      pausing (visually) while the Quick Menu is open.
    - Tapping the icon reveals the other 2 icons in a row to its left.
    - Music starts + Song Toast fires on first entry, and every
      time a new song begins afterward.
    """

    ICON_CYCLE = [BTN_SETTINGS, BTN_TASKS, BTN_DAILY_REWARD]
    ICON_KEYS = ["settings", "tasks", "daily_reward"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self._bg = Image(
            source=BG_HOME,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self._bg)

        # ---------------- Bottom buttons ----------------

        self.play_btn = IconButton(
            source=BTN_PLAY,
            size_hint=(0.30, 0.30),
            pos_hint={"center_x": 0.5, "y": 0.04},
            on_release_action=self._on_play_pressed,
        )
        self.root_layout.add_widget(self.play_btn)

        self.store_btn = IconButton(
            source=BTN_STORE,
            size_hint=(0.22, 0.22),
            pos_hint={"x": 0.03, "y": 0.04},
            on_release_action=self._on_store_pressed,
        )
        self.root_layout.add_widget(self.store_btn)

        self.support_btn = IconButton(
            source=BTN_SUPPORT,
            size_hint=(0.22, 0.22),
            pos_hint={"right": 0.97, "y": 0.04},
            on_release_action=self._on_support_pressed,
        )
        self.root_layout.add_widget(self.support_btn)

        # ---------------- Top-right shuffling icon ----------------

        self._icon_index = random.randint(0, len(self.ICON_CYCLE) - 1)
        self.quick_menu_icon = IconButton(
            source=self.ICON_CYCLE[self._icon_index],
            size_hint=TOP_RIGHT_ICON_SIZE_HINT,
            pos_hint=TOP_RIGHT_ICON_POS_HINT,
            on_release_action=self._on_quick_menu_icon_pressed,
        )
        self.root_layout.add_widget(self.quick_menu_icon)
        

        self._shuffle_event = None

        # ---------------- Quick Menu (reveals other 2 icons) ----------------

        self.quick_menu = QuickMenu(
            on_settings=self._on_settings_pressed,
            on_tasks=self._on_tasks_pressed,
            on_daily_reward=self._on_daily_reward_pressed,
            anchor_widget=self.quick_menu_icon,
        )
        self.root_layout.add_widget(self.quick_menu)

        self._music_started = False

    # --------------------------------------------------------
    # SCREEN LIFECYCLE
    # --------------------------------------------------------

    def on_enter(self, *args):
        if not self._music_started:
            audio_manager.bind(on_new_song=self._on_new_song)
            audio_manager.start_music()
            self._music_started = True

        self._start_icon_shuffle()

    def on_leave(self, *args):
        self._stop_icon_shuffle()

    def _on_new_song(self, instance, song_name):
        song_toast.show(song_name)

    # --------------------------------------------------------
    # TOP-RIGHT ICON SHUFFLE
    # --------------------------------------------------------

    def _start_icon_shuffle(self):
        self._stop_icon_shuffle()
        self._shuffle_event = Clock.schedule_interval(
            self._shuffle_icon, ICON_SHUFFLE_INTERVAL
        )

    def _stop_icon_shuffle(self):
        if self._shuffle_event:
            self._shuffle_event.cancel()
            self._shuffle_event = None

    def _shuffle_icon(self, dt):
        if self.quick_menu.is_open:
            return  # frozen on current icon while panel is open
        self._icon_index = (self._icon_index + 1) % len(self.ICON_CYCLE)
        self.quick_menu_icon.source = self.ICON_CYCLE[self._icon_index]

    # --------------------------------------------------------
    # QUICK MENU ICON PRESS
    # --------------------------------------------------------

    def _on_quick_menu_icon_pressed(self):
        active_key = self.ICON_KEYS[self._icon_index]
        self.quick_menu.toggle(active_icon_key=active_key)

    # --------------------------------------------------------
    # BOTTOM BUTTON ACTIONS (press effect only for now)
    # --------------------------------------------------------
    def _on_play_pressed(self):
        from kivy.app import App
        App.get_running_app().navigate_to("menu")
    
    def _on_store_pressed(self):
        from kivy.app import App
        App.get_running_app().navigate_to("hangar")
    
    def _on_support_pressed(self):
        from kivy.app import App
        App.get_running_app().navigate_to("support")
    

    # --------------------------------------------------------
    # QUICK MENU ACTIONS
    # --------------------------------------------------------
    def _on_settings_pressed(self):
        self.quick_menu.close()
        from kivy.app import App
        App.get_running_app().navigate_to("settings")

    def _on_tasks_pressed(self):
        self.quick_menu.close()
        from screens.tasks_window import TasksWindow
        box = TasksWindow()
        box.open_on(self.root_layout)

    def _on_daily_reward_pressed(self):
        self.quick_menu.close()
        from screens.daily_reward_window import DailyRewardWindow
        box = DailyRewardWindow()
        box.open_on(self.root_layout)

    # --------------------------------------------------------
    # TAP EMPTY SPACE CLOSES QUICK MENU + MESSAGE BOXES
    # --------------------------------------------------------

    def on_touch_down(self, touch):
        if self.quick_menu.is_open and not self.quick_menu.collide_point(*touch.pos):
            self.quick_menu.close()

        if any_message_box_open() and not is_touch_on_any_message_box(touch):
            if not self.quick_menu.collide_point(*touch.pos):
                close_all_message_boxes()

        return super().on_touch_down(touch)