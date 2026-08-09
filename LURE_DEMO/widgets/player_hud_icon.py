# widgets/player_hud_icon.py

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.core.window import Window

from config import PLAYER_ICON, HEALTH_BAR, ARMOUR_BAR, UPPER_BAR


class PlayerHudIcon(FloatLayout):
    """
    Pure display widget - the top-left HUD cluster.

    Health bar + armour bar are stacked so their combined height
    exactly matches the player icon's height. Each bar gets its own
    upper_bar.png overlay, positioned exactly on top of that bar
    (not one long overlay spanning both).
    """

    def __init__(self, ship_sprite_path, kills_needed, **kwargs):
        super().__init__(size_hint=(1, 1), **kwargs)
        self._kills_needed = kills_needed

        W, H = Window.width, Window.height

        icon_sz = H * 0.13
        gap     = H * 0.007
        bar_h   = (icon_sz - gap) / 2     # two bars + gap = icon_sz
        bar_w   = W * 0.44
        pad     = W * 0.018
        icon_x  = W * 0.018
        icon_y  = H - icon_sz - H * 0.018
        bar_x   = icon_x + icon_sz + pad
        ab_y    = icon_y                  # armour bar: bottom, aligns with icon bottom
        hb_y    = ab_y + bar_h + gap      # health bar: above armour bar

        self._bar_w = bar_w

        # player icon frame
        self.add_widget(Image(
            source=PLAYER_ICON, fit_mode="fill",
            size=(icon_sz, icon_sz), pos=(icon_x, icon_y),
            size_hint=(None, None),
        ))

        # equipped ship icon, inset inside the frame
        inset = icon_sz * 0.18
        self._ship_icon = Image(
            source=ship_sprite_path, fit_mode="contain",
            size=(icon_sz - inset * 2, icon_sz - inset * 2),
            pos=(icon_x + inset, icon_y + inset),
            size_hint=(None, None),
        )
        self.add_widget(self._ship_icon)

        # health bar - background + fill
        self._hb_bg = Image(
            source=HEALTH_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, hb_y),
            size_hint=(None, None), color=(0.25, 0.25, 0.25, 1),
        )
        self.add_widget(self._hb_bg)
        self._hb_fill = Image(
            source=HEALTH_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, hb_y),
            size_hint=(None, None),
        )
        self.add_widget(self._hb_fill)

        # armour bar - background + fill
        self._ab_bg = Image(
            source=ARMOUR_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, ab_y),
            size_hint=(None, None), color=(0.25, 0.25, 0.25, 1),
        )
        self.add_widget(self._ab_bg)
        self._ab_fill = Image(
            source=ARMOUR_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, ab_y),
            size_hint=(None, None),
        )
        self.add_widget(self._ab_fill)

        # decorative upper_bar overlay - one per bar, exact same
        # position/size as the bar it sits on top of
        self.add_widget(Image(
            source=UPPER_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, hb_y),
            size_hint=(None, None),
        ))
        self.add_widget(Image(
            source=UPPER_BAR, fit_mode="fill",
            size=(bar_w, bar_h), pos=(bar_x, ab_y),
            size_hint=(None, None),
        ))

        # timer label
        # timer label — aligned with health bar row
        tx = bar_x + bar_w + pad
        self._timer_lbl = Label(
            text="00:00", font_size="17sp", bold=True,
            color=(1, 1, 1, 1), halign="left", valign="middle",
            size=(W * 0.15, bar_h),
            pos=(tx, hb_y), size_hint=(None, None),
        )
        self._timer_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.add_widget(self._timer_lbl)

        # kill counter — aligned with armour bar row
        self._kill_lbl = Label(
            text=f"Kills: 0/{self._kills_needed}",
            font_size="13sp", bold=True,
            color=(1, 0.85, 0.25, 1), halign="left", valign="middle",
            size=(W * 0.18, bar_h),
            pos=(tx, ab_y), size_hint=(None, None),
        )
        self._kill_lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.add_widget(self._kill_lbl)


    # ── public update methods (called by gameplay_screen.py) ──────

    def update_health(self, cur, max_val):
        self._hb_fill.width = self._bar_w * max(0.0, cur / max_val)

    def update_armour(self, cur, max_val):
        self._ab_fill.width = self._bar_w * max(0.0, cur / max_val)

    def update_timer(self, seconds):
        m, s = int(seconds) // 60, int(seconds) % 60
        self._timer_lbl.text = f"{m:02d}:{s:02d}"

    def update_kills(self, count):
        self._kill_lbl.text = f"Kills: {count}/{self._kills_needed}"

    def set_ship_sprite(self, sprite_path):
        self._ship_icon.source = sprite_path
        self._ship_icon.reload()