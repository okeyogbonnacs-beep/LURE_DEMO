# audio_manager.py

import random

from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import StringProperty

from config import SONG_FILES, SFX_BUTTON, SFX_MOVEMENT, SFX_SHOOTING, SFX_EXPLOSION


class AudioManager(EventDispatcher):
    """
    Handles all background music (shuffle-bag, no-repeat-until-exhausted)
    and sound effects for the whole app.
    """

    current_song_name = StringProperty("")

    __events__ = ("on_new_song",)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._song_paths = list(SONG_FILES)
        self._bag = []
        self._current_sound = None
        self._current_path = None

        self._music_enabled = True
        self._paused_for_gameplay = False

        self._sfx_cache = {}
        self._movement_playing = False

        self._sfx_paths = {
            "button": SFX_BUTTON,
            "movement": SFX_MOVEMENT,
            "shooting": SFX_SHOOTING,
            "explosion": SFX_EXPLOSION,
        }

        self._preload_sfx()

    # --------------------------------------------------------
    # SFX
    # --------------------------------------------------------

    def _preload_sfx(self):
        self._sfx_cache["button"] = SoundLoader.load(SFX_BUTTON)
        self._sfx_cache["movement"] = SoundLoader.load(SFX_MOVEMENT)
        self._sfx_cache["shooting"] = SoundLoader.load(SFX_SHOOTING)

    def play_sfx(self, name):
        """Single-instance SFX: stops any previous play of this sound
        before restarting it. Fine for button clicks (one at a time)
        but NOT for rapid-fire sounds like shooting - use
        play_overlapping_sfx for those instead."""
        sound = self._sfx_cache.get(name)
        if sound:
            sound.stop()
            sound.play()

    def play_button_sfx(self):
        self.play_sfx("button")

    def play_overlapping_sfx(self, name):
        """Loads and plays a fresh, independent Sound instance each
        call, so multiple rapid triggers (e.g. fast bullets, several
        explosions at once) layer on top of each other instead of
        cutting each other off. Used for shooting and explosion SFX."""
        path = self._sfx_paths.get(name)
        if not path:
            return
        sound = SoundLoader.load(path)
        if sound is None:
            print(f"[AudioManager] Failed to load SFX: {path}")
            return
        sound.play()

    def play_shoot_sfx(self):
        self.play_overlapping_sfx("shooting")

    def play_explosion_sfx(self):
        self.play_overlapping_sfx("explosion")

    def start_movement_sfx(self):
        sound = self._sfx_cache.get("movement")
        if sound and not self._movement_playing:
            sound.loop = True
            sound.play()
            self._movement_playing = True

    def stop_movement_sfx(self):
        sound = self._sfx_cache.get("movement")
        if sound and self._movement_playing:
            sound.stop()
            self._movement_playing = False

    # --------------------------------------------------------
    # MUSIC - SHUFFLE BAG
    # --------------------------------------------------------

    def _refill_bag(self):
        self._bag = list(self._song_paths)
        random.shuffle(self._bag)

    def start_music(self):
        if self._current_sound is not None:
            return
        if not self._bag:
            self._refill_bag()
        self._play_next_in_bag()

    def _play_next_in_bag(self):
        if not self._music_enabled:
            return

        if not self._bag:
            self._refill_bag()

        next_path = self._bag.pop(0)
        self._start_song(next_path)

    def _start_song(self, path):
        if self._current_sound is not None:
            self._current_sound.unbind(on_stop=self._on_song_finished)
            self._current_sound.stop()

        sound = SoundLoader.load(path)
        if sound is None:
            print(f"[AudioManager] Failed to load song: {path}")
            Clock.schedule_once(lambda dt: self._play_next_in_bag(), 0)
            return

        self._current_sound = sound
        self._current_path = path
        sound.bind(on_stop=self._on_song_finished)
        sound.play()

        song_name = self._extract_song_name(path)
        self.current_song_name = song_name
        self.dispatch("on_new_song", song_name)

    def _extract_song_name(self, path):
        import os
        name = os.path.basename(path)
        name = os.path.splitext(name)[0]
        return name

    def _on_song_finished(self, sound):
        if not self._music_enabled or self._paused_for_gameplay:
            return
        Clock.schedule_once(lambda dt: self._play_next_in_bag(), 0)

    def on_new_song(self, song_name):
        pass

    # --------------------------------------------------------
    # GAMEPLAY MUSIC PAUSE / RESUME
    # --------------------------------------------------------

    def is_paused_for_gameplay(self):
        return self._paused_for_gameplay

    def pause_for_gameplay(self):
        """Called when entering the Gameplay screen. Stops music, keeps SFX."""
        self._paused_for_gameplay = True
        self._music_enabled = False
        if self._current_sound is not None:
            self._current_sound.unbind(on_stop=self._on_song_finished)
            self._current_sound.stop()

    def resume_after_gameplay(self):
        """Called when leaving Gameplay, OR when the pause overlay is
        shown (so music plays while paused)."""
        self._paused_for_gameplay = False
        self._music_enabled = True
        self._play_next_in_bag()

    # --------------------------------------------------------
    # VOLUME
    # --------------------------------------------------------

    def set_volume(self, volume):
        if self._current_sound is not None:
            self._current_sound.volume = volume
        for sound in self._sfx_cache.values():
            if sound:
                sound.volume = volume


audio_manager = AudioManager()