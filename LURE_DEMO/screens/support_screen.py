# screens/support_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.app import App
import webbrowser

from config import BG_SUPPORT, BTN_BACK
from widgets.icon_button import IconButton
from audio_manager import audio_manager


# TODO: replace with the real itch.io support/game page URL
ITCH_IO_SUPPORT_URL = "https://001-productions.itch.io/lure-retro-futuristic-space-game-kit"


INITIAL_SUPPORT_TEXT = (
    "    "
    "    "
    "LURE is being built by a small, independent team chasing a big idea: "
    "a tactical space combat game that feels as good in your hands as it "
    "looks on screen. Every ship, every system, every explosion you see in "
    "this demo was made by people working nights and weekends to bring it "
    "to life.\n\n"
    "If you've enjoyed what you've played so far, supporting the project "
    "helps us keep building - covering tools, assets, and the time it takes "
    "to polish a game the right way. Even small support goes a long way "
    "for a team this size, and every bit of it is genuinely appreciated."
)


SUPPORT_IDEAS = [
    "Buy our asset packs - get quality game-ready assets while helping fund development.",
    "Support development directly through a donation, big or small.",
    "Help us purchase a dedicated development laptop to speed up production.",
    "Share LURE with friends, communities, or anyone who loves space games.",
    "Give feedback - your thoughts directly shape what we build next.",
]


class UnderlinedLink(ButtonBehavior, Label):
    """
    A simple underlined, clickable text link (not using the global
    IconButton press effect since this is text, not an image button).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.color = (0.6, 0.85, 1, 1)


class SupportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self._bg = Image(
            source=BG_SUPPORT,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self._bg)

        # ---------------- Back button ----------------
        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.2222, 0.1147),
            pos_hint={"x": 0.03, "top": 0.96},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        # ---------------- Main text content area ----------------
        self.content_container = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.55),
            pos_hint={"center_x": 0.5, "center_y": 0.50},
            spacing=10,
        )
        self.root_layout.add_widget(self.content_container)

        self._scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._text_label = Label(
            text=INITIAL_SUPPORT_TEXT,
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            halign="center",
            valign="top",
        )
        self._text_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None))
        )
        self._text_label.bind(
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1])
        )
        self._scroll.add_widget(self._text_label)
        self.content_container.add_widget(self._scroll)

        # ---------------- Bottom links area ----------------
        self.links_container = BoxLayout(
            orientation="vertical",
            size_hint=(0.8, 0.14),
            pos_hint={"center_x": 0.5, "y": 0.05},
            spacing=6,
        )
        self.root_layout.add_widget(self.links_container)

        self.support_link = UnderlinedLink(
            text="[u]Support[/u]",
            font_size="20sp",
            size_hint_y=None,
            height=32,
            halign="center",
        )
        self.support_link.bind(on_release=self._on_support_link_pressed)
        self.links_container.add_widget(self.support_link)

        self.not_sure_link = UnderlinedLink(
            text="[u]Not sure how to support?[/u]",
            font_size="14sp",
            size_hint_y=None,
            height=24,
            halign="center",
            color=(0.75, 0.75, 0.75, 1),
        )
        self.not_sure_link.bind(on_release=self._on_not_sure_pressed)
        self.links_container.add_widget(self.not_sure_link)

        self._showing_ideas = False

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def _on_back_pressed(self):
        app = App.get_running_app()
        app.navigate_to("home")

    # --------------------------------------------------------
    # SUPPORT LINK / IDEAS SWAP
    # --------------------------------------------------------

    def _on_support_link_pressed(self, instance):
        webbrowser.open(ITCH_IO_SUPPORT_URL)

    def _on_not_sure_pressed(self, instance):
        if self._showing_ideas:
            return
        self._showing_ideas = True
        self._show_ideas_list()

    def _show_ideas_list(self):
        self._scroll.clear_widgets()

        ideas_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=14, padding=(0, 6))
        ideas_box.bind(minimum_height=ideas_box.setter("height"))

        for idea_text in SUPPORT_IDEAS:
            row = BoxLayout(orientation="vertical", size_hint_y=None, spacing=4)

            idea_label = Label(
                text=idea_text,
                font_size="15sp",
                color=(1, 1, 1, 1),
                size_hint_y=None,
                halign="center",
                valign="top",
            )
            idea_label.bind(
                width=lambda inst, w: setattr(inst, "text_size", (w, None))
            )
            idea_label.bind(
                texture_size=lambda inst, ts: setattr(inst, "height", ts[1])
            )
            row.add_widget(idea_label)

            idea_link = UnderlinedLink(
                text="[u]Support[/u]",
                font_size="15sp",
                size_hint_y=None,
                height=26,
                halign="center",
            )
            idea_link.bind(on_release=self._on_support_link_pressed)
            row.add_widget(idea_link)

            row.height = 90
            ideas_box.add_widget(row)

        self._scroll.add_widget(ideas_box)

    # --------------------------------------------------------
    # RESET ON RE-ENTRY (optional: always start fresh)
    # --------------------------------------------------------

    def on_pre_enter(self, *args):
        self._reset_to_initial_text()

    def _reset_to_initial_text(self):
        self._showing_ideas = False
        self._scroll.clear_widgets()
        self._text_label = Label(
            text=INITIAL_SUPPORT_TEXT,
            font_size="16sp",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            halign="center",
            valign="top",
        )
        self._text_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None))
        )
        self._text_label.bind(
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1])
        )
        self._scroll.add_widget(self._text_label)