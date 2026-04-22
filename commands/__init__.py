"""
commands/__init__.py — Roteador limpo
"""
import re
import sys
import time
import webbrowser
from urllib.parse import urlparse

from .system_commands  import SystemCommands
from .web_commands     import WebCommands
from .spotify_commands import SpotifyCommands
from .ai_parser        import AIParser
from .timer_commands   import TimerCommands
from .file_commands    import FileCommands
from .close_commands   import CloseCommands
from .window_commands  import WindowCommands, open_url_in_browser
from .screenshot       import ScreenshotCommand


HELP_TEXT = (
    "Eu posso abrir, fechar e minimizar apps, pesquisar, tocar músicas, "
    "criar e editar arquivos, tirar screenshots, gerenciar timers, e responder "
    "perguntas. Peça 'me explica mais' para respostas detalhadas."
)


class CommandProcessor:
    def __init__(self, tts, shared_state, spotify_client=None):
        self.tts = tts
        self.shared_state = shared_state
        self.system  = SystemCommands(tts)
        self.web     = WebCommands(tts)
        self.spotify = SpotifyCommands(tts, spotify_client)
        self.timer   = TimerCommands(tts)
        self.files   = FileCommands(tts)
        self.closer  = CloseCommands(tts)
        self.windows = WindowCommands(tts)
        self.shot    = ScreenshotCommand(tts)
        self.ai      = AIParser()

    def execute(self, text):
        text = (text or "").strip()
        if not text: return
        print(f"🔍 Processando: '{text}'")
        self.shared_state['last_command'] = text

        if self.ai.available():
            actions = self.ai.parse(text)
            if actions:
                if len(actions) == 1 and actions[0]["action"] == "chat":
                    q = actions[0]["target"] or text
                    resp = self.ai.chat(q)
                    if resp: self.tts.speak(resp); return
                if len(actions) == 1 and actions[0]["action"] == "explain_more":
                    resp = self.ai.explain_more()
                    if resp: self.tts.speak(resp); return

                actions = [a for a in actions if a["action"] != "unknown"]
                if actions:
                    self._run_sequence(actions); return

            resp = self.ai.chat(text)
            if resp: self.tts.speak(resp); return

        self._rule_based(text.lower())

    def _run_sequence(self, actions):
        n = len(actions)
        for i, a in enumerate(actions):
            try: self._dispatch(a["action"], a["target"])
            except SystemExit: raise
            except Exception as e: print(f"  Erro em {a['action']}: {e}")
            if i < n - 1:
                deadline = time.time() + 15
                while self.shared_state.get('is_speaking') and time.time() < deadline:
                    time.sleep(0.1)
                time.sleep(0.3)

    def _split_pipe(self, t):
        if '|' in t:
            left, right = t.split('|', 1)
            return left.strip(), right
        return t.strip(), ""

    def _dispatch(self, action, target):
        t = target.strip()
        if action == "open_app": self.system.open_app(t)
        elif action == "open_url":
            if not t.startswith(("http://","https://")): t = "https://" + t
            open_url_in_browser(t)
            self.tts.speak(f"Abrindo {self._pretty_domain(t)}.")
        elif action == "close": self.closer.close(t)
        elif action == "minimize": self.windows.minimize(t)
        elif action == "search_google": self.web.search_google(t)
        elif action == "search_youtube": self.web.search_youtube(t)
        elif action == "spotify_play":
            if t: self.spotify.play_track(t)
            else: self.spotify.resume()
        elif action == "spotify_playlist": self.spotify.play_playlist(t)
        elif action == "spotify_album":    self.spotify.play_album(t)
        elif action == "spotify_artist":   self.spotify.play_artist(t)
        elif action == "spotify_pause":    self.spotify.pause()
        elif action == "spotify_resume":   self.spotify.resume()
        elif action == "spotify_next":     self.spotify.next_track()
        elif action == "spotify_prev":     self.spotify.prev_track()
        elif action == "spotify_current":  self.spotify.current_track()
        elif action == "set_volume":     self.system.handle_volume(f"volume {t}")
        elif action == "set_brightness": self.system.handle_brightness(f"brilho {t}")
        elif action == "set_timer":    self.timer.set_timer(t)
        elif action == "set_reminder": self.timer.set_reminder(t)
        elif action == "screenshot":   self.shot.take()
        elif action == "file_create_folder": self.files.create_folder(t)
        elif action == "file_create":
            p, c = self._split_pipe(t); self.files.create_file(p, c)
        elif action == "file_write":
            p, c = self._split_pipe(t); self.files.write_file(p, c)
        elif action == "file_append":
            p, c = self._split_pipe(t); self.files.append_file(p, c)
        elif action == "file_read":   self.files.read_file(t)
        elif action == "file_delete": self.files.delete_path(t)
        elif action == "file_list":   self.files.list_folder(t)
        elif action == "file_open":   self.files.open_folder(t)
        elif action == "chat":
            resp = self.ai.chat(t) if self.ai.available() else None
            if resp: self.tts.speak(resp)
        elif action == "explain_more":
            resp = self.ai.explain_more() if self.ai.available() else None
            if resp: self.tts.speak(resp)
        elif action == "tell_time": self.web.tell_time()
        elif action == "tell_date": self.web.tell_date()
        elif action == "help":      self.tts.speak(HELP_TEXT)
        elif action == "exit":
            self.tts.speak("Encerrando."); sys.exit(0)
        else:
            self.tts.speak("Não entendi.")

    def _pretty_domain(self, url):
        try: return urlparse(url).netloc.replace("www.", "")
        except Exception: return "o site"

    def _rule_based(self, text):
        if 'encerrar' in text:
            self.tts.speak("Encerrando."); sys.exit(0)
        elif 'horas' in text: self.web.tell_time()
        elif 'screenshot' in text or 'print' in text: self.shot.take()
        elif 'minimizar' in text:
            kw = re.sub(r'\b(minimizar|minimize|a|o)\b', '', text).strip()
            self.windows.minimize(kw or "todas")
        elif 'timer' in text: self.timer.set_timer(text)
        elif 'abrir' in text or 'abre' in text:
            q = re.sub(r'\b(abrir|abre|o|a|um|uma)\b', '', text).strip()
            self.system.open_app(q)
        else:
            self.tts.speak("Não entendi.")