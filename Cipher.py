from kivy.app import App
from kivy.uix.label import Label
from plyer import accelerometer
import time


class SecurityApp(App):
    def on_start(self):
        accelerometer.enable()
        self.sequence = ["volume_up", "power"]  # Sequência padrão

    def check_movement(self, dt):
        accel_data = accelerometer.acceleration
        if accel_data[0] > 15:  # Detecção de movimento brusco
            self.trigger_lock()

    def trigger_lock(self):
        self.root.clear_widgets()
        self.root.add_widget(
            Label(text="Bloqueado! Pressione Volume ⬆️ + Power para desbloquear.")
        )

    def on_key_down(self, key):
        if key == "volume_up" and self.check_button_sequence():
            self.unlock()

    def unlock(self):
        self.root.clear_widgets()
        self.root.add_widget(Label(text="Dispositivo desbloqueado!"))


SecurityApp().run()
