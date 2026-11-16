import hashlib
import os
from datetime import datetime

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

# Темний фон вікна за замовчуванням
Window.clearcolor = (0.08, 0.09, 0.12, 1)


class RoundedButton(Button):
    """Сучасна кнопка із закругленими кутами та ефектом натискання."""

    def __init__(self, bg_color=(0.15, 0.45, 0.85, 1), radius=dp(14), **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.default_color = bg_color
        self.pressed_color = (
            bg_color[0] * 0.75,
            bg_color[1] * 0.75,
            bg_color[2] * 0.75,
            bg_color[3],
        )
        self.radius = [radius]

        with self.canvas.before:
            self.color_instruction = Color(*self.default_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=self.radius)

        self.bind(pos=self.update_graphics, size=self.update_graphics, state=self.on_state_change)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_state_change(self, instance, value):
        if not self.disabled:
            self.color_instruction.rgba = self.pressed_color if value == 'down' else self.default_color


class PasswordApp(App):

    def build(self):
        self.current_password = ''
        root = FloatLayout()

        # 1. Фонове зображення на повну яскравість (opacity=1.0)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_dir, 'background.png')

        if os.path.exists(bg_path):
            bg_image = Image(
                source=bg_path,
                allow_stretch=True,
                keep_ratio=True,
                opacity=1.0,
            )
            root.add_widget(bg_image)

        # 2. Основний контейнер
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(25), dp(100), dp(25), dp(40)],
            spacing=dp(20),
        )

        # Картка з паролем
        card = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        with card.canvas.before:
            Color(0.05, 0.06, 0.08, 0.40)
            self.card_rect = RoundedRectangle(radius=[dp(20)])
        card.bind(pos=self.update_card, size=self.update_card)

        self.status_label = Label(
            text='Денний код доступу',
            font_size=sp(24),
            bold=True,
            color=(0.95, 0.96, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.4),
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))

        self.password_label = Label(
            text='••••••',
            font_size=sp(38),
            bold=True,
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint=(1, 0.6),
        )
        self.password_label.bind(size=self.password_label.setter('text_size'))

        card.add_widget(self.status_label)
        card.add_widget(self.password_label)

        # Кнопка генерації
        self.gen_btn = RoundedButton(
            text='Отримати пароль',
            font_size=sp(19),
            bold=True,
            size_hint=(1, None),
            height=dp(58),
            bg_color=(0.16, 0.48, 0.96, 1),
        )
        self.gen_btn.bind(on_press=self.generate_password)

        # Кнопка копіювання
        self.copy_btn = RoundedButton(
            text='Скопіювати код',
            font_size=sp(17),
            size_hint=(1, None),
            height=dp(52),
            bg_color=(0.2, 0.65, 0.45, 1),
            disabled=True,
            opacity=0.4,
        )
        self.copy_btn.bind(on_press=self.copy_password)

        main_layout.add_widget(card)
        main_layout.add_widget(self.gen_btn)
        main_layout.add_widget(self.copy_btn)

        # 3. Велика кнопка закриття у правому верхньому куті
        close_btn = RoundedButton(
            text='X',
            font_size=sp(26),
            bold=True,
            size_hint=(None, None),
            size=(dp(60), dp(60)),
            pos_hint={'right': 0.96, 'top': 0.98},
            bg_color=(0.85, 0.25, 0.25, 0.95),
            radius=dp(30),
        )
        close_btn.bind(on_press=self.stop)

        root.add_widget(main_layout)
        root.add_widget(close_btn)

        return root

    def update_card(self, instance, value):
        self.card_rect.pos = instance.pos
        self.card_rect.size = instance.size

    def generate_password(self, instance):
        date_str = datetime.now().strftime('%d.%m.%Y')
        raw_string = f'{date_str}_бонус'
        hashed = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

        self.current_password = hashed[:6].upper()
        self.password_label.text = self.current_password
        self.status_label.text = f'Денний код доступу\nна {date_str}'

        self.copy_btn.disabled = False
        self.copy_btn.opacity = 1.0

    def copy_password(self, instance):
        if self.current_password:
            Clipboard.copy(self.current_password)
            self.copy_btn.text = 'Скопійовано в буфер!'
            Clock.schedule_once(self.reset_copy_btn, 2)

    def reset_copy_btn(self, dt):
        self.copy_btn.text = 'Скопіювати код'


if __name__ == '__main__':
    PasswordApp().run()
