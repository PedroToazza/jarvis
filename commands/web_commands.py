"""
commands/web_commands.py — Reutiliza navegador
"""
import urllib.parse
from datetime import datetime
from .window_commands import open_url_in_browser


DIAS_SEMANA = [
    "segunda-feira", "terça-feira", "quarta-feira",
    "quinta-feira", "sexta-feira", "sábado", "domingo"
]
MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
]


class WebCommands:
    def __init__(self, tts):
        self.tts = tts

    def search_google(self, query: str):
        if not query: self.tts.speak("O que pesquisar?"); return
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        open_url_in_browser(url)
        self.tts.speak(f"Pesquisando {query} no Google.")

    def search_youtube(self, query: str):
        if not query: self.tts.speak("O que pesquisar?"); return
        url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        open_url_in_browser(url)
        self.tts.speak(f"Pesquisando {query} no YouTube.")

    def tell_time(self):
        now = datetime.now()
        hora = now.strftime("%H e %M minutos") if now.minute != 0 else now.strftime("%H horas")
        self.tts.speak(f"São {hora}.")

    def tell_date(self):
        now = datetime.now()
        self.tts.speak(f"Hoje é {DIAS_SEMANA[now.weekday()]}, "
                       f"{now.day} de {MESES[now.month-1]} de {now.year}.")