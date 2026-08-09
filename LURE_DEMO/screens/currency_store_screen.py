# screens/currency_store_screen.py
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.app import App

from config import (
    BG_STORE, BTN_BACK, COIN_HOLDER, DIAMOND_HOLDER,
    COIN_PACK_ICONS, DIAMOND_PACK_ICONS, BTN_BUY,
)
from widgets.icon_button import IconButton
from widgets.message_box import MessageBox
from save_manager import save_manager


COIN_PACK_AMOUNTS = [1000, 10000, 45000, 99000, 120000]
DIAMOND_PACK_AMOUNTS = [100, 1000, 4500, 9900, 12000]

PACK_ITEM_HEIGHT_HINT = 0.50


def format_currency(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"
    if value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(value)


class PackButton(IconButton):
    """
    A single purchasable pack icon (art already shows the amount,
    no separate text label needed). Clicking opens Buy confirmation.
    """

    def __init__(self, currency_type, amount, on_pack_selected, **kwargs):
        self._currency_type = currency_type
        self._amount = amount
        self._on_pack_selected_cb = on_pack_selected
        kwargs["on_release_action"] = self._select
        super().__init__(**kwargs)

    def _select(self):
        self._on_pack_selected_cb(self._currency_type, self._amount)


class CurrencyHolderButton(IconButton):
    """
    Coin/Diamond holder that behaves like a real button (press effect,
    sound, scale/darken) while also displaying the current amount as
    text centered over the holder art.
    """

    def __init__(self, on_press=None, **kwargs):
        kwargs["on_release_action"] = on_press
        super().__init__(**kwargs)

        self._value_label = Label(
            text="0",
            font_size="16sp",
            bold=True,
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
            size_hint=(None, None),
        )
        self._value_label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        self.bind(pos=self._sync_label, size=self._sync_label)
        Clock.schedule_once(lambda dt: self._sync_label(), 0)

    def _sync_label(self, *args):
        if hasattr(self, "_value_label"):
            self._value_label.pos = self.pos
            self._value_label.size = self.size


class BuyConfirmBox(MessageBox):
    """
    Confirmation popup: "Do you want to buy X Coins/Diamonds?"
    No real payment gateway - clicking Buy immediately adds the
    amount and updates the holder instantly.
    """

    def __init__(self, currency_type, amount, on_confirm, **kwargs):
        super().__init__(width_hint=0.7, height_hint=0.75, **kwargs)
        self.currency_type = currency_type
        self.amount = amount
        self._on_confirm_cb = on_confirm

        currency_label = "Coins" if currency_type == "coins" else "Diamonds"

        title = Label(
            text="[b]Confirm Purchase[/b]",
            markup=True,
            font_size="20sp",
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1),
        )
        self.content_area.add_widget(title)

        msg = Label(
            text=f"Do you want to buy {format_currency(amount)} {currency_label}?",
            font_size="17sp",
            color=(1, 1, 1, 1),
            halign="center",
        )
        msg.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.content_area.add_widget(msg)

        spacer = BoxLayout(size_hint_y=1)
        self.content_area.add_widget(spacer)

        buy_btn = IconButton(
            source=BTN_BUY,
            size_hint=(None, None),
            size=(220, 70),
            pos_hint={"center_x": 0.5},
            on_release_action=self._confirm,
        )
        self.content_area.add_widget(buy_btn)

    def _confirm(self):
        self._on_confirm_cb(self.currency_type, self.amount)
        self.close()


class CurrencyStoreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self._bg = Image(
            source=BG_STORE,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self._bg)

        # ---------------- Back button (top-left) ----------------
        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.1894, 0.3324),
            pos_hint={"x": 0.0192, "top": 1.0565},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        # ---------------- Coin / Diamond holders (top-right) ----------------
        self.coin_holder_btn = CurrencyHolderButton(
            source=COIN_HOLDER,
            size_hint=(0.1488, 0.2603),
            pos_hint={"right": 0.792, "top": 1.0278},
            on_press=self._no_action_here,
        )
        self.root_layout.add_widget(self.coin_holder_btn)
        self.root_layout.add_widget(self.coin_holder_btn._value_label)

        self.diamond_holder_btn = CurrencyHolderButton(
            source=DIAMOND_HOLDER,
            size_hint=(0.1578, 0.2663),
            pos_hint={"right": 0.9601, "top": 1.025},
            on_press=self._no_action_here,
        )
        self.root_layout.add_widget(self.diamond_holder_btn)
        self.root_layout.add_widget(self.diamond_holder_btn._value_label)

        # ---------------- Center gradient panel ----------------
        self.center_panel = FloatLayout(
            size_hint=(0.86, 0.72),
            pos_hint={"center_x": 0.5, "top": 0.84},
        )
        with self.center_panel.canvas.before:
            Color(0, 0, 0, 0.55)
            self._panel_bg_rect = Rectangle(pos=self.center_panel.pos, size=self.center_panel.size)
        self.center_panel.bind(
            pos=lambda inst, val: setattr(self._panel_bg_rect, "pos", val),
            size=lambda inst, val: setattr(self._panel_bg_rect, "size", val),
        )
        self.root_layout.add_widget(self.center_panel)

        self._scroll = ScrollView(
            size_hint=(0.96, 0.96),
            pos_hint={"center_x": 0.5, "top": 0.98},
            do_scroll_x=False,
        )
        self.center_panel.add_widget(self._scroll)

        self._content = BoxLayout(orientation="vertical", size_hint_y=None, spacing=24, padding=(10, 16))
        self._content.bind(minimum_height=self._content.setter("height"))
        self._scroll.add_widget(self._content)

        self._build_pack_section("Coin Packs", COIN_PACK_ICONS, COIN_PACK_AMOUNTS, "coins")
        self._build_pack_section("Diamond Packs", DIAMOND_PACK_ICONS, DIAMOND_PACK_AMOUNTS, "diamonds")

        self._refresh_currency_labels()

    # --------------------------------------------------------
    # CURRENCY HOLDERS
    # --------------------------------------------------------

    def _refresh_currency_labels(self):
        self.coin_holder_btn._value_label.text = format_currency(save_manager.get_gold())
        self.diamond_holder_btn._value_label.text = format_currency(save_manager.get_diamonds())

    def _no_action_here(self):
        pass

    # --------------------------------------------------------
    # PACK GRID
    # --------------------------------------------------------

    def _build_pack_section(self, title_text, icon_list, amount_list, currency_type):
        section_title = Label(
            text=f"[b]{title_text}[/b]",
            markup=True,
            font_size="20sp",
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1),
        )
        self._content.add_widget(section_title)

        grid = GridLayout(cols=2, size_hint_y=None, spacing=20, padding=(0, 6))
        grid.bind(minimum_height=grid.setter("height"))

        for icon_source, amount in zip(icon_list, amount_list):
            pack_btn = PackButton(
                currency_type=currency_type,
                amount=amount,
                on_pack_selected=self._on_pack_selected,
                source=icon_source,
                size_hint=(1, None),
                height=170,
            )
            grid.add_widget(pack_btn)

        self._content.add_widget(grid)

    def _on_pack_selected(self, currency_type, amount):
        box = BuyConfirmBox(
            currency_type=currency_type,
            amount=amount,
            on_confirm=self._complete_purchase,
        )
        box.open_on(self.root_layout)

    def _complete_purchase(self, currency_type, amount):
        if currency_type == "coins":
            save_manager.add_gold(amount)
        else:
            save_manager.add_diamonds(amount)
        self._refresh_currency_labels()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def _on_back_pressed(self):
        App.get_running_app().navigate_to("hangar")

    def on_pre_enter(self, *args):
        self._refresh_currency_labels()