import sqlite3
import openai
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.properties import StringProperty

Config.set('graphics', 'backend', 'sdl2')

openai.api_key = "API"

Builder.load_string('''
<StartScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Soy estudiante de ingeniería en desarrollo de software, este es un proyecto personal, espero que les guste."
        Label:
            text: "Ingrese su nombre de usuario:"
        TextInput:
            id: username_input
            multiline: False
        Button:
            text: "Ingresar"
            on_press: app.iniciar_chat(username_input.text)

<DefaultScreen>:
    BoxLayout:
        id: box_layout
        orientation: 'vertical'
        padding: [10, 10, 10, 10]
        Image:
            source: 'background.jpg'
            size_hint: 1, 1
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        Label:
            id: welcome_label
            text: ""
            size_hint_y: None
            height: dp(40)

        ScrollView:
            Label:
                id: chat_history_label
                text: app.chat_history
                size_hint_y: None
                height: self.texture_size[1]
                height_hint: 1.0
        BoxLayout:
            size_hint_y: None
            height: dp(40)
            TextInput:
                id: entrada_usuario
                multiline: False
                size_hint_x: 0.5
            Button:
                id: enviar_button
                text: "Enviar"
                size_hint_x: 0.5
                on_press: app.enviar_mensaje(entrada_usuario.text)
''')

class StartScreen(Screen):
    pass

class DefaultScreen(Screen):
    pass

class ChatbotApp(App):
    conn = None
    current_user = None
    chat_history = StringProperty("")

    def build(self):
        if platform == 'android':
            Config.set('graphics', 'width', '360')
            Config.set('graphics', 'height', '640')
            Window.size = (360, 640)
        screen_manager = ScreenManager()
        start_screen = StartScreen(name='start')
        default_screen = DefaultScreen(name='default')
        screen_manager.add_widget(start_screen)
        screen_manager.add_widget(default_screen)

        self.conn = sqlite3.connect(':memory:')
        self.create_table()

        return screen_manager

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history
                          (id INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT,
                           message TEXT)''')
        self.conn.commit()

    def iniciar_chat(self, username):
        app = App.get_running_app()
        app.root.current = 'default'
        app.root.get_screen('default').ids.welcome_label.text = f"Bienvenido, {username}!"
        self.current_user = username

    def enviar_mensaje(self, mensaje):
        entrada_usuario = self.root.get_screen('default').ids.entrada_usuario
        mensaje = entrada_usuario.text.strip()
        entrada_usuario.text = ""

        if mensaje:
            self.guardar_mensaje(mensaje, self.current_user)
            respuesta = self.obtener_respuesta(mensaje)
            self.guardar_mensaje(respuesta, "Chatbot")

        self.update_chat_history()

    def guardar_mensaje(self, mensaje, usuario):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO chat_history (username, message)
                          VALUES (?, ?)''', (usuario, mensaje))
        self.conn.commit()

    def obtener_respuesta(self, mensaje):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=mensaje,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].text.strip()

    def update_chat_history(self):
        cursor = self.conn.cursor()
        cursor.execute('''SELECT * FROM chat_history ORDER BY id''')
        rows = cursor.fetchall()

        chat_history = ""
        for row in rows:
            username = row[1]
            message = row[2]
            chat_history += f"{username}: {message}\n"

        self.chat_history = chat_history

    def on_chat_history(self, instance, value):
        chat_history_label = self.root.get_screen('default').ids.chat_history_label
        chat_history_label.text = value
        chat_history_label.height = chat_history_label.texture_size[1]

if __name__ == "__main__":
    ChatbotApp().run()
