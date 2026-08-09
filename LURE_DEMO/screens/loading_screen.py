# screens/loading_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.app import App

from config import BG_LOADING, LOADING_SCREEN_DURATION


class LoadingScreen(Screen):
    """
    First screen shown on app start.

    Countdown no longer starts automatically on_enter (that fired
    before other screens even existed, causing a race). Instead,
    LureApp calls start_countdown() once every other screen has
    finished building, so this screen has genuinely been visible for
    its full duration before advancing to Home.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._bg = Image(
            source=BG_LOADING,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.add_widget(self._bg)

        self._advance_event = None
        self._countdown_started = False

    def start_countdown(self):
        if self._countdown_started:
            return
        self._countdown_started = True
        self._advance_event = Clock.schedule_once(self._go_to_home, LOADING_SCREEN_DURATION)

    def on_leave(self, *args):
        if self._advance_event:
            self._advance_event.cancel()
            self._advance_event = None

    def _go_to_home(self, dt):
        app_instance = App.get_running_app()
        if hasattr(app_instance, "navigate_to"):
            app_instance.navigate_to("home", push_to_stack=False)
        else:
            self.manager.current = "home"