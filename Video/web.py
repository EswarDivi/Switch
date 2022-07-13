from re import L
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
import cv2, imutils, socket
import numpy as np
import time
import base64
import cv2
from kivy.uix.screenmanager import ScreenManager, NoTransition,Screen


class CamApp(App):
    def build(self):
        self.BUFF_SIZE = 65536
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE
        )
        self.img1 = Image()
        layout = BoxLayout()
        host_ip = "192.168.140.23"
        port = 9999
        message = b"Hello"

        self.client_socket.sendto(message, (host_ip, port))
        layout.add_widget(self.img1)
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 33.0)
        return layout

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


if __name__ == "__main__":
    chat_app=CamApp()
    chat_app.run()
