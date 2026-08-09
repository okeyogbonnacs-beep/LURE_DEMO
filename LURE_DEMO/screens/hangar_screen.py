# screens/hangar_screen.py

import json


from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.graphics import Color, Rectangle
from kivy.app import App
from kivy.core.window import Window

from config import (
    BG_HANGAR, BTN_BACK, COIN_HOLDER, DIAMOND_HOLDER,
    BTN_EQUIP, BTN_UPGRADE, BTN_YES, BTN_BUY, asset_path,
    SHIPS_JSON_PATH,
)
from widgets.icon_button import IconButton
from widgets.message_box import MessageBox
from save_manager import save_manager




STAT_KEYS = ["health", "armor", "shield", "speed", "agility", "firepower", "energy", "cargo"]
STAT_LABELS = {
    "health": "Health", "armor": "Armor", "shield": "Shield", "speed": "Speed",
    "agility": "Agility", "firepower": "Firepower", "energy": "Energy", "cargo": "Cargo",
}

UPGRADE_COST = 876


def load_ships():
    with open(SHIPS_JSON_PATH, "r") as f:
        data = json.load(f)
    return data["ships"]


def format_currency(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"
    if value >= 1_000:
        return f"{value / 1_000:.1f}".rstrip("0").rstrip(".") + "k"
    return str(value)


def ship_rating(ship_data):
    stats = ship_data["stats"]
    avg = sum(stats[k] for k in STAT_KEYS) / len(STAT_KEYS)
    return round(avg)


class ShipPreviewButton(IconButton):
    """
    on_release_action must be passed through kwargs to IconButton's
    __init__ (which stores it internally as self._release_action) -
    setting it as a plain attribute afterward would never fire.
    """

    def __init__(self, ship_data, on_select, **kwargs):
        self._on_select_cb = on_select
        kwargs["on_release_action"] = self._select
        super().__init__(**kwargs)
        self.ship_data = ship_data

    def _select(self):
        self._on_select_cb(self.ship_data)


class UpgradeConfirmBox(MessageBox):
    def __init__(self, ship_data, on_confirm, **kwargs):
        super().__init__(width_hint=0.78, height_hint=0.75, **kwargs)
        self.ship_data = ship_data
        self._on_confirm_cb = on_confirm

        title = Label(
            text="[b]Upgrade Ship[/b]",
            markup=True,
            font_size="30sp",
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1),
        )
        self.content_area.add_widget(title)

        msg = Label(
            text=f"This upgrade takes {UPGRADE_COST} coins.\nApply it now?",
            font_size="20sp",
            color=(1, 1, 1, 1),
            halign="center",
        )
        msg.bind(width=lambda inst, w: setattr(inst, "text_size", (w, None)))
        self.content_area.add_widget(msg)

        spacer = BoxLayout(size_hint_y=1)
        self.content_area.add_widget(spacer)

        confirm_btn = IconButton(
            source=BTN_YES,
            size_hint=(None, None),
            size=(140, 46),
            pos_hint={"center_x": 0.5},
            on_release_action=self._confirm,
        )
        self.content_area.add_widget(confirm_btn)

    def _confirm(self):
        self._on_confirm_cb(self.ship_data)
        self.close()


class HangarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.ships = load_ships()
        self.ships_by_id = {s["id"]: s for s in self.ships}
        self.selected_ship_id = save_manager.get_equipped_ship()

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        self._bg = Image(
            source=BG_HANGAR,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(self._bg)

        # ---------------- Back button ----------------
        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.1674, 0.5075),
            pos_hint={"x": 0.039, "top": 1.17},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        # ---------------- Coin / Diamond holders (top-right) ----------------
        holder_row = BoxLayout(
            orientation="horizontal",
            size_hint=(0.42, 0.1),
            pos_hint={"right": 0.97, "top": 0.96},
            spacing=10,
        )
        self.root_layout.add_widget(holder_row)

        self.coin_holder_btn = self._build_currency_holder(COIN_HOLDER, self._open_currency_store)
        self.diamond_holder_btn = self._build_currency_holder(DIAMOND_HOLDER, self._open_currency_store)
        holder_row.add_widget(self.coin_holder_btn)
        holder_row.add_widget(self.diamond_holder_btn)

        # ---------------- Large ship preview (left-center) - uses PREVIEW art ----------------
        self.large_preview = Image(
            source=asset_path("UI", "Inventory", self.ships_by_id[self.selected_ship_id]["preview"]),
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(0.4, 0.5),
            pos_hint={"x": 0.02, "center_y": 0.55},
        )
        self.root_layout.add_widget(self.large_preview)

        # ---------------- Ship info panel (right side) ----------------
        self.info_panel = BoxLayout(
            orientation="vertical",
            size_hint=(0.4, 0.62),
            pos_hint={"right": 0.97, "top": 0.85},
            spacing=6,
            padding=14,
        )
        with self.info_panel.canvas.before:
            Color(0, 0, 0, 0.55)
            self._info_bg_rect = Rectangle(pos=self.info_panel.pos, size=self.info_panel.size)
        self.info_panel.bind(
            pos=lambda inst, val: setattr(self._info_bg_rect, "pos", val),
            size=lambda inst, val: setattr(self._info_bg_rect, "size", val),
        )
        self.root_layout.add_widget(self.info_panel)

        # ---------------- Bottom gradient + ship carousel ----------------
        self.bottom_gradient = FloatLayout(size_hint=(1, 0.2), pos_hint={"x": 0, "y": 0})
        with self.bottom_gradient.canvas.before:
            Color(0, 0, 0, 0.5)
            self._gradient_rect = Rectangle(pos=self.bottom_gradient.pos, size=self.bottom_gradient.size)
        self.bottom_gradient.bind(
            pos=lambda inst, val: setattr(self._gradient_rect, "pos", val),
            size=lambda inst, val: setattr(self._gradient_rect, "size", val),
        )
        self.root_layout.add_widget(self.bottom_gradient)

        self.carousel_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=False,
            bar_width=4,
        )
        self.bottom_gradient.add_widget(self.carousel_scroll)

        self.carousel_row = BoxLayout(
            orientation="horizontal",
            size_hint=(None, 1.2),
            spacing=12,
            padding=30,
        )
        self.carousel_row.bind(minimum_width=self.carousel_row.setter("width"))
        self.carousel_scroll.add_widget(self.carousel_row)

        self._build_ship_previews()
        self._refresh_currency_labels()
        self._refresh_info_panel()

    # --------------------------------------------------------
    # CURRENCY HOLDERS
    # --------------------------------------------------------

    def _build_currency_holder(self, icon_source, on_press):
        holder = FloatLayout(size_hint=(0.48, 1))

        img = Image(
            source=icon_source,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0},
        )
        holder.add_widget(img)

        label = Label(
            text="0",
            font_size="16sp",
            bold=True,
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.55, "center_y": 0.5},
            size_hint=(0.6, 0.6),
            halign="center",
            valign="middle",
        )
        label.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        holder.add_widget(label)
        holder._value_label = label

        holder.on_touch_down_original = holder.on_touch_down

        def _touch_down(touch, holder=holder, on_press=on_press):
            if holder.collide_point(*touch.pos):
                on_press()
                return True
            return holder.on_touch_down_original(touch)

        holder.on_touch_down = _touch_down

        return holder

    def _refresh_currency_labels(self):
        self.coin_holder_btn._value_label.text = format_currency(save_manager.get_gold())
        self.diamond_holder_btn._value_label.text = format_currency(save_manager.get_diamonds())

    def _open_currency_store(self):
        App.get_running_app().navigate_to("currency_store")

    # --------------------------------------------------------
    # SHIP CAROUSEL
    # --------------------------------------------------------

    def _build_ship_previews(self):
        self.carousel_row.clear_widgets()
        for ship_data in self.ships:
            preview_btn = ShipPreviewButton(
                ship_data=ship_data,
                on_select=self._on_ship_selected,
                source=asset_path("UI", "Inventory", ship_data["preview"]),
                size_hint=(None, 0.9),
                width=Window.width * 0.22,
                pos_hint={"center_y": 0.5},
            )
            self.carousel_row.add_widget(preview_btn)

    def _on_ship_selected(self, ship_data):
        self.selected_ship_id = ship_data["id"]
        self.large_preview.source = asset_path("UI", "Inventory", ship_data["preview"])
        self._refresh_info_panel()

    # --------------------------------------------------------
    # SHIP INFO PANEL
    # --------------------------------------------------------

    def _refresh_info_panel(self):
        self.info_panel.clear_widgets()
        ship_data = self.ships_by_id[self.selected_ship_id]

        name_label = Label(
            text=f"[b]{ship_data['name']}[/b]",
            markup=True,
            font_size="20sp",
            size_hint_y=None,
            height=32,
            color=(1, 1, 1, 1),
        )
        self.info_panel.add_widget(name_label)

        stats_scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        stats_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=8)
        stats_box.bind(minimum_height=stats_box.setter("height"))

        for stat_key in STAT_KEYS:
            value = ship_data["stats"][stat_key]
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=26, spacing=6)

            label = Label(
                text=STAT_LABELS[stat_key],
                font_size="12sp",
                size_hint_x=0.35,
                color=(0.9, 0.9, 0.9, 1),
                halign="left",
            )
            row.add_widget(label)

            bar = ProgressBar(max=100, value=value, size_hint_x=0.45)
            row.add_widget(bar)

            percent_label = Label(
                text=f"{value}%",
                font_size="12sp",
                size_hint_x=0.2,
                color=(1, 1, 1, 1),
            )
            row.add_widget(percent_label)

            stats_box.add_widget(row)

        stats_scroll.add_widget(stats_box)
        self.info_panel.add_widget(stats_scroll)

        rating = ship_rating(ship_data)
        rating_label = Label(
            text=f"Overall Rating: {rating} / 100",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=26,
            color=(1, 0.85, 0.4, 1),
        )
        self.info_panel.add_widget(rating_label)

        action_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=48, spacing=10)

        is_owned = save_manager.is_ship_owned(ship_data["id"])
        is_equipped = save_manager.get_equipped_ship() == ship_data["id"]

        equip_label = "Equipped" if is_equipped else ("Equip" if is_owned else f"{ship_data['cost']} coins")
        equip_btn_source = BTN_EQUIP if is_owned else BTN_BUY

        equip_btn = IconButton(
            source=equip_btn_source,
            size_hint=(0.5, 1),
            disabled=is_equipped,
            opacity=0.4 if is_equipped else 1.0,
            on_release_action=lambda sd=ship_data: self._on_equip_pressed(sd),
        )
        action_row.add_widget(equip_btn)

        upgrade_btn = IconButton(
            source=BTN_UPGRADE,
            size_hint=(0.5, 1),
            on_release_action=lambda sd=ship_data: self._on_upgrade_pressed(sd),
        )
        action_row.add_widget(upgrade_btn)

        self.info_panel.add_widget(action_row)

        equip_status_label = Label(
            text=equip_label,
            font_size="12sp",
            size_hint_y=None,
            height=20,
            color=(0.8, 0.8, 0.8, 1),
        )
        self.info_panel.add_widget(equip_status_label)

    # --------------------------------------------------------
    # EQUIP / UPGRADE ACTIONS
    # --------------------------------------------------------

    def _on_equip_pressed(self, ship_data):
        ship_id = ship_data["id"]

        if save_manager.is_ship_owned(ship_id):
            save_manager.set_equipped_ship(ship_id)
            self._refresh_info_panel()
            return

        success = save_manager.buy_ship(ship_id, ship_data["cost"])
        if success:
            save_manager.set_equipped_ship(ship_id)
            self._refresh_currency_labels()
            self._refresh_info_panel()

    def _on_upgrade_pressed(self, ship_data):
        box = UpgradeConfirmBox(ship_data=ship_data, on_confirm=self._apply_upgrade)
        box.open_on(self.root_layout)

    def _apply_upgrade(self, ship_data):
        success = save_manager.upgrade_ship(ship_data["id"], UPGRADE_COST)
        if success:
            self._refresh_currency_labels()
            self._refresh_info_panel()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    def _on_back_pressed(self):
        App.get_running_app().navigate_to("home")

    def on_pre_enter(self, *args):
        self.selected_ship_id = save_manager.get_equipped_ship()
        self._refresh_currency_labels()
        self._refresh_info_panel()
        self.large_preview.source = asset_path(
            "UI", "Inventory", self.ships_by_id[self.selected_ship_id]["preview"]
        )