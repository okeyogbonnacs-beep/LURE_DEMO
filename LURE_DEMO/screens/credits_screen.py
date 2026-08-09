# screens/credits_screen.py

from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.app import App

from config import BG_CREDITS, BTN_BACK
from widgets.icon_button import IconButton


CREDITS_TEXT = """
LURE

Version 1.0 Demo

A Game By

001 Productions

================================================
CREDITS

FOUNDER

Ogbonna

================================================
CREATED BY

001 Productions

================================================
GAME DESIGN

Game Concept

Core Gameplay

Mission Structure

Gameplay Systems

Enemy Behaviour

Progression Design

Player Progression

Difficulty Planning

User Interface Planning

Visual Direction

Creative Direction

Game Flow

Overall Vision

Designed By

001 Productions

================================================
PROGRAMMING

Programming Assistance

Claude AI

Programming Integration

001 Productions

================================================
ART DIRECTION

Retro Futuristic Art Direction

Spacecraft Visual Direction

Enemy Visual Direction

Environment Direction

Background Planning

User Interface Direction

Visual Consistency

Asset Integration

Creative Direction

001 Productions

================================================
AUDIO

Music

FLOATIN'

BOY Đ LYK STRESS

VVS

DON'T GIVE ME THAT GREEN LYT

Generated Using

Suno

Sound Effects

Integrated By

001 Productions

================================================
GAMEPLAY TESTING

Gameplay Testing

System Testing

Bug Testing

Performance Testing

User Interface Testing

Balance Testing

Mission Testing

Quality Assurance

001 Productions

================================================
TECHNICAL DEVELOPMENT

Python

Kivy

Pydroid 3

GitHub

Claude AI

================================================
SPECIAL THANKS

Python Community

Kivy Community

Open Source Community

Game Development Community

Independent Developers

Artists

Musicians

Everyone Who Shares Knowledge

Everyone Supporting Independent Game Development

Every Player Who Tested The Demo

Everyone Who Gives Feedback

Friends And Family For Their Support

================================================
ABOUT LURE

LURE is a tactical mission based science fiction game focused on strategy, positioning, and intelligent decision making.

Players must carefully complete objectives, survive dangerous encounters, and use tactical thinking instead of relying only on direct combat.

Every mission has been designed to encourage planning, observation, and creative problem solving.

================================================
AI DEVELOPMENT DISCLOSURE

Programming for this project was created with assistance from Claude AI.

Claude AI assisted with programming during development.

All gameplay ideas, project planning, game systems, mechanics, user interface planning, visual direction, feature planning, implementation decisions, balancing, testing, and overall creative direction were completed by 001 Productions.

All final development decisions were made by 001 Productions.

================================================
SOFTWARE AND TECHNOLOGY

Python

Kivy

Pydroid 3

GitHub

Claude AI

Suno

================================================
MESSAGE FROM THE DEVELOPER

Thank you for taking the time to play the LURE Demo.

This project represents countless hours of planning, experimentation, learning, problem solving, testing, and continuous improvement.

Every system, mechanic, visual element, and design decision has been carefully considered to create a unique tactical science fiction experience.

This demo is only the beginning.

Future updates will continue expanding the LURE universe with new gameplay systems, missions, ships, enemies, visual improvements, music, and additional content.

Your feedback, encouragement, and support help shape the future of this project.

Thank you for believing in independent game development.

Thank you for being part of this journey.

================================================
COPYRIGHT

LURE

Copyright 2026

001 Productions

All Rights Reserved.

================================================
001 PRODUCTIONS

Creating Games

Creating Game Assets

Building Creative Software

Learning

Improving

Creating

One Project At A Time

Thank You For Playing

See You In The Next Mission

END OF CREDITS
"""


class CreditsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)

        bg = Image(
            source=BG_CREDITS,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
        )
        self.root_layout.add_widget(bg)

        # Dark overlay so text is readable over the background
        with self.root_layout.canvas.before:
            Color(0, 0, 0, 0.45)
            self._overlay = Rectangle(
                pos=self.root_layout.pos,
                size=self.root_layout.size,
            )
        self.root_layout.bind(
            pos=lambda inst, val: setattr(self._overlay, "pos", val),
            size=lambda inst, val: setattr(self._overlay, "size", val),
        )

        # Back button
        self.back_btn = IconButton(
            source=BTN_BACK,
            size_hint=(0.197, 0.3066),
            pos_hint={"x": 0.0282, "top": 1.0565},
            on_release_action=self._on_back_pressed,
        )
        self.root_layout.add_widget(self.back_btn)

        # Scrollable credits text
        self.scroll = ScrollView(
            size_hint=(0.88, 0.80),
            pos_hint={"center_x": 0.5, "y": 0.04},
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=4,
        )
        self.root_layout.add_widget(self.scroll)

        content = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=(0, 20),
        )
        content.bind(minimum_height=content.setter("height"))

        self.credits_label = Label(
            text=CREDITS_TEXT,
            font_size="15sp",
            halign="center",
            valign="top",
            color=(1, 1, 1, 1),
            size_hint_y=None,
            markup=False,
        )
        self.credits_label.bind(
            width=lambda inst, w: setattr(inst, "text_size", (w, None))
        )
        self.credits_label.bind(
            texture_size=lambda inst, ts: setattr(inst, "height", ts[1])
        )
        content.add_widget(self.credits_label)
        self.scroll.add_widget(content)

    def _on_back_pressed(self):
        App.get_running_app().navigate_to("menu")