"""
commands/memory.py — Memória contextual persistente
"""
import json
import os
import threading
from datetime import datetime


class ConversationMemory:
    MAX_TURNS = 20
    MAX_HISTORY = 200

    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        self.turns = []
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.turns = data.get('turns', [])[-self.MAX_HISTORY:]
                    print(f"💾 Memória carregada: {len(self.turns)} turnos")
        except Exception as e:
            print(f"  Memória: erro: {e}")
            self.turns = []

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.storage_path) or '.', exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({'turns': self.turns[-self.MAX_HISTORY:]},
                          f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"  Memória salvar: {e}")

    def add(self, role: str, content: str):
        with self._lock:
            self.turns.append({
                'role': role, 'content': content,
                'timestamp': datetime.now().isoformat(timespec='seconds'),
            })
            if len(self.turns) > self.MAX_HISTORY:
                self.turns = self.turns[-self.MAX_HISTORY:]
            self._save()

    def context_messages(self, limit: int = None) -> list:
        limit = limit or self.MAX_TURNS
        return [{"role": t['role'], "content": t['content']}
                for t in self.turns[-limit:]]

    def clear(self):
        with self._lock:
            self.turns = []
            self._save()