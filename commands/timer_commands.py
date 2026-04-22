"""
commands/timer_commands.py — Timer e lembretes por voz
"""
import re
import threading
import time


WORD_NUMS = {
    'zero': 0, 'um': 1, 'uma': 1, 'dois': 2, 'duas': 2,
    'três': 3, 'tres': 3, 'quatro': 4, 'cinco': 5,
    'seis': 6, 'sete': 7, 'oito': 8, 'nove': 9, 'dez': 10,
    'onze': 11, 'doze': 12, 'quinze': 15, 'vinte': 20,
    'trinta': 30, 'quarenta': 40, 'cinquenta': 50, 'sessenta': 60,
    'meia': 0.5, 'meio': 0.5,
}


def parse_duration(text: str):
    if not text:
        return None
    t = text.lower().strip()
    for word, num in WORD_NUMS.items():
        t = re.sub(rf'\b{word}\b', str(num), t)
    t = t.replace(',', '.')
    m = re.search(r'([\d\.]+)', t)
    if not m:
        return None
    try:
        value = float(m.group(1))
    except ValueError:
        return None
    if 'hora' in t:
        return value * 60.0
    if 'seg' in t:
        return value / 60.0
    return value


def format_duration(minutes: float) -> str:
    if minutes < 1:
        return f"{int(round(minutes * 60))} segundos"
    if minutes == 1:
        return "1 minuto"
    if minutes < 60:
        if minutes == int(minutes):
            return f"{int(minutes)} minutos"
        return f"{minutes:.1f} minutos"
    hours = minutes / 60
    return f"{hours:g} hora" + ("s" if hours != 1 else "")


class TimerCommands:
    def __init__(self, tts):
        self.tts = tts

    def set_timer(self, text: str):
        minutes = parse_duration(text)
        if minutes is None or minutes <= 0:
            self.tts.speak("Não entendi o tempo. Exemplo: timer de 10 minutos.")
            return
        seconds = minutes * 60
        formatted = format_duration(minutes)

        def _fire():
            time.sleep(seconds)
            self.tts.speak(f"Timer terminado! Já se passaram {formatted}.")

        threading.Thread(target=_fire, daemon=True).start()
        self.tts.speak(f"Timer de {formatted} iniciado.")

    def set_reminder(self, text: str):
        if '|' in text:
            time_part, message = text.split('|', 1)
        else:
            m = re.search(
                r'(?:em|daqui|após|apos)\s+(.+?)\s+(?:de|para|que)\s+(.+)',
                text.lower()
            )
            if m:
                time_part, message = m.group(1), m.group(2)
            else:
                time_part, message = text, "lembrete"

        minutes = parse_duration(time_part)
        if minutes is None or minutes <= 0:
            self.tts.speak("Não entendi o tempo do lembrete.")
            return

        seconds   = minutes * 60
        message   = message.strip() or "lembrete"
        formatted = format_duration(minutes)

        def _fire():
            time.sleep(seconds)
            self.tts.speak(f"Lembrete: {message}")

        threading.Thread(target=_fire, daemon=True).start()
        self.tts.speak(f"Vou te lembrar em {formatted}.")