import subprocess

subprocess.run("python Kivy_App\Chat_Server.py & python Kivy_App\Video_Server.py & python Kivy_App\Audio_server.py ", shell=True)