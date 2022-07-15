# Client for the server
from importlib.util import set_loader
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import time
import os
import cv2, imutils, socket
import numpy as np
import time
import base64
from re import L
import Chat_Client
import sys

# Login Page
class ConnectPage(GridLayout):
    # runs on initialization
    def __init__(self, **kwargs):
        # we want to run __init__ of both ConnectPage AAAAND GridLayout
        super().__init__(**kwargs)

        self.cols = 2  # used for our grid

        # Adding the Padding and Spacing
        self.padding = [30, 30, 30, 30]
        self.spacing = [30, 30]

        # reading the previous user information
        if os.path.isfile("prev_details.txt"):
            with open("prev_details.txt", "r") as f:
                prev_details = f.read()
                prev_details = prev_details.split(",")
                ip = prev_details[0]
                port = prev_details[1]
                username = prev_details[2]
        else:
            ip = ""
            port = ""
            username = ""

        # widgets added in order of appearance
        self.add_widget(Label(text="IP :"))  # widget #1, top left
        self.ip = TextInput(text=ip, multiline=False)  # defining self.ip...
        self.add_widget(self.ip)  # widget #2, top right

        self.add_widget(Label(text="Port :"))
        self.port = TextInput(text=port, multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text="Username :"))
        self.username = TextInput(text=username, multiline=False)
        self.add_widget(self.username)

        # Adding the Login Button

        self.join = Button(text="Join")
        self.join.bind(on_press=self.join_button)
        self.add_widget(Label())
        self.add_widget(self.join)

    def join_button(self, instance):
        # get the text from the textinputs
        ip = self.ip.text
        port = self.port.text
        username = self.username.text
        # Logging the user info
        with open("log.txt", "a") as f:
            f.write(
                f"{time.strftime('%m/%d/%Y, %H:%M:%S', time.localtime())}--> 'Attempting to join {ip}:{port} as {username}'"
                + "\n"
            )
        # previous user information
        with open("prev_details.txt", "w") as f:
            f.write(f"{ip},{port},{username}")
        # print(f'Attempting to join {ip}:{port} as {username}')
        info = [f"Joining {ip}:{port} as {username}", f"{ip},{port},{username}"]
        chat_app.info_page.update_info(info)
        chat_app.screen_manager.current = "Info"
        Clock.schedule_once(self.connect, 1)

    def connect(self, _):
        BUFF_SIZE = 65536
        port = int(self.port.text)
        ip = self.ip.text
        username = self.username.text
        chat_app.create_chat_page()
        chat_app.screen_manager.current = "Chat"


class InfoPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 1

        self.message = Label(halign="center", valign="middle", font_size=30)

        self.message.bind(width=self.update_text_width)

        self.add_widget(self.message)

    def update_info(self, message):
        self.message.text = message[0]

    def update_text_width(self, *_):
        self.message.text_size = (self.message.width * 0.9, None)


class ScrollableLabel(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = GridLayout(cols=1, size_hint_y=None)
        self.add_widget(self.layout)
        self.chat_history = Label(size_hint_y=None, markup=True)
        self.scroll_to_point = Label()
        self.layout.add_widget(self.chat_history)
        self.layout.add_widget(self.scroll_to_point)

    def update_chat_history(self, message):

        self.chat_history.text += "\n" + message
        self.layout.height = self.chat_history.texture_size[1] + 15
        self.chat_history.height = self.chat_history.texture_size[1]
        self.chat_history.text_size = (self.chat_history.width * 0.98, None)
        self.scroll_to(self.scroll_to_point)


class ChatPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 2
        self.rows = 2
        self.BUFF_SIZE = 65536
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE
        )
        self.img1 = Image()

        obj = ConnectPage()
        self.port = obj.port.text
        self.host_ip = obj.ip.text
        username = obj.username.text
        username_ = bytes(username, "utf-8")

        self.client_socket.sendto(username_, (self.host_ip, int(self.port)))
        self.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)

        self.history = ScrollableLabel(height=Window.size[1] * 0.9, size_hint_y=None)
        self.add_widget(self.history)

        self.new_message = TextInput(
            width=(Window.size[0] * 0.8) / 2, size_hint_x=None, multiline=False
        )
        self.send = Button(text="Send")
        self.send.bind(on_press=self.send_message)

        bottom_line = GridLayout(cols=2)
        bottom_line.add_widget(self.new_message)
        bottom_line.add_widget(self.send)
        self.add_widget(bottom_line)

        Window.bind(on_key_down=self.on_key_down)

        Clock.schedule_once(self.focus_text_input, 1)
        Chat_Client.connect(obj.ip.text, int(obj.port.text) - 1, username, show_error)
        Chat_Client.start_listening(self.incoming_message, show_error)

    def update(self, dt):
        packet, _ = self.client_socket.recvfrom(self.BUFF_SIZE)
        data = base64.b64decode(packet, " /")
        npdata = np.fromstring(data, dtype=np.uint8)
        frame = cv2.imdecode(npdata, 1)
        frame1 = cv2.flip(frame, 0)
        buf = frame1.tostring()
        texture1 = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture1.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.img1.texture = texture1

    def send_message(self, _):
        print("Message snt")
        message = self.new_message.text
        self.new_message.text = ""
        if message:
            # Our messages - use red color for the name
            self.history.update_chat_history(
                f"[color=dd2020]{chat_app.connect_page.username.text}[/color] > {message}"
            )
            Chat_Client.send(message)
        Clock.schedule_once(self.focus_text_input, 0.1)

    def on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:
            self.send_message(None)

    def focus_text_input(self, _):
        self.new_message.focus = True

    def incoming_message(self, username, message):
        # Update chat history with username and message, green color for username
        self.history.update_chat_history(
            f"[color=20dd20]{username}[/color] > {message}"
        )


class Epic(App):
    def build(self):
        # Adding Screen Manager to Handle Multiple Displays
        self.screen_manager = ScreenManager()

        # Adding Screens to the Screen Manager
        self.connect_page = ConnectPage()
        screen = Screen(name="Connect")
        screen.add_widget(self.connect_page)
        self.screen_manager.add_widget(screen)
 
        # Info Page
        self.info_page = InfoPage()
        screen = Screen(name="Info")
        screen.add_widget(self.info_page)
        self.screen_manager.add_widget(screen)
        return self.screen_manager

    def create_chat_page(self):
        self.chat_page = ChatPage()
        screen = Screen(name="Chat")
        screen.add_widget(self.chat_page)
        self.screen_manager.add_widget(screen)


def show_error(message):
    chat_app.info_page.update_info(message)
    chat_app.screen_manager.current = "Info"
    Clock.schedule_once(sys.exit, 10)


if __name__ == "__main__":
    chat_app = Epic()
    chat_app.run()
