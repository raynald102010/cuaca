# -*- coding: utf-8 -*-
"""
Cuaca - aplikasi prakiraan cuaca sederhana.
Data cuaca: Open-Meteo (tidak memerlukan API key).
"""
import threading
from datetime import datetime
from urllib.parse import quote

import requests
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex

BG = get_color_from_hex("#F4F7FB")
CARD = get_color_from_hex("#FFFFFF")
INK = get_color_from_hex("#17243A")
MUTED = get_color_from_hex("#718096")
ACCENT = get_color_from_hex("#3478F6")

WEATHER = {
    0: "Cerah", 1: "Cerah berawan", 2: "Berawan sebagian",
    3: "Mendung", 45: "Berkabut", 48: "Kabut tebal",
    51: "Gerimis ringan", 53: "Gerimis", 55: "Gerimis lebat",
    61: "Hujan ringan", 63: "Hujan", 65: "Hujan lebat",
    71: "Salju ringan", 73: "Salju", 75: "Salju lebat",
    80: "Hujan lokal", 81: "Hujan lokal", 82: "Hujan lebat lokal",
    95: "Badai petir", 96: "Badai petir", 99: "Badai petir kuat"
}

def weather_text(code):
    return WEATHER.get(int(code), "Kondisi tidak diketahui")

def get_json(url, params=None):
    response = requests.get(url, params=params, timeout=15,
                            headers={"User-Agent": "CuacaApp/1.0"})
    response.raise_for_status()
    return response.json()

class WeatherApp(App):
    def build(self):
        self.title = "Cuaca"
        self.root_box = BoxLayout(orientation="vertical", padding=dp(18),
                                  spacing=dp(12))
        self.root_box.canvas.before.clear()
        from kivy.graphics import Color, Rectangle
        with self.root_box.canvas.before:
            Color(*BG)
            self.bg_rect = Rectangle(pos=self.root_box.pos, size=self.root_box.size)
        self.root_box.bind(pos=self._update_bg, size=self._update_bg)

        header = BoxLayout(size_hint_y=None, height=dp(42))
        title = Label(text="[b]Cuaca[/b]", markup=True, color=INK,
                      font_size="25sp", halign="left", valign="middle")
        title.bind(size=lambda w, s: setattr(w, "text_size", s))
        header.add_widget(title)
        self.root_box.add_widget(header)

        search_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        self.city_input = TextInput(
            hint_text="Cari kota, misalnya Pematangsiantar",
            multiline=False, font_size="15sp", padding=[dp(12), dp(13)],
            background_normal="", background_active="",
            background_color=CARD, foreground_color=INK,
            hint_text_color=MUTED
        )
        self.city_input.text = "Pematangsiantar"
        self.city_input.bind(on_text_validate=lambda *_: self.search_weather())
        search_row.add_widget(self.city_input)
        search = Button(text="Cari", size_hint_x=None, width=dp(76),
                        background_normal="", background_color=ACCENT,
                        color=(1, 1, 1), bold=True)
        search.bind(on_release=lambda *_: self.search_weather())
        search_row.add_widget(search)
        self.root_box.add_widget(search_row)

        self.status = Label(text="Masukkan kota untuk melihat prakiraan.",
                            color=MUTED, size_hint_y=None, height=dp(26),
                            font_size="13sp", halign="left")
        self.status.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.root_box.add_widget(self.status)

        self.content = BoxLayout(orientation="vertical", spacing=dp(12),
                                 size_hint_y=None)
        self.content.bind(minimum_height=self.content.setter("height"))
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.content)
        self.root_box.add_widget(scroll)

        self.search_weather()
        return self.root_box

    def _update_bg(self, *_):
        self.bg_rect.pos = self.root_box.pos
        self.bg_rect.size = self.root_box.size

    def add_label(self, text, size=15, color=INK, height=32, markup=False):
        label = Label(text=text, markup=markup, color=color,
                      font_size=f"{size}sp", size_hint_y=None,
                      height=dp(height), halign="left", valign="middle")
        label.bind(size=lambda w, s: setattr(w, "text_size", (s[0], None)))
        self.content.add_widget(label)
        return label

    def search_weather(self):
        city = self.city_input.text.strip()
        if not city:
            self.status.text = "Masukkan nama kota terlebih dahulu."
            return
        self.status.text = "Mengambil data cuaca..."
        threading.Thread(target=self._load_weather, args=(city,), daemon=True).start()

    def _load_weather(self, city):
        try:
            geo = get_json(
                "https://geocoding-api.open-meteo.com/v1/search",
                {"name": city, "count": 1, "language": "id", "format": "json"}
            )
            results = geo.get("results") or []
            if not results:
                raise ValueError("Kota tidak ditemukan. Periksa ejaan nama kota.")
            place = results[0]
            params = {
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,"
                           "is_day,precipitation,weather_code,wind_speed_10m",
                "hourly": "temperature_2m,precipitation_probability,weather_code",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                         "precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 7
            }
            data = get_json("https://api.open-meteo.com/v1/forecast", params)
            Clock.schedule_once(lambda dt: self._show_weather(place, data), 0)
        except Exception as exc:
            message = str(exc)
            Clock.schedule_once(lambda dt: self._show_error(message), 0)

    def _show_error(self, message):
        self.status.text = "Tidak dapat memuat data."
        self.content.clear_widgets()
        self.add_label(message, 14, MUTED, 60)

    def _show_weather(self, place, data):
        self.content.clear_widgets()
        current = data["current"]
        daily = data["daily"]
        location = ", ".join(filter(None, [
            place.get("name"), place.get("admin1"), place.get("country")
        ]))
        self.status.text = f"Terakhir diperbarui: {current.get('time', '').replace('T', ' ')}"
        self.add_label(location, 18, INK, 34, True)
        self.add_label(f"{round(current['temperature_2m'])}°", 54, INK, 82, True)
        self.add_label(weather_text(current["weather_code"]), 19, MUTED, 34)
        self.add_label(
            f"Terasa seperti {round(current['apparent_temperature'])}°C",
            14, MUTED, 28
        )

        self.add_label("Kondisi saat ini", 17, INK, 40, True)
        metrics = [
            ("Kelembapan", f"{current['relative_humidity_2m']}%"),
            ("Angin", f"{current['wind_speed_10m']} km/jam"),
            ("Curah hujan", f"{current['precipitation']} mm"),
        ]
        for name, value in metrics:
            self.add_label(f"{name}   •   {value}", 15, MUTED, 34)

        self.add_label("Prakiraan per jam", 17, INK, 48, True)
        hourly = data.get("hourly", {})
        hourly_times = hourly.get("time", [])
        now_text = current.get("time", "")
        start_index = 0
        for j, hour_text in enumerate(hourly_times):
            if hour_text >= now_text[:13]:
                start_index = j
                break
        for j in range(start_index, min(start_index + 6, len(hourly_times))):
            hour = datetime.fromisoformat(hourly_times[j]).strftime("%H:%M")
            temp = round(hourly["temperature_2m"][j])
            rain = hourly["precipitation_probability"][j]
            self.add_label(
                f"{hour}   {temp}°C   •   Peluang hujan {rain}%",
                13, INK, 34
            )

        self.add_label("Prakiraan 7 hari", 17, INK, 48, True)
        for i, day in enumerate(daily["time"]):
            date = datetime.fromisoformat(day).strftime("%a, %d %b")
            code = daily["weather_code"][i]
            high = round(daily["temperature_2m_max"][i])
            low = round(daily["temperature_2m_min"][i])
            rain = daily.get("precipitation_probability_max", [None] * len(daily["time"]))[i]
            rain_text = f"  •  Peluang hujan {rain}%" if rain is not None else ""
            self.add_label(
                f"{date}   {weather_text(code)}   {high}° / {low}°{rain_text}",
                13, INK, 42
            )
        self.add_label("Sumber data: Open-Meteo", 11, MUTED, 42)

if __name__ == "__main__":
    WeatherApp().run()
