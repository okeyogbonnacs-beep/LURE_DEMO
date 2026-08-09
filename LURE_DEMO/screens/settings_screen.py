# screens/settings_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.switch import Switch
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.app import App

from config import BG_SETTINGS, BTN_BACK, C_SLIDER, P_SLIDER
from widgets.icon_button import IconButton
from audio_manager import audio_manager
from save_manager import save_manager


KEYBIND_ACTIONS = [
    ("move_left",  "Move Left"),
    ("move_right", "Move Right"),
    ("move_up",    "Move Up"),
    ("move_down",  "Move Down"),
    ("shoot",      "Shoot"),
    ("bomb",       "Bomb"),
    ("pause",      "Pause"),
]


class SectionHeader(Label):
    def __init__(self, text, **kwargs):
        super().__init__(
            text=f"[b]{text}[/b]",
            markup=True,
            font_size="17sp",
            size_hint_y=None,
            height="38dp",
            halign="left",
            valign="middle",
            color=(1, 0.75, 0.3, 1),
            padding=(16, 0),
            **kwargs
        )
        self.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))


class Divider(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(size_hint_y=None, height="1dp", **kwargs)
        with self.canvas:
            Color(1, 1, 1, 0.15)
            self._line = Rectangle(pos=self.pos, size=self.size)
        self.bind(
            pos=lambda inst, val: setattr(self._line, "pos", val),
            size=lambda inst, val: setattr(self._line, "size", val),
        )


class SettingsRow(BoxLayout):
    def __init__(self, label_text, initial_value=1.0,
                 min_val=0.0, max_val=1.0, on_change=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height="64dp",
            spacing=12,
            padding=(16, 8),
            **kwargs
        )

        self.label = Label(
            text=label_text,
            font_size="15sp",
            size_hint_x=0.38,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        self.label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.add_widget(self.label)

        self.slider = Slider(
            min=min_val,
            max=max_val,
            value=initial_value,
            size_hint_x=0.47,
            cursor_image=C_SLIDER,
            cursor_size=("28dp", "28dp"),
            background_horizontal=P_SLIDER,
        )
        if on_change:
            self.slider.bind(value=lambda inst, val: on_change(val))
        self.add_widget(self.slider)

        self.value_label = Label(
            text=f"{int(initial_value * 100)}%",
            font_size="13sp",
            size_hint_x=0.15,
            halign="center",
            valign="middle",
            color=(1, 1, 0.6, 1),
        )
        self.value_label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        if on_change:
            self.slider.bind(
                value=lambda inst, val: setattr(
                    self.value_label, "text", f"{int(val * 100)}%"
                )
            )
        self.add_widget(self.value_label)


class ToggleRow(BoxLayout):
    def __init__(self, label_text, left_label, right_label,
                 initial_active=False, on_change=None, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height="64dp",
            spacing=12,
            padding=(16, 8),
            **kwargs
        )

        self.label = Label(
            text=label_text,
            font_size="15sp",
            size_hint_x=0.35,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        self.label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.add_widget(self.label)

        self.left_label = Label(
            text=left_label,
            font_size="14sp",
            size_hint_x=0.18,
            halign="right",
            valign="middle",
            color=(1, 1, 1, 0.8),
        )
        self.left_label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.add_widget(self.left_label)

        self.switch = Switch(
            active=initial_active,
            size_hint_x=0.22,
        )
        if on_change:
            self.switch.bind(active=lambda inst, val: on_change(val))
        self.add_widget(self.switch)

        self.right_label = Label(
            text=right_label,
            font_size="14sp",
            size_hint_x=0.25,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 0.8),
        )
        self.right_label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.add_widget(self.right_label)


class KeybindRow(BoxLayout):
    def __init__(self, action_key, action_label, current_key, on_remap, **kwargs):
        super().__init__(
            orientation="horizontal",
            size_hint_y=None,
            height="56dp",
            spacing=12,
            padding=(16, 6),
            **kwargs
        )
        self.action_key = action_key
        self.on_remap = on_remap

        name_label = Label(
            text=action_label,
            font_size="14sp",
            size_hint_x=0.50,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        name_label.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.add_widget(name_label)

        self.key_btn = Button(
            text=current_key.upper(),
            font_size="13sp",
            size_hint_x=0.30,
            size_hint_y=0.75,
            pos_hint={"center_y": 0.5},
            background_color=(0.2, 0.2, 0.3, 1),
            color=(1, 1, 0.5, 1),
        )
        self.key_btn.bind(on_release=self._open_remap_popup)
        self.add_widget(self.key_btn)

        reset_btn = Button(
            text="Reset",
            font_size="12sp",
            size_hint_x=0.20,
            size_hint_y=0.65,
            pos_hint={"center_y": 0.5},
            background_color=(0.3, 0.1, 0.1, 1),
            color=(1, 0.6, 0.6, 1),
        )
        reset_btn.bind(on_release=self._reset_key)
        self.add_widget(reset_btn)

    def _open_remap_popup(self, *args):
        content = BoxLayout(orientation="vertical", spacing=12, padding=16)

        instruction = Label(
            text=f"Press a key or type below\nfor: [b]{self.action_key}[/b]",
            markup=True,
            font_size="16sp",
            halign="center",
            size_hint_y=None,
            height="56dp",
            color=(1, 1, 1, 1),
        )
        content.add_widget(instruction)

        self._text_input = TextInput(
            text="",
            hint_text="Type key name e.g. a, space, up",
            multiline=False,
            font_size="16sp",
            size_hint_y=None,
            height="44dp",
        )
        content.add_widget(self._text_input)

        confirm_btn = Button(
            text="Confirm",
            size_hint_y=None,
            height="44dp",
            background_color=(0.1, 0.4, 0.1, 1),
        )
        confirm_btn.bind(on_release=self._confirm_remap)
        content.add_widget(confirm_btn)

        self._popup = Popup(
            title="Remap Key",
            content=content,
            size_hint=(0.75, 0.45),
        )
        self._popup.open()

    def _confirm_remap(self, *args):
        new_key = self._text_input.text.strip().lower()
        if new_key:
            save_manager.set_keybind(self.action_key, new_key)
            self.key_btn.text = new_key.upper()
            self.on_remap(self.action_key, new_key)
        self._popup.dismiss()

    def _reset_key(self, *args):
        from save_manager import DEFAULT_SAVE_DATA
        default_key = DEFAULT_SAVE_DATA["settings"]["keybinds"].get(self.action_key, "?")
        save_manager.set_keybind(self.action_key, default_key)
        self.key_btn.text = default_key.upper()
        self.on_remap(self.action_key, default_key)


class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        bg = Image(
            source=BG_SETTINGS,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(bg)

        with self.root_layout.canvas.before:
            Color(0, 0, 0, 0.5)
            self._overlay = Rectangle(
                pos=self.root_layout.pos,
                size=self.root_layout.size,
            )
        self.root_layout.bind(
            pos=lambda inst, val: setattr(self._overlay, "pos", val),
            size=lambda inst, val: setattr(self._overlay, "size", val),
        )

        title = Label(
            text="[b]SETTINGS[/b]",
            markup=True,
            font_size="22sp",
            size_hint=(0.5, 0.08),
            pos_hint={"center_x": 0.5, "top": 0.97},
            color=(1, 1, 1, 1),
            halign="center",
            valign="middle",
        )
        title.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.root_layout.add_widget(title)

        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.175, 0.267),
            pos_hint={"x": 0.0564, "top": 1.0265},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        self.scroll = ScrollView(
            size_hint=(0.92, 0.78),
            pos_hint={"center_x": 0.5, "y": 0.04},
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=4,
        )
        self.root_layout.add_widget(self.scroll)

        self.content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=4,
            padding=(0, 8),
        )
        self.content.bind(minimum_height=self.content.setter("height"))
        self.scroll.add_widget(self.content)

        self._build_settings()

    def _build_settings(self):
        s = save_manager.get_settings()
        keybinds = s.get("keybinds", {})
        is_pc = s.get("platform_mode", "mobile") == "pc"

        # ── PLATFORM ───────────────────────────────────────
        self.content.add_widget(SectionHeader("Platform"))
        self.content.add_widget(Divider())
        self.content.add_widget(ToggleRow(
            label_text="Mode",
            left_label="Mobile",
            right_label="PC",
            initial_active=is_pc,
            on_change=self._on_platform_toggle,
        ))

        # ── AUDIO ──────────────────────────────────────────
        self.content.add_widget(SectionHeader("Audio"))
        self.content.add_widget(Divider())
        self.content.add_widget(SettingsRow(
            "Music Volume",
            initial_value=s.get("volume", 1.0),
            on_change=self._on_music_volume,
        ))
        self.content.add_widget(SettingsRow(
            "SFX Volume",
            initial_value=s.get("sfx_volume", 1.0),
            on_change=self._on_sfx_volume,
        ))

        # ── DISPLAY ────────────────────────────────────────
        self.content.add_widget(SectionHeader("Display"))
        self.content.add_widget(Divider())
        self.content.add_widget(SettingsRow(
            "Brightness",
            initial_value=s.get("brightness", 1.0),
            on_change=self._on_brightness,
        ))
        self.content.add_widget(SettingsRow(
            "Graphics Quality",
            initial_value=s.get("graphics_quality", 1.0),
            on_change=self._on_graphics_quality,
        ))

        # ── GAMEPLAY ───────────────────────────────────────
        self.content.add_widget(SectionHeader("Gameplay"))
        self.content.add_widget(Divider())
        self.content.add_widget(SettingsRow(
            "Camera Shake",
            initial_value=s.get("camera_shake", 1.0),
            on_change=self._on_camera_shake,
        ))
        self.content.add_widget(SettingsRow(
            "Enemy Difficulty",
            initial_value=s.get("enemy_difficulty", 0.5),
            on_change=self._on_enemy_difficulty,
        ))
        self.content.add_widget(SettingsRow(
            "Fire Rate",
            initial_value=s.get("fire_rate", 0.5),
            on_change=self._on_fire_rate,
        ))
        self.content.add_widget(SettingsRow(
            "Bullet Speed",
            initial_value=s.get("bullet_speed", 0.5),
            on_change=self._on_bullet_speed,
        ))
        self.content.add_widget(SettingsRow(
            "Player Speed",
            initial_value=s.get("player_speed", 0.5),
            on_change=self._on_player_speed,
        ))

        # ── CONTROLS ───────────────────────────────────────
        self.content.add_widget(SectionHeader("Controls"))
        self.content.add_widget(Divider())
        self.content.add_widget(SettingsRow(
            "Joystick Size",
            initial_value=s.get("joystick_size", 0.5),
            on_change=self._on_joystick_size,
        ))
        self.content.add_widget(SettingsRow(
            "Joystick Sensitivity",
            initial_value=s.get("joystick_sensitivity", 0.5),
            on_change=self._on_joystick_sensitivity,
        ))
        self.content.add_widget(SettingsRow(
            "Shoot Button Size",
            initial_value=s.get("shoot_btn_size", 0.5),
            on_change=self._on_shoot_btn_size,
        ))

        # ── KEY MAPPING ────────────────────────────────────
        self.content.add_widget(SectionHeader("Key Mapping"))
        self.content.add_widget(Divider())

        pc_note = Label(
            text="Tap a key button to remap it. These apply in PC mode.",
            font_size="12sp",
            size_hint_y=None,
            height="28dp",
            halign="left",
            valign="middle",
            color=(0.7, 0.7, 0.7, 1),
            padding=(16, 0),
        )
        pc_note.bind(size=lambda inst, sz: setattr(inst, "text_size", sz))
        self.content.add_widget(pc_note)

        for action_key, action_label in KEYBIND_ACTIONS:
            current = keybinds.get(action_key, "?")
            row = KeybindRow(
                action_key=action_key,
                action_label=action_label,
                current_key=current,
                on_remap=self._on_keybind_remapped,
            )
            self.content.add_widget(row)

        # ── NOTIFICATIONS ──────────────────────────────────
        self.content.add_widget(SectionHeader("Notifications"))
        self.content.add_widget(Divider())
        self.content.add_widget(SettingsRow(
            "Song Toast Duration",
            initial_value=s.get("song_toast_duration", 0.5),
            on_change=self._on_song_toast_duration,
        ))

    # ── HANDLERS ───────────────────────────────────────────

    def _on_platform_toggle(self, is_pc):
        mode = "pc" if is_pc else "mobile"
        save_manager.set_setting("platform_mode", mode)

    def _on_music_volume(self, val):
        save_manager.set_setting("volume", val)
        audio_manager.set_volume(val)

    def _on_sfx_volume(self, val):
        save_manager.set_setting("sfx_volume", val)
        for sound in audio_manager._sfx_cache.values():
            if sound:
                sound.volume = val
    def _on_brightness(self, val):
        save_manager.set_setting("brightness", val)
        if not hasattr(self, "_brightness_overlay"):
            from kivy.core.window import Window
            from kivy.uix.widget import Widget
            from kivy.graphics import Color, Rectangle
            overlay = Widget(size_hint=(1, 1))
            with overlay.canvas:
                self._bright_color = Color(0, 0, 0, 0)
                self._bright_rect = Rectangle(
                    pos=(0, 0), size=Window.size   # fixed: no Window.pos
                )
            Window.bind(
                size=lambda inst, sz: setattr(self._bright_rect, "size", sz)
            )
            Window.add_widget(overlay)
            self._brightness_overlay = overlay
        self._bright_color.a = 1.0 - val

    def _on_graphics_quality(self, val):
        save_manager.set_setting("graphics_quality", val)

    def _on_camera_shake(self, val):
        save_manager.set_setting("camera_shake", val)

    def _on_enemy_difficulty(self, val):
        save_manager.set_setting("enemy_difficulty", val)

    def _on_fire_rate(self, val):
        save_manager.set_setting("fire_rate", val)

    def _on_bullet_speed(self, val):
        save_manager.set_setting("bullet_speed", val)

    def _on_player_speed(self, val):
        save_manager.set_setting("player_speed", val)

    def _on_joystick_size(self, val):
        save_manager.set_setting("joystick_size", val)

    def _on_joystick_sensitivity(self, val):
        save_manager.set_setting("joystick_sensitivity", val)

    def _on_shoot_btn_size(self, val):
        save_manager.set_setting("shoot_btn_size", val)

    def _on_keybind_remapped(self, action_key, new_key):
        pass  # already saved inside KeybindRow

    def _on_song_toast_duration(self, val):
        actual_seconds = 2 + val * 6
        save_manager.set_setting("song_toast_duration", val)
        import widgets.song_toast as st_module
        st_module.SONG_TOAST_DURATION = actual_seconds

    # ── NAVIGATION ─────────────────────────────────────────

    def _on_back_pressed(self):
        App.get_running_app().navigate_to("menu")

    def on_pre_enter(self, *args):
        self.content.clear_widgets()
        self._build_settings()