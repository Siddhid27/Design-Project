import sounddevice as sd
import numpy as np
import wave
import threading
import time
import geocoder
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy_garden.mapview import MapView, MapMarker
from kivy.lang import Builder

# Kivy layout for the map screen
KV = '''
ScreenManager:
    WelcomeScreen:
    ProfileCreationScreen:
    MainScreen:
    EmergencyContactsScreen:
    NearbyServicesScreen:
    MapScreen:

<WelcomeScreen>:
    BoxLayout:
        orientation: "vertical"
        Label:
            text: "Women's Safety App"
            font_size: 32
            halign: 'center'
            valign: 'middle'
            size_hint_y: 0.6
        Button:
            text: "Get Started"
            size_hint_y: 0.2
            on_press: app.root.current = 'profile'

<MapScreen>:
    BoxLayout:
        orientation: "vertical"
        MapView:
            id: map_view
            zoom: 12
            lat: 19.0760
            lon: 72.8777
'''
class WelcomeScreen(Screen):
    pass
Window.size = (360, 640)

class ProfileCreationScreen(Screen):
    def __init__(self, **kwargs):
        super(ProfileCreationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.name_input = TextInput(hint_text="Enter Your Name", size_hint=(1, 0.2), multiline=False)
        layout.add_widget(self.name_input)

        self.contact_input = TextInput(hint_text="Enter Emergency Contact", size_hint=(1, 0.2), multiline=False)
        layout.add_widget(self.contact_input)

        create_profile_button = Button(text="Create Profile", size_hint=(1, 0.2), background_color=(0, 0.5, 0, 1))
        create_profile_button.bind(on_press=self.create_profile)
        layout.add_widget(create_profile_button)

        self.add_widget(layout)

    def create_profile(self, instance):
        name = self.name_input.text
        emergency_contact = self.contact_input.text
        if name and emergency_contact:
            print(f"Profile Created: Name - {name}, Emergency Contact - {emergency_contact}")
            app = App.get_running_app()
            app.root.current = 'main'
        else:
            print("Please fill in all fields!")

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.status_label = Label(text="Press the button to send an alert", size_hint=(1, 0.2))
        layout.add_widget(self.status_label)

        self.alert_button = Button(text="Send Alert", size_hint=(1, 0.2), background_color=(1, 0, 0, 1))
        self.alert_button.bind(on_press=self.send_alert)
        layout.add_widget(self.alert_button)

        self.location_button = Button(text="Get Location", size_hint=(1, 0.2), background_color=(0, 0, 1, 1))
        self.location_button.bind(on_press=self.get_location)
        layout.add_widget(self.location_button)

        emergency_button = Button(text="Emergency Contacts", size_hint=(1, 0.2), background_color=(0, 1, 0, 1))
        emergency_button.bind(on_press=self.go_to_emergency)
        layout.add_widget(emergency_button)

        nearby_button = Button(text="Nearby Services", size_hint=(1, 0.2), background_color=(0.5, 0, 0.5, 1))
        nearby_button.bind(on_press=self.go_to_nearby)
        layout.add_widget(nearby_button)

        map_button = Button(text="View Map", size_hint=(1, 0.2), background_color=(0, 0.5, 1, 1))
        map_button.bind(on_press=self.go_to_map)
        layout.add_widget(map_button)

        self.add_widget(layout)

    def go_to_emergency(self, instance):
        app = App.get_running_app()
        app.root.current = 'emergency'

    def go_to_nearby(self, instance):
        app = App.get_running_app()
        app.root.current = 'nearby'

    def go_to_map(self, instance):
        app = App.get_running_app()
        app.root.current = 'map'
        self.get_location()

    def send_alert(self, instance):
        self.status_label.text = "Alert sent!"
        self.record_audio()

    def get_location(self, instance=None):  # Updated to accept instance
        g = geocoder.ip('me')  # Get current location
        if g.ok and g.latlng:
            latitude, longitude = g.latlng
            location = f"Latitude: {latitude}, Longitude: {longitude}"
            self.status_label.text = location
            app = App.get_running_app()
            map_screen = app.root.get_screen('map')
            map_screen.display_location(latitude, longitude)
        else:
            self.status_label.text = "Could not retrieve location."
    def record_audio(self):
        fs = 44100
        duration = 5
        self.status_label.text = "Recording audio..."
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        self.save_audio(recording)

    def save_audio(self, recording):
        filename = "alert_audio.wav"
        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(2)
        wave_file.setframerate(44100)
        wave_file.writeframes(recording.tobytes())
        wave_file.close()
        self.status_label.text = "Audio recorded and saved!"

class EmergencyContactsScreen(Screen):
    def __init__(self, **kwargs):
        super(EmergencyContactsScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.contact_label = Label(
            text="Emergency Contacts:\n\nPolice: 100\nAmbulance: 102\nFire Brigade: 101\nLocal Hospital: 1234567890",
            size_hint=(1, 0.8)
        )
        layout.add_widget(self.contact_label)

        back_button = Button(text="Back to Main", size_hint=(1, 0.2), background_color=(0.5, 0.5, 0.5, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'

class NearbyServicesScreen(Screen):
    def __init__(self, **kwargs):
        super(NearbyServicesScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.services_label = Label(
            text="Nearby Police Stations:\n\nStation A: 9876543210\nStation B: 1234567890\nStation C: 0987654321",
            size_hint=(1, 0.8)
        )
        layout.add_widget(self.services_label)

        back_button = Button(text="Back to Main", size_hint=(1, 0.2), background_color=(0.5, 0.5, 0.5, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'

class MapScreen(Screen):
    def __init__(self, **kwargs):
        super(MapScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.map_view = MapView(zoom=12, lat=19.0760, lon=72.8777)  # Default location
        layout.add_widget(self.map_view)

        add_marker_button = Button(text="Add Marker", size_hint=(1, 0.2), background_color=(0.5, 0.5, 0.5, 1))
        add_marker_button.bind(on_press=lambda x: self.add_marker(19.0760, 72.8777))
        layout.add_widget(add_marker_button)

        back_button = Button(text="Back to Main", size_hint=(1, 0.2), background_color=(0.5, 0.5, 0.5, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

    def add_marker(self, latitude, longitude):
        marker = MapMarker(lat=latitude, lon=longitude)
        self.map_view.add_marker(marker)

    def display_location(self, latitude, longitude):
        self.map_view.lat = latitude
        self.map_view.lon = longitude
        self.add_marker(latitude, longitude)

    def go_back(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'

class SafetyApp(App):
    def build(self):
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(WelcomeScreen(name='welcome'))
        sm.add_widget(ProfileCreationScreen(name='profile'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EmergencyContactsScreen(name='emergency'))
        sm.add_widget(NearbyServicesScreen(name='nearby'))
        sm.add_widget(MapScreen(name='map'))
        return sm

if __name__ == '__main__':
    SafetyApp().run()
