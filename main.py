import time

import cv2
import numpy as np
from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

BG = (0.035, 0.055, 0.09, 1)
CYAN = (0.20, 0.92, 1.0, 1)


class BoxOverlay(Widget):
    """Draws person boxes over the live camera preview."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boxes = []
        self.bind(pos=self.redraw, size=self.redraw)

    def set_boxes(self, boxes):
        self.boxes = boxes
        self.redraw()

    def redraw(self, *_):
        self.canvas.after.clear()
        with self.canvas.after:
            Color(*CYAN)
            for x, y, w, h in self.boxes:
                # OpenCV uses top-left image coordinates; Kivy uses bottom-left.
                px = self.x + x * self.width
                py = self.y + (1.0 - y - h) * self.height
                Line(rectangle=(px, py, w * self.width, h * self.height), width=2.2)


class PersonCamApp(App):
    def build(self):
        self.title = "People ESP"
        self.camera_index = 0
        self.esp_on = False
        self.last_detection = 0.0
        self.boxes = []
        self.detector = cv2.HOGDescriptor()
        self.detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        root = BoxLayout(orientation="vertical", padding=12, spacing=10)
        Window.clearcolor = BG
        self.root_layout = root

        header = BoxLayout(size_hint_y=None, height=42, spacing=8)
        header.add_widget(Label(text="PEOPLE ESP", bold=True, font_size="20sp", halign="left"))
        self.status = Label(text="Kamera wird vorbereitet …", color=(0.55, 0.78, 0.86, 1), font_size="13sp", halign="right")
        header.add_widget(self.status)
        root.add_widget(header)

        self.preview_area = FloatLayout()
        self.preview_area.size_hint_y = 1
        root.add_widget(self.preview_area)
        self.camera = None
        self.overlay = BoxOverlay()
        self.preview_area.add_widget(self.overlay)

        controls = BoxLayout(size_hint_y=None, height=54, spacing=8)
        self.camera_button = Button(text="Rückkamera", background_normal="", background_color=(0.11, 0.16, 0.24, 1), font_size="15sp")
        self.camera_button.bind(on_release=self.switch_camera)
        self.esp_button = Button(text="ESP AUS", background_normal="", background_color=(0.11, 0.16, 0.24, 1), font_size="15sp")
        self.esp_button.bind(on_release=self.toggle_esp)
        controls.add_widget(self.camera_button)
        controls.add_widget(self.esp_button)
        root.add_widget(controls)
        root.add_widget(Label(text="Live-Erkennung auf dem Gerät · keine Bilder werden gespeichert oder gesendet", size_hint_y=None, height=24, font_size="10sp", color=(0.48, 0.60, 0.72, 1)))

        Clock.schedule_once(self.request_camera_access, 0.3)
        Clock.schedule_interval(self.detect_people, 0.18)
        return root

    def request_camera_access(self, *_):
        if platform == "android":
            try:
                from android.permissions import Permission, request_permissions
                request_permissions([Permission.CAMERA], self.permission_result)
                return
            except Exception as exc:
                self.status.text = f"Kamerazugriff: {exc}"
                return
        self.open_camera()

    def permission_result(self, permissions, grants):
        if grants and all(grants):
            Clock.schedule_once(self.open_camera, 0.2)
        else:
            self.status.text = "Bitte Kamerazugriff in den Android-Einstellungen erlauben."

    def open_camera(self, *_):
        if self.camera is not None:
            self.camera.play = False
            self.preview_area.remove_widget(self.camera)
        self.camera = Camera(index=self.camera_index, resolution=(320, 240), play=True, allow_stretch=True, keep_ratio=False)
        self.camera.bind(on_texture=self.camera_frame_ready)
        self.preview_area.add_widget(self.camera, index=1)
        self.status.text = "Kamera bereit · ESP ist aus"

    def switch_camera(self, *_):
        self.camera_index = 1 if self.camera_index == 0 else 0
        self.camera_button.text = "Frontkamera" if self.camera_index == 1 else "Rückkamera"
        self.open_camera()

    def toggle_esp(self, *_):
        self.esp_on = not self.esp_on
        self.esp_button.text = "ESP AN" if self.esp_on else "ESP AUS"
        self.esp_button.background_color = (0.0, 0.42, 0.50, 1) if self.esp_on else (0.11, 0.16, 0.24, 1)
        if not self.esp_on:
            self.boxes = []
            self.overlay.set_boxes([])
            self.status.text = "Kamera bereit · ESP ist aus"
        else:
            self.status.text = "Suche Personen …"

    def camera_frame_ready(self, *_):
        # Detection is rate-limited in detect_people to keep the preview responsive.
        pass

    def detect_people(self, _dt):
        if not self.esp_on or self.camera is None or self.camera.texture is None:
            return
        now = time.monotonic()
        if now - self.last_detection < 0.45:
            return
        self.last_detection = now
        try:
            width, height = self.camera.texture.size
            if width < 64 or height < 64:
                return
            rgba = np.frombuffer(self.camera.texture.pixels, dtype=np.uint8).reshape((height, width, 4))
            bgr = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGR)
            # Analyze a small frame to keep CPU use manageable on phones.
            small = cv2.resize(bgr, (320, 240), interpolation=cv2.INTER_AREA)
            found, weights = self.detector.detectMultiScale(
                small, hitThreshold=0.2, winStride=(8, 8), padding=(8, 8), scale=1.05
            )
            boxes = []
            for (x, y, w, h), score in zip(found, weights):
                if float(score) >= 0.35:
                    boxes.append((x / 320.0, y / 240.0, w / 320.0, h / 240.0))
            self.boxes = boxes
            self.overlay.set_boxes(boxes)
            self.status.text = f"{len(boxes)} Person(en) erkannt" if boxes else "Keine Person erkannt"
        except Exception as exc:
            self.status.text = f"Erkennung nicht verfügbar: {exc}"

    def on_stop(self):
        if self.camera is not None:
            self.camera.play = False
            self.camera = None


if __name__ == "__main__":
    PersonCamApp().run()

