"""
main.py — Ponto de entrada
"""
import os
import sys
import threading


def main():
    print("=" * 54)
    print("   🤖  JARVIS — iniciando...")
    print("=" * 54)
    import config

    shared_state = {
        'is_speaking': False, 'is_busy': False, 'is_active': True,
        'status': 'idle', 'last_command': '', 'last_reply': '',
    }

    try:
        from gui import JarvisApp
        app = JarvisApp(shared_state)
    except ModuleNotFoundError as e:
        if e.name not in ('tkinter', 'customtkinter'):
            raise

        print("⚠️  Interface gráfica indisponível. Iniciando em modo sem GUI.")
        print("   No Fedora, instale com: sudo dnf install python3-tkinter")

        class HeadlessApp:
            def mainloop(self):
                threading.Event().wait()

        app = HeadlessApp()

    def _start_backend():
        try:
            from tts_engine import TTSEngine
            original = TTSEngine.speak
            def speak_log(self, text):
                shared_state['last_reply'] = text
                return original(self, text)
            TTSEngine.speak = speak_log

            tts = TTSEngine(shared_state)

            spotify_client = None
            if config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET:
                try:
                    import spotipy
                    from spotipy.oauth2 import SpotifyOAuth
                    auth = SpotifyOAuth(
                        client_id=config.SPOTIFY_CLIENT_ID,
                        client_secret=config.SPOTIFY_CLIENT_SECRET,
                        redirect_uri=config.SPOTIFY_REDIRECT_URI,
                        scope=config.SPOTIFY_SCOPE,
                        cache_path=os.path.join(
                            os.path.dirname(os.path.abspath(__file__)),
                            '.spotify_cache'),
                        open_browser=True,
                    )
                    spotify_client = spotipy.Spotify(auth_manager=auth)
                    spotify_client.current_user()
                    print("✅ Spotify conectado.")
                except Exception as e:
                    print(f"⚠️  Spotify: {e}")

            from commands import CommandProcessor
            cmd = CommandProcessor(tts, shared_state, spotify_client)

            from clap_detector import ClapDetector

            def on_double_clap():
                if shared_state.get('is_busy') or shared_state.get('is_speaking'): return
                if not shared_state.get('is_active', True): return
                tts.speak("Ativando modo programação.")
                cmd.system.open_app("visual studio code")
                cmd.spotify.play_back_in_black()

            clap = ClapDetector(
                callback=on_double_clap, shared_state=shared_state,
                peak_threshold=config.CLAP_PEAK_THRESHOLD,
                sustain_threshold=config.CLAP_SUSTAIN_THRESHOLD,
                max_interval=config.CLAP_MAX_INTERVAL,
                cooldown=config.CLAP_COOLDOWN,
            )
            threading.Thread(target=clap.start, daemon=True).start()

            from listener import VoiceListener
            listener = VoiceListener(on_command=cmd.execute, tts=tts,
                                     shared_state=shared_state)
            tts.speak("Jarvis online.")
            listener.start()
        except Exception as e:
            print(f"❌ Backend erro: {e}")
            import traceback; traceback.print_exc()

    threading.Thread(target=_start_backend, daemon=True).start()

    try: app.mainloop()
    except KeyboardInterrupt: pass
    os._exit(0)


if __name__ == "__main__":
    main()