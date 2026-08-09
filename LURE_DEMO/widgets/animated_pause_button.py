# widgets/animated_pause_button.py

from kivy.clock import Clock

from config import BTN_PAUSE, PAUSE_BTN_ANI_FRAMES
from widgets.icon_button import IconButton


class AnimatedPauseButton(IconButton):
    """
    Pause button that idles on BTN_PAUSE, then every IDLE_SECONDS plays
    through PAUSE_BTN_ANI_FRAMES once and returns to idle - repeating
    forever. Remains fully clickable while animating (IconButton's
    press/release behavior is untouched).
    """

    FRAME_DURATION = 0.06  # seconds per animation frame
    IDLE_SECONDS = 3.0

    def __init__(self, **kwargs):
        kwargs["source"] = BTN_PAUSE
        super().__init__(**kwargs)
        self._frame_index = 0
        self._anim_event = None
        self._idle_event = None
        self._schedule_idle_then_play()

    def _schedule_idle_then_play(self):
        if self._idle_event:
            self._idle_event.cancel()
        self._idle_event = Clock.schedule_once(self._play_animation, self.IDLE_SECONDS)

    def _play_animation(self, dt=None):
        self._frame_index = 0
        if self._anim_event:
            self._anim_event.cancel()
        self._anim_event = Clock.schedule_interval(self._advance_frame, self.FRAME_DURATION)

    def _advance_frame(self, dt):
        if self._frame_index >= len(PAUSE_BTN_ANI_FRAMES):
            self._anim_event.cancel()
            self._anim_event = None
            self.source = BTN_PAUSE  # back to idle art
            self._schedule_idle_then_play()
            return
        self.source = PAUSE_BTN_ANI_FRAMES[self._frame_index]
        self._frame_index += 1

    def stop_animation(self):
        if self._anim_event:
            self._anim_event.cancel()
            self._anim_event = None
        if self._idle_event:
            self._idle_event.cancel()
            self._idle_event = None