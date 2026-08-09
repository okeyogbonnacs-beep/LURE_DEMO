# screens/tasks_window.py

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView

from widgets.message_box import MessageBox
from widgets.icon_button import IconButton
from save_manager import save_manager
from config import BTN_CLAIM  # reusing a button-style asset as a stand-in Claim graphic


# ------------------------------------------------------------
# HARDCODED DEMO TASK DATA
# ------------------------------------------------------------

DEMO_TASKS = [
    {
        "id": "kill_30_enemies",
        "name": "Kill 30 Enemies",
        "description": "Defeat 30 enemies across any missions.",
        "progress": 0.45,
        "reward_gold": 200,
    },
    {
        "id": "survive_low_hp",
        "name": "Steady Hands",
        "description": "Don't drop below 40% HP in your next 5 games.",
        "progress": 0.20,
        "reward_gold": 150,
    },
    {
        "id": "complete_1_match",
        "name": "First Flight",
        "description": "Complete 1 match.",
        "progress": 1.0,
        "reward_gold": 100,
    },
]


class TaskRow(BoxLayout):
    """
    A single task entry: name, description, progress bar, percentage,
    and a Claim button that is only enabled once progress reaches 100%.
    """

    def __init__(self, task_data, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=150, spacing=6, **kwargs)

        self.task_data = task_data
        self._claimed = False

        self.name_label = Label(
            text=f"[b]{task_data['name']}[/b]",
            markup=True,
            font_size="20sp",
            size_hint_y=None,
            height=30,
            halign="left",
            valign="middle",
            color=(1, 1, 1, 1),
        )
        self.name_label.bind(size=self._sync_text_size)
        self.add_widget(self.name_label)

        self.desc_label = Label(
            text=task_data["description"],
            font_size="15sp",
            size_hint_y=None,
            height=40,
            halign="left",
            valign="top",
            color=(0.85, 0.85, 0.85, 1),
        )
        self.desc_label.bind(size=self._sync_text_size)
        self.add_widget(self.desc_label)

        progress_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=30, spacing=10)

        self.progress_bar = ProgressBar(
            max=1.0,
            value=task_data["progress"],
            size_hint_x=0.75,
        )
        progress_row.add_widget(self.progress_bar)

        self.percent_label = Label(
            text=f"{int(task_data['progress'] * 100)}%",
            font_size="15sp",
            size_hint_x=0.25,
            color=(1, 1, 1, 1),
        )
        progress_row.add_widget(self.percent_label)

        self.add_widget(progress_row)

        is_complete = task_data["progress"] >= 1.0

        self.claim_btn = IconButton(
            source=BTN_CLAIM,
            size_hint=(None, None),
            size=(200, 62),
            pos_hint={"center_x": 0.5},
            disabled=not is_complete,
            opacity=1.0 if is_complete else 0.4,
            on_release_action=self._on_claim,
        )
        self.add_widget(self.claim_btn)

    def _sync_text_size(self, instance, value):
        instance.text_size = value

    def _on_claim(self):
        if self._claimed:
            return
        if self.task_data["progress"] < 1.0:
            return

        self._claimed = True
        save_manager.add_gold(self.task_data["reward_gold"])

        self.claim_btn.disabled = True
        self.claim_btn.opacity = 0.4
        self.name_label.text = f"[b]{self.task_data['name']} (Claimed)[/b]"


class TasksWindow(MessageBox):
    """
    MessageBox subclass showing the demo task list.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        title = Label(
            text="[b]Tasks[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=None,
            height=36,
            color=(1, 1, 1, 1),
        )
        self.content_area.add_widget(title)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        task_list = BoxLayout(orientation="vertical", size_hint_y=None, spacing=12, padding=(0, 6))
        task_list.bind(minimum_height=task_list.setter("height"))

        for task_data in DEMO_TASKS:
            row = TaskRow(task_data)
            task_list.add_widget(row)

        scroll.add_widget(task_list)
        self.content_area.add_widget(scroll)