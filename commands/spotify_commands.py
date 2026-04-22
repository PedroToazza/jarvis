"""
commands/spotify_commands.py — Música, playlist, álbum, artista
"""
import os
import subprocess
import time


class SpotifyCommands:
    def __init__(self, tts, client=None):
        self.tts = tts
        self.sp  = client

    def _ok(self) -> bool:
        if not self.sp:
            self.tts.speak("Spotify não configurado.")
            return False
        return True

    def _active_device(self):
        try:
            devs = self.sp.devices()
            for d in devs.get('devices', []):
                if d.get('is_active'):
                    return d['id']
            devs_list = devs.get('devices', [])
            return devs_list[0]['id'] if devs_list else None
        except Exception:
            return None

    def _open_spotify_if_needed(self):
        try:
            if self._active_device(): return
            print("🎵 Abrindo Spotify...")
            try: os.startfile("spotify:")
            except Exception: subprocess.Popen('start spotify:', shell=True)
            for _ in range(12):
                time.sleep(1.5)
                if self._active_device(): return
        except Exception as e:
            print(f"  Spotify abrir: {e}")

    def _start_playback(self, uri_list=None, context_uri=None):
        self._open_spotify_if_needed()
        device = self._active_device()
        if not device:
            self.tts.speak("Não consegui abrir o Spotify.")
            return False
        try:
            if context_uri:
                self.sp.start_playback(device_id=device, context_uri=context_uri)
            else:
                self.sp.start_playback(device_id=device, uris=uri_list)
            return True
        except Exception as e:
            if 'Premium' in str(e):
                self.tts.speak("Requer Spotify Premium.")
            else:
                self.tts.speak("Erro ao controlar o Spotify.")
            print(f"  playback: {e}")
            return False

    def play_track(self, query: str):
        if not self._ok(): return
        try:
            results = self.sp.search(q=query, limit=1, type='track')
            tracks  = results['tracks']['items']
            if not tracks:
                self.tts.speak(f"Não encontrei: {query}.")
                return
            t = tracks[0]
            if self._start_playback(uri_list=[t['uri']]):
                self.tts.speak(f"Tocando {t['name']} de {t['artists'][0]['name']}.")
        except Exception as e:
            print(f"  play_track: {e}")

    def play_playlist(self, query: str):
        if not self._ok(): return
        try:
            found = None
            results = self.sp.current_user_playlists(limit=50)
            qnorm = query.lower()
            for pl in results.get('items', []):
                if qnorm in (pl.get('name') or '').lower():
                    found = pl; break
            if not found:
                results = self.sp.search(q=query, limit=1, type='playlist')
                items = results['playlists']['items']
                if items: found = items[0]
            if not found:
                self.tts.speak(f"Playlist não encontrada: {query}.")
                return
            if self._start_playback(context_uri=found['uri']):
                self.tts.speak(f"Tocando playlist {found['name']}.")
        except Exception as e:
            print(f"  playlist: {e}")
            self.tts.speak("Erro ao tocar a playlist.")

    def play_album(self, query: str):
        if not self._ok(): return
        try:
            results = self.sp.search(q=query, limit=1, type='album')
            items = results['albums']['items']
            if not items:
                self.tts.speak(f"Álbum não encontrado: {query}.")
                return
            a = items[0]
            if self._start_playback(context_uri=a['uri']):
                self.tts.speak(f"Tocando álbum {a['name']} de {a['artists'][0]['name']}.")
        except Exception as e:
            print(f"  album: {e}")

    def play_artist(self, query: str):
        if not self._ok(): return
        try:
            results = self.sp.search(q=query, limit=1, type='artist')
            artists = results['artists']['items']
            if not artists:
                self.tts.speak(f"Artista não encontrado: {query}.")
                return
            artist = artists[0]
            top = self.sp.artist_top_tracks(artist['id'], country='BR')
            uris = [t['uri'] for t in top.get('tracks', [])]
            if not uris:
                self.tts.speak(f"Sem músicas de {artist['name']}.")
                return
            if self._start_playback(uri_list=uris):
                self.tts.speak(f"Tocando {artist['name']}.")
        except Exception as e:
            print(f"  artist: {e}")

    def play_back_in_black(self):
        self._open_spotify_if_needed()
        self.play_track("Back in Black AC/DC")

    def pause(self):
        if not self._ok(): return
        try: self.sp.pause_playback(); self.tts.speak("Pausado.")
        except Exception: self.tts.speak("Não foi possível pausar.")

    def resume(self):
        if not self._ok(): return
        try: self.sp.start_playback(device_id=self._active_device()); self.tts.speak("Retomando.")
        except Exception: self.tts.speak("Não foi possível retomar.")

    def next_track(self):
        if not self._ok(): return
        try: self.sp.next_track(); self.tts.speak("Próxima música.")
        except Exception: self.tts.speak("Não foi possível avançar.")

    def prev_track(self):
        if not self._ok(): return
        try: self.sp.previous_track(); self.tts.speak("Música anterior.")
        except Exception: self.tts.speak("Não foi possível voltar.")

    def current_track(self):
        if not self._ok(): return
        try:
            info = self.sp.current_playback()
            if info and info.get('item'):
                self.tts.speak(f"Tocando agora: {info['item']['name']} de {info['item']['artists'][0]['name']}.")
            else:
                self.tts.speak("Nada tocando.")
        except Exception:
            self.tts.speak("Erro ao obter música atual.")