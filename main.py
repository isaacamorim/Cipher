from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from plyer import accelerometer
import json
import os
from jnius import autoclass, PythonJavaClass, java_method
from kivy.utils import platform


# Classe para gerenciar sequências
class SequenceManager:
    def __init__(self):
        self.sequences_file = "sequences.json"
        self.load_sequences()

    def load_sequences(self):
        if os.path.exists(self.sequences_file):
            with open(self.sequences_file, "r") as f:
                self.sequences = json.load(f)
        else:
            self.sequences = {"default": ["volume_up", "power", "volume_up"]}
            self.save_sequences()

    def save_sequences(self):
        with open(self.sequences_file, "w") as f:
            json.dump(self.sequences, f)


class LockScreen(Popup):
    def __init__(self, sequence, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sequence
        self.attempts = 0
        self.current_input = []
        self.title = "Dispositivo Bloqueado!"
        self.content = Label(text="Insira a sequência correta")

    def on_key_down(self, key):
        self.current_input.append(key)
        print(f"Sequência atual: {self.current_input}")  # Debug
        if len(self.current_input) == len(self.sequence):
            if self.current_input == self.sequence:
                self.dismiss()
            else:
                self.attempts += 1
                self.current_input = []
                if self.attempts >= 3:
                    self.trigger_alarm()
            self.content.text = f"Tentativas restantes: {3 - self.attempts}"

    def trigger_alarm(self):
        sound = SoundLoader.load("alarm.mp3")
        if sound:
            sound.play()


# Classe principal do App
class CipherLockApp(App):

    def build(self):
        self.sequence_manager = SequenceManager()
        self.lock_sequence = self.sequence_manager.sequences["default"]
        self.current_input = []
        self.start_motion_detection()
        return BoxLayout()

    def on_button_press(self, button):
        if hasattr(self, "lock_screen") and self.lock_screen:
            self.lock_screen.on_key_down(button)
        else:
            print(f"Botão pressionado: {button}")

    def start_motion_detection(self):
        try:
            accelerometer.enable()
            Clock.schedule_interval(self.check_movement, 0.1)
        except:
            print("Acelerômetro não disponível")

    def check_movement(self, dt):
        try:
            accel = accelerometer.acceleration
            if accel and (abs(accel[0]) > 15 or abs(accel[1]) > 15):
                self.trigger_lock()
        except:
            pass

    def trigger_lock(self):
        lock = LockScreen(self.lock_sequence)
        lock.open()


if __name__ == "__main__":
    CipherLockApp().run()


from jnius import autoclass, PythonJavaClass, java_method
from kivy.app import App
from kivy.utils import platform

# Configuração da API Android
if platform == "android":
    Activity = autoclass("android.app.Activity")
    KeyEvent = autoclass("android.view.KeyEvent")
    PythonActivity = autoclass("org.kivy.android.PythonActivity")
    Context = autoclass("android.content.Context")
    WindowManager = autoclass("android.view.WindowManager")

    # Classe para detectar pressionamento de botões
    class KeyListener(PythonJavaClass):
        __javainterfaces__ = ["android/view/View$OnKeyListener"]

        @java_method("(Landroid/view/View;ILandroid/view/KeyEvent;)Z")
        def onKey(self, view, key_code, event):
            if event.getAction() == KeyEvent.ACTION_DOWN:
                if key_code == KeyEvent.KEYCODE_VOLUME_UP:
                    App.get_running_app().on_button_press("volume_up")
                    return True
                elif key_code == KeyEvent.KEYCODE_VOLUME_DOWN:
                    App.get_running_app().on_button_press("volume_down")
                    return True
                elif key_code == KeyEvent.KEYCODE_POWER:
                    App.get_running_app().on_button_press("power")
                    return True
            return False

    # Ativar listener de botões
    activity = PythonActivity.mActivity
    key_listener = KeyListener()
    activity.getWindow().getDecorView().setOnKeyListener(key_listener)
    
    
    if platform == 'android':
    PowerManager = autoclass('android.os.PowerManager')
    power_service = activity.getSystemService(Context.POWER_SERVICE)
    wake_lock = power_service.newWakeLock(
        PowerManager.SCREEN_BRIGHT_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP,
        "CipherLock:WakeLock"
    )
    wake_lock.acquire()
