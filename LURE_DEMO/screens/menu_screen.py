# screens/menu_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.app import App
from kivy.core.window import Window

from config import (
    BG_HOME, BTN_BACK, BTN_NEW_GAME, BTN_YES, BTN_NO,
    asset_path,
)
from widgets.icon_button import IconButton
from widgets.message_box import MessageBox
from audio_manager import audio_manager
from save_manager import save_manager


MENU_BTN_PLAY = asset_path("UI", "buttons", "play.png")
MENU_BTN_SETTINGS = asset_path("UI", "buttons", "settings.png")


class NewGameConfirmBox(MessageBox):
    def __init__(self, on_confirm, **kwargs):
        super().__init__(width_hint=0.72, height_hint=0.72, **kwargs)
        self._on_confirm_cb = on_confirm

        from kivy.uix.label import Label
        title = Label(
            text="[b]New Game[/b]",
            markup=True,
            font_size="30sp",
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1),
        )
        self.content_area.add_widget(title)

        msg = Label(
            text="Starting a new game will erase all saved progress.",
            font_size="16sp",
            color=(1, 1, 1, 1),
            halign="center",
        )
        msg.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.content_area.add_widget(msg)

        spacer = BoxLayout(size_hint_y=1)
        self.content_area.add_widget(spacer)

        button_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=90,
            spacing=24,
        )

        no_btn = IconButton(
            source=BTN_NO,
            size_hint=(0.5, 1),
            on_release_action=self._on_no,
        )
        button_row.add_widget(no_btn)

        yes_btn = IconButton(
            source=BTN_YES,
            size_hint=(0.5, 1),
            on_release_action=self._on_yes,
        )
        button_row.add_widget(yes_btn)

        self.content_area.add_widget(button_row)

    def _on_no(self):
        self.close()

    def _on_yes(self):
        self._on_confirm_cb()
        self.close()


class MenuScreen(Screen):
    LOAD_BAR_DURATION = 2.0

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

        # Back button
        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.19, 0.19),
            pos_hint={"x": 0.03, "top": 0.96},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        # Bottom gradient strip
        self.bottom_gradient = FloatLayout(
            size_hint=(1, 0.20),
            pos_hint={"x": 0, "y": 0},
        )
        with self.bottom_gradient.canvas.before:
            Color(0, 0, 0, 0.6)
            self._gradient_rect = Rectangle(
                pos=self.bottom_gradient.pos,
                size=self.bottom_gradient.size,
            )
        self.bottom_gradient.bind(
            pos=lambda inst, val: setattr(self._gradient_rect, "pos", val),
            size=lambda inst, val: setattr(self._gradient_rect, "size", val),
        )
        self.root_layout.add_widget(self.bottom_gradient)

        # Scrollable horizontal button row
        self.menu_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=3,
        )
        self.bottom_gradient.add_widget(self.menu_scroll)

        self.menu_row = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1),
            spacing=20,
            padding=(24, 8, 24, 8),
        )
        self.menu_row.bind(minimum_width=self.menu_row.setter("width"))
        self.menu_scroll.add_widget(self.menu_row)

        self._build_menu_buttons()

        # Loading bar (hidden until Play pressed)
        self.loading_bar_bg = FloatLayout(
            size_hint=(0.8, 0.04),
            pos_hint={"center_x": 0.5, "y": 0.08},
            opacity=0,
        )
        with self.loading_bar_bg.canvas.before:
            Color(1, 1, 1, 0.2)
            self._bar_bg_rect = Rectangle(
                pos=self.loading_bar_bg.pos,
                size=self.loading_bar_bg.size,
            )
        self.loading_bar_bg.bind(
            pos=lambda inst, val: setattr(self._bar_bg_rect, "pos", val),
            size=lambda inst, val: setattr(self._bar_bg_rect, "size", val),
        )
        self.root_layout.add_widget(self.loading_bar_bg)

        self.loading_bar_fill = FloatLayout(
            size_hint=(0, 0.04),
            pos_hint={"x": 0.1, "y": 0.08},
            opacity=0,
        )
        with self.loading_bar_fill.canvas.before:
            Color(1, 1, 1, 1)
            self._bar_fill_rect = Rectangle(
                pos=self.loading_bar_fill.pos,
                size=self.loading_bar_fill.size,
            )
        self.loading_bar_fill.bind(
            pos=lambda inst, val: setattr(self._bar_fill_rect, "pos", val),
            size=lambda inst, val: setattr(self._bar_fill_rect, "size", val),
        )
        self.root_layout.add_widget(self.loading_bar_fill)

    def _build_menu_buttons(self):
        gradient_h = Window.height * 0.37
        btn_size = gradient_h * 0.70

        buttons = [
            (MENU_BTN_PLAY,                              self._on_play_pressed),
            (BTN_NEW_GAME,                               self._on_new_game_pressed),
            (MENU_BTN_SETTINGS,                          self._on_settings_pressed),
            (asset_path("UI", "buttons", "credits.png"), self._on_credits_pressed),
        ]

        num_buttons = len(buttons)
        min_spacing = 20
        side_padding = 24

        # Spread buttons across the full screen width: total row width
        # should equal Window.width, so Play sits near the left edge and
        # Credits near the right edge, with the middle two evenly spaced.
        available = Window.width - (side_padding * 2) - (btn_size * num_buttons)
        gaps = num_buttons - 1
        spacing = max(min_spacing, available / gaps) if gaps > 0 else min_spacing

        self.menu_row.spacing = spacing
        self.menu_row.padding = (side_padding, 8, side_padding, 8)

        for source, action in buttons:
            btn = IconButton(
                source=source,
                size_hint=(None, None),
                size=(btn_size, btn_size),
                pos_hint={"center_y": 0.5},
                on_release_action=action,
            )
            self.menu_row.add_widget(btn)

    def _on_back_pressed(self):
        App.get_running_app().navigate_to("home")

    def _on_settings_pressed(self):
        App.get_running_app().navigate_to("settings")

    def _on_credits_pressed(self):
        App.get_running_app().navigate_to("credits")

    def _on_new_game_pressed(self):
        box = NewGameConfirmBox(on_confirm=self._start_new_game)
        box.open_on(self.root_layout)

    def _start_new_game(self):
        save_manager.reset()

    def _on_play_pressed(self):
        self.bottom_gradient.opacity = 0
        self.bottom_gradient.disabled = True
        self.back_btn.opacity = 0
        self.back_btn.disabled = True

        self.loading_bar_bg.opacity = 1
        self.loading_bar_fill.opacity = 1
        self.loading_bar_fill.size_hint_x = 0

        anim = Animation(size_hint_x=0.8, duration=self.LOAD_BAR_DURATION)
        anim.bind(on_complete=self._on_loading_complete)
        anim.start(self.loading_bar_fill)

    def _on_loading_complete(self, *args):
        audio_manager.pause_for_gameplay()
        App.get_running_app().navigate_to("gameplay")

    def on_pre_enter(self, *args):
        self.bottom_gradient.opacity = 1
        self.bottom_gradient.disabled = False
        self.back_btn.opacity = 1
        self.back_btn.disabled = False
        self.loading_bar_bg.opacity = 0
        self.loading_bar_fill.opacity = 0
        self.loading_bar_fill.size_hint_x = 0