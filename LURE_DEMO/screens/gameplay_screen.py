# screens/gameplay_screen.py

import math
import os
import random

from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.app import App

from screens.pause_screen import PauseOverlay
from audio_manager import audio_manager
from config import (
    BTN_PAUSE, BTN_HOME_ICON, ENEMY_DEFS, asset_path,
)
from widgets.icon_button import IconButton
from widgets.joystick import Joystick
from widgets.player_ship import PlayerShip
from widgets.player_hud_icon import PlayerHudIcon
from widgets.combat_buttons import ShootButton, BombButton
from widgets.mission_dialogue import MissionDialogue
from widgets.scrolling_background import ScrollingBackground
from widgets.bullet import Projectile
from widgets.enemy_ship import EnemyShip
from widgets.explosion import Explosion
from widgets.message_box import MessageBox

from save_manager import save_manager
from ship_utils import load_ship_sprite_filename


DEMO_MISSION_TEXT = "Pilot, enemy forces have entered the sector. Hold the line."
KILLS_NEEDED = 5


class GameplayScreen(Screen):

    JOYSTICK_HINT = {"size": (0.2053, 0.3622), "pos": (0.1129, 0.066)}
    SHOOT_BTN_HINT = {"size": (0.1103, 0.2402), "pos": (0.6721, 0.1251)}
    BOMB_BTN_HINT = {"size": (0.1144, 0.2168), "pos": (0.7906, 0.273)}

    SHIP_SIZE_RATIO = 0.20
    CAMERA_MARGIN_RATIO = 0.20
    WORLD_SIZE_MULT = 3.0

    PLAYER_MOVE_SPEED = 200
    PLAYER_MAX_HEALTH = 100
    PLAYER_MAX_ARMOUR = 50
    PLAYER_FIRE_RATE = 0.25
    PLAYER_BULLET_SPEED = 420
    PLAYER_BULLET_DAMAGE = 10
    PLAYER_BOMB_SPEED = 160
    PLAYER_BOMB_DAMAGE = 35
    PLAYER_BOMB_COOLDOWN = 5.0

    ENEMY_MAX_CONCURRENT = 5
    ENEMY_SPAWN_INTERVAL = 3.0
    ENEMY_HEALTH = 30
    ENEMY_WANDER_SPEED = 60
    ENEMY_CHASE_SPEED = 110
    ENEMY_DETECT_RADIUS = 260
    ENEMY_LOSE_RADIUS = 340
    ENEMY_SHOOT_RANGE = 380
    ENEMY_SHOOT_COOLDOWN = 2.2
    ENEMY_BULLET_SPEED = 260
    ENEMY_BULLET_DAMAGE = 8
    ENEMY_BOMB_RANGE = 220
    ENEMY_BOMB_COOLDOWN = 6.0
    ENEMY_BOMB_SPEED = 90
    ENEMY_BOMB_DAMAGE = 18
    ENEMY_CONTACT_DAMAGE = 6
    ENEMY_CONTACT_COOLDOWN = 1.0

    BULLET_SIZE_RATIO = 0.06
    BOMB_SIZE_RATIO = 0.10
    EXPLOSION_SIZE_RATIO = 0.20

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._active = False
        self._shooting = False
        self._bomb_queued = False
        self._fire_timer = 0.0
        self._player_bomb_timer = 0.0

        self.enemies = []
        self.bullets = []
        self.explosions = []

        self._elapsed = 0.0
        self._kills = 0
        self._current_ship_id = None
        self._facing_angle = 90.0

        self._player_health = self.PLAYER_MAX_HEALTH
        self._player_armour = self.PLAYER_MAX_ARMOUR

        self._spawn_timer = 0.0
        self._mission_over = False
        self._mission_won_shown = False

        self.world_width = Window.width * self.WORLD_SIZE_MULT
        self.world_height = Window.height * self.WORLD_SIZE_MULT
        self.camera_x = (self.world_width - Window.width) / 2
        self.camera_y = (self.world_height - Window.height) / 2

        self._is_pc_mode = False
        self._keybinds = {}
        self._kb_move_state = {
            "move_left": False, "move_right": False,
            "move_up": False, "move_down": False,
        }
        self._kb_held_actions = set()

        self._build_ui()
        Window.bind(size=self._on_window_resize)
        Window.bind(on_key_down=self._on_key_down)
        Window.bind(on_key_up=self._on_key_up)

    # ------------------------------------------------------------
    # SETUP
    # ------------------------------------------------------------

    def _build_ui(self):
        self.background = ScrollingBackground(
            world_size=(self.world_width, self.world_height)
        )
        self.add_widget(self.background)

        sprite_path = self._get_selected_ship_sprite()
        self._current_ship_id = save_manager.get_equipped_ship()
        self._refresh_weapon_paths(sprite_path)

        ship_size = min(Window.width, Window.height) * self.SHIP_SIZE_RATIO
        self.player_ship = PlayerShip(sprite_path, size=(ship_size, ship_size))
        self.player_ship.world_x = self.world_width / 2 - ship_size / 2
        self.player_ship.world_y = self.world_height / 2 - ship_size / 2
        self.add_widget(self.player_ship)

        self.hud_icon = PlayerHudIcon(sprite_path, KILLS_NEEDED)
        self.add_widget(self.hud_icon)

        self.joystick = Joystick(size=(1, 1))
        self.add_widget(self.joystick)

        self.shoot_btn = ShootButton(
            size=(1, 1),
            on_press_callback=self._on_shoot_press,
            on_release_callback=self._on_shoot_release,
        )
        self.add_widget(self.shoot_btn)

        self.bomb_btn = BombButton(
            size=(1, 1),
            on_press_callback=self._on_bomb_press,
        )
        self.add_widget(self.bomb_btn)

        self.pause_btn = IconButton(
            source=BTN_PAUSE,
            size_hint=(0.09, 0.09),
            pos_hint={"right": 0.97, "top": 0.97},
            on_release_action=self._show_pause_overlay,
        )
        self.add_widget(self.pause_btn)

        self._apply_combat_layout()
        self._sync_world_positions()

    def _apply_combat_layout(self):
        W, H = Window.width, Window.height

        jw = W * self.JOYSTICK_HINT["size"][0]
        jh = H * self.JOYSTICK_HINT["size"][1]
        jx = W * self.JOYSTICK_HINT["pos"][0]
        jy = H * self.JOYSTICK_HINT["pos"][1]
        self.joystick.size = (jw, jh)
        self.joystick.pos = (jx, jy)

        sw = W * self.SHOOT_BTN_HINT["size"][0]
        sh = H * self.SHOOT_BTN_HINT["size"][1]
        sx = W * self.SHOOT_BTN_HINT["pos"][0]
        sy = H * self.SHOOT_BTN_HINT["pos"][1]
        self.shoot_btn.size = (sw, sh)
        self.shoot_btn.pos = (sx, sy)

        bw = W * self.BOMB_BTN_HINT["size"][0]
        bh = H * self.BOMB_BTN_HINT["size"][1]
        bx = W * self.BOMB_BTN_HINT["pos"][0]
        by = H * self.BOMB_BTN_HINT["pos"][1]
        self.bomb_btn.size = (bw, bh)
        self.bomb_btn.pos = (bx, by)

    def _on_window_resize(self, instance, size):
        self._apply_combat_layout()

    def _get_selected_ship_sprite(self):
        ship_id = save_manager.get_equipped_ship()
        filename = load_ship_sprite_filename(ship_id)
        return asset_path("characters", "player", filename)

    def _refresh_weapon_paths(self, sprite_path):
        base = os.path.splitext(os.path.basename(sprite_path))[0]
        self._player_bullet_path = asset_path("characters", "player weapons", f"{base}_bullet.png")
        self._player_bomb_path = asset_path("characters", "player weapons", f"{base}_bomb.png")
        self._player_explosion_path = asset_path("characters", "player weapons", f"{base}_explosion.png")

    def _refresh_player_ship_if_changed(self):
        equipped_id = save_manager.get_equipped_ship()
        if equipped_id == self._current_ship_id:
            return
        self._current_ship_id = equipped_id
        sprite_path = self._get_selected_ship_sprite()
        self.player_ship.set_sprite(sprite_path)
        self.hud_icon.set_ship_sprite(sprite_path)
        self._refresh_weapon_paths(sprite_path)

    # ------------------------------------------------------------
    # PLATFORM MODE
    # ------------------------------------------------------------

    def _apply_platform_mode(self):
        settings = save_manager.get_settings()
        self._is_pc_mode = settings.get("platform_mode", "mobile") == "pc"
        self._keybinds = dict(settings.get("keybinds", {}))

        touch_opacity = 0 if self._is_pc_mode else 1
        touch_enabled = not self._is_pc_mode

        self.joystick.opacity = touch_opacity
        self.joystick.input_enabled = touch_enabled

        self.shoot_btn.opacity = touch_opacity
        self.shoot_btn.input_enabled = touch_enabled

        self.bomb_btn.opacity = touch_opacity
        self.bomb_btn.input_enabled = touch_enabled

        for k in self._kb_move_state:
            self._kb_move_state[k] = False
        self._kb_held_actions.clear()
        if self._is_pc_mode:
            self._shooting = False

    def _action_for_key(self, codepoint, key):
        for action, bound_key in self._keybinds.items():
            if not bound_key:
                continue
            bound_key = bound_key.lower()
            if bound_key == "spacebar":
                if codepoint == " " or key == 32:
                    return action
            elif bound_key == "escape":
                if key == 27:
                    return action
            else:
                if codepoint is not None and codepoint.lower() == bound_key and len(bound_key) == 1:
                    return action
        return None

    def _on_key_down(self, window, key, scancode, codepoint, modifiers):
        if self.manager is None or self.manager.current != self.name:
            return False
        if not self._is_pc_mode:
            return False

        action = self._action_for_key(codepoint, key)
        if action is None:
            return False

        if action == "pause":
            if "pause" in self._kb_held_actions:
                return True
            self._kb_held_actions.add("pause")
            if getattr(self, "_pause_overlay", None):
                self._on_resume_pressed()
            else:
                self._show_pause_overlay()
            return True

        if not self._active:
            return False

        if action in self._kb_move_state:
            self._kb_move_state[action] = True
        elif action == "shoot":
            self._shooting = True
        elif action == "bomb":
            if "bomb" not in self._kb_held_actions:
                self._kb_held_actions.add("bomb")
                self._bomb_queued = True

        return True

    def _on_key_up(self, window, key, scancode, codepoint=None):
        if self.manager is None or self.manager.current != self.name:
            return False
        if not self._is_pc_mode:
            return False

        for action, bound_key in self._keybinds.items():
            if not bound_key:
                continue
            bound_key = bound_key.lower()
            matched = False
            if bound_key == "spacebar" and key == 32:
                matched = True
            elif bound_key == "escape" and key == 27:
                matched = True
            elif len(bound_key) == 1 and codepoint is not None and codepoint.lower() == bound_key:
                matched = True

            if not matched:
                continue

            self._kb_held_actions.discard(action)
            if action in self._kb_move_state:
                self._kb_move_state[action] = False
            elif action == "shoot":
                self._shooting = False
            return True

        return False

    # ------------------------------------------------------------
    # PAUSE (music resumes while paused, re-pauses on resume)
    # ------------------------------------------------------------

    def _show_pause_overlay(self):
        self._active = False
        audio_manager.stop_movement_sfx()
        if audio_manager.is_paused_for_gameplay():
            audio_manager.resume_after_gameplay()
        self._pause_overlay = PauseOverlay(
            on_resume=self._on_resume_pressed,
            on_home=self._on_home_pressed,
        )
        self.add_widget(self._pause_overlay)

    def _on_resume_pressed(self):
        if getattr(self, "_pause_overlay", None):
            self.remove_widget(self._pause_overlay)
            self._pause_overlay = None
        self._active = True
        if not audio_manager.is_paused_for_gameplay():
            audio_manager.pause_for_gameplay()

    def _on_home_pressed(self):
        if getattr(self, "_pause_overlay", None):
            self.remove_widget(self._pause_overlay)
            self._pause_overlay = None
        self._active = False
        audio_manager.stop_movement_sfx()
        if not audio_manager.is_paused_for_gameplay():
            audio_manager.resume_after_gameplay()
        else:
            audio_manager.resume_after_gameplay()
        App.get_running_app().navigate_to("home")

    # ------------------------------------------------------------
    # SCREEN LIFECYCLE
    # ------------------------------------------------------------

    def on_enter(self):
        self._apply_combat_layout()
        self._refresh_player_ship_if_changed()
        self._apply_platform_mode()
        self._reset_mission_state()
        self._show_mission_dialogue()
        Clock.schedule_interval(self._update, 1.0 / 60.0)

    def on_leave(self):
        Clock.unschedule(self._update)
        audio_manager.stop_movement_sfx()

    def _reset_mission_state(self):
        for e in list(self.enemies):
            self.remove_widget(e)
        for b in list(self.bullets):
            self.remove_widget(b)
        for x in list(self.explosions):
            self.remove_widget(x)
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self._kills = 0
        self._elapsed = 0.0
        self._player_health = self.PLAYER_MAX_HEALTH
        self._player_armour = self.PLAYER_MAX_ARMOUR
        self._spawn_timer = 0.0
        self._mission_over = False
        self._mission_won_shown = False

        self.player_ship.world_x = self.world_width / 2 - self.player_ship.width / 2
        self.player_ship.world_y = self.world_height / 2 - self.player_ship.height / 2
        self.camera_x = (self.world_width - Window.width) / 2
        self.camera_y = (self.world_height - Window.height) / 2
        self._sync_world_positions()

    def _show_mission_dialogue(self):
        dialogue = MissionDialogue(
            text=DEMO_MISSION_TEXT,
            on_close_callback=self._on_dialogue_close,
        )
        self.add_widget(dialogue)

    def _on_dialogue_close(self):
        self._active = True

    # ------------------------------------------------------------
    # TOUCH COMBAT CALLBACKS
    # ------------------------------------------------------------

    def _on_shoot_press(self, touch):
        self._shooting = True

    def _on_shoot_release(self, touch):
        self._shooting = False

    def _on_bomb_press(self):
        self._bomb_queued = True

    # ------------------------------------------------------------
    # MAIN UPDATE LOOP
    # ------------------------------------------------------------

    def _update(self, dt):
        if not self._active:
            return

        self._elapsed += dt

        self._read_input()
        self._move_player(dt)
        self._rotate_player()
        self._update_camera()

        self._handle_shooting(dt)
        self._handle_bomb(dt)

        self._spawn_enemies(dt)
        self._move_enemies(dt)
        self._handle_enemy_shooting(dt)

        self._move_bullets(dt)

        self._sync_world_positions()

        self._check_collisions()

        self._update_health_ui()
        self._update_armour_ui()
        self._update_timer_ui()
        self._update_kills_ui()
        self._check_mission_complete()

    def _read_input(self):
        if self._is_pc_mode:
            dx = 0.0
            dy = 0.0
            if self._kb_move_state["move_left"]:
                dx -= 1.0
            if self._kb_move_state["move_right"]:
                dx += 1.0
            if self._kb_move_state["move_up"]:
                dy += 1.0
            if self._kb_move_state["move_down"]:
                dy -= 1.0

            mag = math.hypot(dx, dy)
            if mag > 0:
                self._joy_dx = dx / mag
                self._joy_dy = dy / mag
                self._joy_mag = 1.0
            else:
                self._joy_dx = 0.0
                self._joy_dy = 0.0
                self._joy_mag = 0.0
        else:
            self._joy_dx = self.joystick.dx
            self._joy_dy = self.joystick.dy
            self._joy_mag = self.joystick.magnitude

    # ------------------------------------------------------------
    # WORLD / CAMERA
    # ------------------------------------------------------------

    def _move_player(self, dt):
        if self._joy_mag <= 0:
            audio_manager.stop_movement_sfx()
            return

        audio_manager.start_movement_sfx()

        move_x = self._joy_dx * self.PLAYER_MOVE_SPEED * self._joy_mag * dt
        move_y = self._joy_dy * self.PLAYER_MOVE_SPEED * self._joy_mag * dt

        new_x = self.player_ship.world_x + move_x
        new_y = self.player_ship.world_y + move_y

        new_x = max(0, min(new_x, self.world_width - self.player_ship.width))
        new_y = max(0, min(new_y, self.world_height - self.player_ship.height))

        self.player_ship.world_x = new_x
        self.player_ship.world_y = new_y

    def _rotate_player(self):
        if self._joy_mag > 0:
            if self._is_pc_mode:
                angle = math.degrees(math.atan2(self._joy_dy, self._joy_dx))
                self._facing_angle = angle % 360
            else:
                self._facing_angle = self.joystick.snapped_angle_deg
            self.player_ship.set_angle(self._facing_angle)

    def _update_camera(self):
        W, H = Window.width, Window.height
        margin_x = W * self.CAMERA_MARGIN_RATIO
        margin_y = H * self.CAMERA_MARGIN_RATIO

        ship_screen_x = self.player_ship.world_x - self.camera_x
        ship_screen_y = self.player_ship.world_y - self.camera_y

        min_x = margin_x
        max_x = W - margin_x - self.player_ship.width
        min_y = margin_y
        max_y = H - margin_y - self.player_ship.height

        if ship_screen_x < min_x:
            self.camera_x -= (min_x - ship_screen_x)
        elif ship_screen_x > max_x:
            self.camera_x += (ship_screen_x - max_x)

        if ship_screen_y < min_y:
            self.camera_y -= (min_y - ship_screen_y)
        elif ship_screen_y > max_y:
            self.camera_y += (ship_screen_y - max_y)

        self.camera_x = max(0, min(self.camera_x, self.world_width - W))
        self.camera_y = max(0, min(self.camera_y, self.world_height - H))

    def _sync_world_positions(self):
        cx, cy = self.camera_x, self.camera_y
        self.background.pos = (-cx, -cy)
        self.player_ship.pos = (self.player_ship.world_x - cx, self.player_ship.world_y - cy)
        for e in self.enemies:
            e.pos = (e.world_x - cx, e.world_y - cy)
        for b in self.bullets:
            b.pos = (b.world_x - cx, b.world_y - cy)
        for x in self.explosions:
            x.pos = (x.world_x - cx, x.world_y - cy)

    def _spawn_point_under(self, entity, size):
        center_x = entity.world_x + entity.width / 2
        bottom_y = entity.world_y
        return (center_x - size / 2, bottom_y - size * 0.3)

    # ------------------------------------------------------------
    # PROJECTILES (shared player + enemy spawning)
    # ------------------------------------------------------------

    def _spawn_projectile_aimed(self, shooter_world_center, target_world_center,
                                 source, speed, damage, owner, is_bomb,
                                 explosion_source, spawn_under=None, facing_angle=None):
        if facing_angle is not None:
            rad = math.radians(facing_angle)
        else:
            sx, sy = shooter_world_center
            tx, ty = target_world_center
            dist = math.hypot(tx - sx, ty - sy)
            if dist == 0:
                return
            rad = math.atan2(ty - sy, tx - sx)

        vx = math.cos(rad) * speed
        vy = math.sin(rad) * speed

        size = min(Window.width, Window.height) * (
            self.BOMB_SIZE_RATIO if is_bomb else self.BULLET_SIZE_RATIO
        )

        if spawn_under is not None:
            world_pos = self._spawn_point_under(spawn_under, size)
        else:
            cx, cy = shooter_world_center
            world_pos = (cx - size / 2, cy - size / 2)

        proj = Projectile(
            source=source, size=(size, size), world_pos=world_pos,
            vx=vx, vy=vy, damage=damage, owner=owner, is_bomb=is_bomb,
            explosion_source=explosion_source,
        )
        self.bullets.append(proj)
        self.add_widget(proj)

        # bullet sound plays on every shot fired (player and enemy),
        # bombs do NOT get the shooting sound - only their own
        # explosion sound on impact
        if not is_bomb:
            audio_manager.play_shoot_sfx()

    # ------------------------------------------------------------
    # PLAYER SHOOTING / BOMBING
    # ------------------------------------------------------------

    def _handle_shooting(self, dt):
        self._fire_timer -= dt
        if not self._shooting or self._fire_timer > 0:
            return
        self._fire_timer = self.PLAYER_FIRE_RATE

        pcx = self.player_ship.world_x + self.player_ship.width / 2
        pcy = self.player_ship.world_y + self.player_ship.height / 2

        self._spawn_projectile_aimed(
            shooter_world_center=(pcx, pcy), target_world_center=None,
            source=self._player_bullet_path, speed=self.PLAYER_BULLET_SPEED,
            damage=self.PLAYER_BULLET_DAMAGE, owner="player", is_bomb=False,
            explosion_source=self._player_explosion_path,
            spawn_under=None, facing_angle=self._facing_angle,
        )

    def _handle_bomb(self, dt):
        self._player_bomb_timer -= dt
        if not self._bomb_queued:
            return
        self._bomb_queued = False
        if self._player_bomb_timer > 0:
            return
        self._player_bomb_timer = self.PLAYER_BOMB_COOLDOWN

        pcx = self.player_ship.world_x + self.player_ship.width / 2
        pcy = self.player_ship.world_y + self.player_ship.height / 2

        self._spawn_projectile_aimed(
            shooter_world_center=(pcx, pcy), target_world_center=None,
            source=self._player_bomb_path, speed=self.PLAYER_BOMB_SPEED,
            damage=self.PLAYER_BOMB_DAMAGE, owner="player", is_bomb=True,
            explosion_source=self._player_explosion_path,
            spawn_under=self.player_ship, facing_angle=self._facing_angle,
        )
        self.bomb_btn.start_cooldown(self.PLAYER_BOMB_COOLDOWN)

    # ------------------------------------------------------------
    # ENEMIES
    # ------------------------------------------------------------

    def _spawn_enemies(self, dt):
        self._spawn_timer -= dt
        if self._spawn_timer > 0 or len(self.enemies) >= self.ENEMY_MAX_CONCURRENT:
            return
        self._spawn_timer = self.ENEMY_SPAWN_INTERVAL

        enemy_def = random.choice(ENEMY_DEFS)
        size = min(Window.width, Window.height) * 0.16
        margin = 60
        edge = random.choice(["left", "right", "top", "bottom"])
        if edge == "left":
            sx, sy = -margin, random.uniform(0, Window.height)
        elif edge == "right":
            sx, sy = Window.width + margin, random.uniform(0, Window.height)
        elif edge == "top":
            sx, sy = random.uniform(0, Window.width), Window.height + margin
        else:
            sx, sy = random.uniform(0, Window.width), -margin

        world_x = sx + self.camera_x
        world_y = sy + self.camera_y

        enemy = EnemyShip(
            enemy_def=enemy_def, size=(size, size), pos=(world_x, world_y),
            health=self.ENEMY_HEALTH,
        )
        self.enemies.append(enemy)
        self.add_widget(enemy)

    def _move_enemies(self, dt):
        pcx = self.player_ship.world_x + self.player_ship.width / 2
        pcy = self.player_ship.world_y + self.player_ship.height / 2

        for e in self.enemies:
            ecx = e.world_x + e.width / 2
            ecy = e.world_y + e.height / 2
            dist = math.hypot(pcx - ecx, pcy - ecy)

            if e.state == "wander" and dist <= self.ENEMY_DETECT_RADIUS:
                e.state = "chase"
            elif e.state == "chase" and dist >= self.ENEMY_LOSE_RADIUS:
                e.state = "wander"
                e.wander_angle = random.uniform(0, 360)
                e.wander_timer = 0.0

            if e.state == "chase":
                if dist > 0:
                    dx = (pcx - ecx) / dist
                    dy = (pcy - ecy) / dist
                else:
                    dx = dy = 0
                e.world_x += dx * self.ENEMY_CHASE_SPEED * dt
                e.world_y += dy * self.ENEMY_CHASE_SPEED * dt
            else:
                e.wander_timer -= dt
                if e.wander_timer <= 0:
                    e.wander_angle = random.uniform(0, 360)
                    e.wander_timer = random.uniform(1.5, 3.0)
                rad = math.radians(e.wander_angle)
                e.world_x += math.cos(rad) * self.ENEMY_WANDER_SPEED * dt
                e.world_y += math.sin(rad) * self.ENEMY_WANDER_SPEED * dt

            e.world_x = max(0, min(e.world_x, self.world_width - e.width))
            e.world_y = max(0, min(e.world_y, self.world_height - e.height))

    def _handle_enemy_shooting(self, dt):
        pcx = self.player_ship.world_x + self.player_ship.width / 2
        pcy = self.player_ship.world_y + self.player_ship.height / 2

        for e in self.enemies:
            e.shoot_timer -= dt
            e.bomb_timer -= dt

            ecx = e.world_x + e.width / 2
            ecy = e.world_y + e.height / 2
            dist = math.hypot(pcx - ecx, pcy - ecy)

            if e.state == "chase" and dist <= self.ENEMY_SHOOT_RANGE and e.shoot_timer <= 0:
                e.shoot_timer = self.ENEMY_SHOOT_COOLDOWN + random.uniform(-0.4, 0.4)
                self._spawn_projectile_aimed(
                    shooter_world_center=(ecx, ecy), target_world_center=(pcx, pcy),
                    source=e.enemy_def["bullet"], speed=self.ENEMY_BULLET_SPEED,
                    damage=self.ENEMY_BULLET_DAMAGE, owner="enemy", is_bomb=False,
                    explosion_source=e.enemy_def["explosion"], spawn_under=None,
                )

            if (e.state == "chase" and e.enemy_def["bomb"]
                    and dist <= self.ENEMY_BOMB_RANGE and e.bomb_timer <= 0):
                e.bomb_timer = self.ENEMY_BOMB_COOLDOWN + random.uniform(-0.5, 0.5)
                self._spawn_projectile_aimed(
                    shooter_world_center=(ecx, ecy), target_world_center=(pcx, pcy),
                    source=e.enemy_def["bomb"], speed=self.ENEMY_BOMB_SPEED,
                    damage=self.ENEMY_BOMB_DAMAGE, owner="enemy", is_bomb=True,
                    explosion_source=e.enemy_def["explosion"], spawn_under=e,
                )

    # ------------------------------------------------------------
    # BULLETS / EXPLOSIONS / COLLISIONS
    # ------------------------------------------------------------

    def _move_bullets(self, dt):
        for b in list(self.bullets):
            b.update(dt)
            if b.is_off_view(self.camera_x, self.camera_y, Window.width, Window.height):
                self.bullets.remove(b)
                self.remove_widget(b)

    def _spawn_explosion(self, source, world_center):
        if not source:
            return
        size = min(Window.width, Window.height) * self.EXPLOSION_SIZE_RATIO
        explosion = Explosion(
            source=source, world_center=world_center, size=(size, size),
            on_finished=self._on_explosion_finished,
        )
        self.explosions.append(explosion)
        self.add_widget(explosion)

    def _on_explosion_finished(self, explosion):
        if explosion in self.explosions:
            self.explosions.remove(explosion)
        if explosion.parent:
            self.remove_widget(explosion)

    def _check_collisions(self):
        # player projectiles vs enemies
        for b in list(self.bullets):
            if b.owner != "player":
                continue
            for e in list(self.enemies):
                if b.collide_widget(e):
                    dead = e.take_damage(b.damage)
                    if b.is_bomb:
                        self._spawn_explosion(
                            b.explosion_source,
                            (b.world_x + b.width / 2, b.world_y + b.height / 2),
                        )
                        # explosion sound: ONLY when a player bomb
                        # hits an enemy, per spec
                        audio_manager.play_explosion_sfx()
                    if b in self.bullets:
                        self.bullets.remove(b)
                        self.remove_widget(b)
                    if dead:
                        self.enemies.remove(e)
                        self.remove_widget(e)
                        self._kills += 1
                    break

        # enemy projectiles vs player
        for b in list(self.bullets):
            if b.owner != "enemy":
                continue
            if b.collide_widget(self.player_ship):
                self._apply_player_damage(b.damage)
                if b.is_bomb:
                    self._spawn_explosion(
                        b.explosion_source,
                        (b.world_x + b.width / 2, b.world_y + b.height / 2),
                    )
                self.bullets.remove(b)
                self.remove_widget(b)

        # enemy contact damage
        for e in self.enemies:
            e.contact_timer -= 1.0 / 60.0
            if e.collide_widget(self.player_ship) and e.contact_timer <= 0:
                e.contact_timer = self.ENEMY_CONTACT_COOLDOWN
                self._apply_player_damage(self.ENEMY_CONTACT_DAMAGE)

    def _apply_player_damage(self, amount):
        if self._player_armour > 0:
            absorbed = min(self._player_armour, amount)
            self._player_armour -= absorbed
            amount -= absorbed
        if amount > 0:
            self._player_health -= amount

    # ------------------------------------------------------------
    # UI
    # ------------------------------------------------------------

    def _update_health_ui(self):
        self.hud_icon.update_health(max(0, self._player_health), self.PLAYER_MAX_HEALTH)

    def _update_armour_ui(self):
        self.hud_icon.update_armour(max(0, self._player_armour), self.PLAYER_MAX_ARMOUR)

    def _update_timer_ui(self):
        self.hud_icon.update_timer(self._elapsed)

    def _update_kills_ui(self):
        self.hud_icon.update_kills(self._kills)

    def _show_fading_text(self, text):
        lbl = Label(
            text=f"[b]{text}[/b]", markup=True, font_size="34sp",
            color=(1, 1, 1, 1), size_hint=(None, None),
            size=(Window.width * 0.9, 80),
            pos=(Window.width * 0.05, Window.height * 0.55),
            halign="center", valign="middle",
        )
        lbl.bind(size=lambda i, v: setattr(i, "text_size", v))
        self.add_widget(lbl)

        def start_fade(dt):
            anim = Animation(opacity=0, duration=1.2)
            anim.bind(on_complete=lambda *a: self._remove_if_present(lbl))
            anim.start(lbl)

        Clock.schedule_once(start_fade, 1.4)

    def _remove_if_present(self, widget):
        if widget.parent:
            self.remove_widget(widget)

    def _check_mission_complete(self):
        if not self._mission_won_shown and self._kills >= KILLS_NEEDED:
            self._mission_won_shown = True
            self._show_fading_text("Mission Complete — You Won!")

        if not self._mission_over and self._player_health <= 0:
            self._end_mission("Mission Failed", "Your ship has been destroyed.")

    def _end_mission(self, title, message):
        self._mission_over = True
        self._active = False
        audio_manager.stop_movement_sfx()

        box = MessageBox(width_hint=0.72, height_hint=0.5)
        title_lbl = Label(
            text=f"[b]{title}[/b]", markup=True, font_size="22sp",
            size_hint_y=None, height=32, color=(1, 1, 1, 1),
        )
        box.content_area.add_widget(title_lbl)

        msg_lbl = Label(
            text=message, font_size="16sp", color=(1, 1, 1, 1), halign="center",
        )
        msg_lbl.bind(width=lambda i, w: setattr(i, "text_size", (w, None)))
        box.content_area.add_widget(msg_lbl)

        spacer = BoxLayout(size_hint_y=1)
        box.content_area.add_widget(spacer)

        home_btn = IconButton(
            source=BTN_HOME_ICON,
            size_hint=(None, None), size=(180, 60),
            pos_hint={"center_x": 0.5},
            on_release_action=self._on_home_pressed,
        )
        box.content_area.add_widget(home_btn)

        box.open_on(self)