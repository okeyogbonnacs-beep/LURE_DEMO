# main.py

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock

from config import FADE_TRANSITION_DURATION
from screens.loading_screen import LoadingScreen


class LureManager(ScreenManager):
    pass


class LureApp(App):
    """
    Main application entry point.

    Only the LoadingScreen is built up front so it appears on screen
    immediately. Every other (asset-heavy) screen is built one frame
    later via Clock.schedule_once, so the loading screen isn't racing
    against big image/audio loads happening underneath it.
    """

    def build(self):
        self.title = "LURE"

        self.sm = LureManager(transition=FadeTransition(duration=FADE_TRANSITION_DURATION))
        self.nav_stack = []

        self.sm.add_widget(LoadingScreen(name="loading"))
        self.sm.current = "loading"
        self.nav_stack.append("loading")

        Clock.schedule_once(self._build_remaining_screens, 0)

        return self.sm

    def _build_remaining_screens(self, dt):
        from screens.home_screen import HomeScreen
        from screens.support_screen import SupportScreen
        from screens.hangar_screen import HangarScreen
        from screens.currency_store_screen import CurrencyStoreScreen
        from screens.menu_screen import MenuScreen
        from screens.settings_screen import SettingsScreen
        from screens.credits_screen import CreditsScreen
        from screens.gameplay_screen import GameplayScreen

        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(SupportScreen(name="support"))
        self.sm.add_widget(HangarScreen(name="hangar"))
        self.sm.add_widget(CurrencyStoreScreen(name="currency_store"))
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(CreditsScreen(name="credits"))
        self.sm.add_widget(GameplayScreen(name="gameplay"))

        # Everything exists now — safe to start the loading countdown.
        self.sm.get_screen("loading").start_countdown()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def navigate_to(self, screen_name, push_to_stack=True):
        if screen_name not in [s.name for s in self.sm.screens]:
            print(f"[LureApp] Unknown screen: {screen_name}")
            return

        if push_to_stack:
            self.nav_stack.append(screen_name)
        else:
            self.nav_stack = [screen_name]

        self.sm.current = screen_name

    def go_back(self):
        if len(self.nav_stack) <= 1:
            return
        self.nav_stack.pop()
        previous_screen = self.nav_stack[-1]
        self.sm.current = previous_screen


if __name__ == "__main__":
    LureApp().run()