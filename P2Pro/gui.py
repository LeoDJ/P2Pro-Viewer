import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.graphics.texture import Texture
from kivy.clock import Clock, mainthread
from kivy.lang import Builder
from kivy.base import EventLoop
from kivy.core.window import Window

from kivymd.app import MDApp

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from os.path import dirname, basename, join

filename = 'P2Pro/gui.kv'
PATH = dirname(filename)
TARGET = basename(filename)

class KvHandler(FileSystemEventHandler):
    def __init__(self, callback, target, **kwargs):
        super(KvHandler, self).__init__(**kwargs)
        self.callback = callback
        self.target = target

    def on_any_event(self, event):
        if basename(event.src_path) == self.target:
            self.callback()



class Scale(Widget):
    def __init__(self, **kwargs):
        super(Scale, self).__init__(**kwargs)
        self.bind(size=self.draw_scale)
        self.bind(pos=self.draw_scale)

    def draw_scale(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=(10, self.height))

            # Draw color gradient
            # Replace this with your own gradient logic
            color_range = [(1, 0, 0, 1), (0, 1, 0, 1)]  # Example gradient from red to green
            color_steps = len(color_range)
            step_height = self.height / color_steps
            for i, color in enumerate(color_range):
                Color(*color)
                Rectangle(pos=(self.pos[0] + 10, self.pos[1] + i * step_height), size=(self.width - 10, step_height))

            # Draw ticks with values
            # Replace this with your own tick logic
            tick_values = [0, 0.25, 0.5, 0.75, 1.0]  # Example tick values
            tick_positions = [(self.pos[0] + 10, self.pos[1] + i * step_height) for i, _ in enumerate(tick_values)]
            for value, position in zip(tick_values, tick_positions):
                Label(text=str(value), pos=(position[0] + 15, position[1] - 10), size_hint=(None, None))
                Line(points=[position[0] + 10, position[1], position[0] + self.width, position[1]], width=1)


class GuiApp(MDApp):
    def on_start(self):
        # print(dir(self.root.ids))
        print(self.root.ids.keys())
        self.clock_interval = Clock.schedule_interval(self.update_frame, 1.0 / 60.0)

    def update_frame(self, dt):
        # Generate sample frame (replace with your own video stream processing logic)
        frame = generate_frame()

        # Update image texture
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='luminance', bufferfmt='ushort')
        texture.blit_buffer(frame.tobytes(), colorfmt='luminance', bufferfmt='ushort')
        # print('.', end='')
        # print(dir(self.root.ids))
        # print(self.root.ids.items())
        self.root.ids.image_widget.texture = texture
    


    # dev build function, reloads on .kv change
    def build(self):
        self.title = "P2 Pro Viewer"
        self.theme_cls.theme_style = "Dark"
        # self.on_start()
        o = Observer()
        o.schedule(KvHandler(self.update, TARGET), PATH)
        o.start()
        Clock.schedule_once(self.update, 1)
        return super(GuiApp, self).build()

    @mainthread
    def update(self, *args):
        print(".kv file changed, reloading...")
        Builder.unload_file(join(PATH, TARGET))
        Window.remove_widget(Window.children[0])
        try:
            Window.add_widget(Builder.load_file(join(PATH, TARGET)))
        except Exception as e:
            Window.add_widget(Label(text=str(e)))
            print(str(e))
            # Window.add_widget(Label(text=e.message if e.message else str(e)))
        self.on_start()


import numpy as np
def generate_frame():
    # Replace this with your video stream processing logic
    # Here's a dummy example that generates a gradient frame
    frame = np.arange(0, 65536, 1, dtype=np.uint16).reshape(256, 256)
    return frame


if __name__ == '__main__':
    GuiApp().run()