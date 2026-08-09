# screens/daily_reward_window.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.clock import Clock

from widgets.message_box import MessageBox
from widgets.icon_button import IconButton
from save_manager import save_manager
from config import BTN_CLAIM


DAILY_REWARD_DIAMONDS = 100


class DailyRewardWindow(MessageBox):
    """
    MessageBox subclass showing the daily reward.

    - Shows diamond reward amount (text only, no icon).
    - Claim label sits above the drag-handle dots.
    - Clicking Claim adds diamonds via SaveManager and starts a
      real 24-hour cooldown (persisted, survives app restart).
    - If on cooldown, shows a live countdown instead of the Claim button.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._countdown_event = None

        title = Label(
            text="[b]Daily Reward[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=None,
            height=36,
            color=(1, 1, 1, 1),
        )
        self.content_area.add_widget(title)

        reward_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=80,
            spacing=14,
            padding=(0, 12),
        )

        reward_label = Label(
            text=f"+{DAILY_REWARD_DIAMONDS} Diamonds",
            font_size="26sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
        )
        reward_row.add_widget(reward_label)

        self.content_area.add_widget(reward_row)

        spacer = BoxLayout(size_hint_y=1)
        self.content_area.add_widget(spacer)

        self.status_label = Label(
            text="",
            font_size="15sp",
            size_hint_y=None,
            height=26,
            color=(0.85, 0.85, 0.85, 1),
        )
        self.content_area.add_widget(self.status_label)

        self.claim_btn = IconButton(
            source=BTN_CLAIM,
            size_hint=(None, None),
            size=(220, 70),
            pos_hint={"center_x": 0.5},
            on_release_action=self._on_claim,
        )
        self.content_area.add_widget(self.claim_btn)

        self._refresh_state()

    # --------------------------------------------------------
    # STATE / COOLDOWN
    # --------------------------------------------------------

    def _refresh_state(self):
        if save_manager.is_daily_reward_available():
            self.claim_btn.disabled = False
            self.claim_btn.opacity = 1.0
            self.status_label.text = "Ready to claim!"
            self._stop_countdown()
        else:
            self.claim_btn.disabled = True
            self.claim_btn.opacity = 0.4
            self._start_countdown()

    def _start_countdown(self):
        self._stop_countdown()
        self._update_countdown_label(0)
        self._countdown_event = Clock.schedule_interval(self._update_countdown_label, 1.0)

    def _stop_countdown(self):
        if self._countdown_event:
            self._countdown_event.cancel()
            self._countdown_event = None

    def _update_countdown_label(self, dt):
        remaining = save_manager.get_daily_reward_seconds_remaining()
        if remaining <= 0:
            self._refresh_state()
            return
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        self.status_label.text = f"Available in {hours:02d}:{minutes:02d}:{seconds:02d}"

    # --------------------------------------------------------
    # CLAIM
    # --------------------------------------------------------

    def _on_claim(self):
        if not save_manager.is_daily_reward_available():
            return
        save_manager.add_diamonds(DAILY_REWARD_DIAMONDS)
        save_manager.claim_daily_reward()
        self._refresh_state()

    # --------------------------------------------------------
    # CLEANUP
    # --------------------------------------------------------

    def close(self):
        self._stop_countdown()
        super().close()