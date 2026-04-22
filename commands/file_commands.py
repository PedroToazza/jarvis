"""
commands/file_commands.py — Manipulação de arquivos em pastas permitidas

Seguro: só opera dentro de Desktop, Documentos e Downloads.
"""
import os
import re
import shutil
import unicodedata


def _user_home() -> str:
    return os.path.expanduser("~")


def _onedrive_root():
    od = os.environ.get("OneDrive") or os.environ.get("OneDriveConsumer")
    return od if od and os.path.isdir(od) else None


def _safe_roots() -> list:
    home  = _user_home()
    roots = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Área de Trabalho"),
        os.path.join(home, "Documents"),
        os.path.join(home, "Documentos"),
        os.path.join(home, "Downloads"),
    ]
    od = _onedrive_root()
    if od:
        roots += [
            os.path.join(od, "Desktop"),
            os.path.join(od, "Área de Trabalho"),
            os.path.join(od, "Documents"),
            os.path.join(od, "Documentos"),
        ]
    return [r for r in roots if os.path.isdir(r)]


def _normalize(s: str) -> str:
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return s.lower().strip()


FOLDER_ALIASES = {
    "desktop":           ["Desktop", "Área de Trabalho"],
    "area de trabalho":  ["Desktop", "Área de Trabalho"],
    "areadetrabalho":    ["Desktop", "Área de Trabalho"],
    "documentos":        ["Documents", "Documentos"],
    "documents":         ["Documents", "Documentos"],
    "downloads":         ["Downloads"],
    "transferencias":    ["Downloads"],
    "transferências":    ["Downloads"],
}


def resolve_path(target: str) -> str | None:
    if not target:
        return None

    target     = target.strip().strip('/\\').strip('"').strip("'")
    parts      = re.split(r'[\\/]+', target)
    first_norm = _normalize(parts[0])

    root = None
    rest = parts[1:]

    for alias, folder_names in FOLDER_ALIASES.items():
        if first_norm == alias:
            for folder_name in folder_names:
                for candidate_root in _safe_roots():
                    if os.path.basename(candidate_root) == folder_name:
                        root = candidate_root
                        break
                if root: break
        if root: break

    if not root and os.path.isabs(target):
        real = os.path.abspath(target)
        for safe in _safe_roots():
            if real.lower().startswith(safe.lower() + os.sep) or \
               real.lower() == safe.lower():
                return real
        return None

    if not root:
        for safe in _safe_roots():
            candidate = os.path.join(safe, *parts)
            if os.path.exists(candidate):
                return candidate
        desks = [r for r in _safe_roots()
                 if os.path.basename(r) in ("Desktop", "Área de Trabalho")]
        if desks:
            return os.path.join(desks[0], *parts)
        return None

    full = os.path.join(root, *rest) if rest else root
    real = os.path.abspath(full)
    for safe in _safe_roots():
        if real.lower().startswith(safe.lower()) or real.lower() == safe.lower():
            return real
    return None


class FileCommands:
    def __init__(self, tts):
        self.tts = tts

    def create_folder(self, target: str):
        path = resolve_path(target)
        if not path:
            self.tts.speak("Só posso criar pastas dentro de Desktop, Documentos ou Downloads.")
            return
        try:
            os.makedirs(path, exist_ok=True)
            self.tts.speak(f"Pasta {os.path.basename(path)} criada.")
        except Exception as e:
            self.tts.speak("Erro ao criar a pasta.")
            print(f"  create_folder: {e}")

    def create_file(self, target: str, content: str = ""):
        path = resolve_path(target)
        if not path:
            self.tts.speak("Só posso criar arquivos dentro das pastas permitidas.")
            return
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content or "")
            name = os.path.basename(path)
            if content:
                self.tts.speak(f"Arquivo {name} criado com o conteúdo.")
            else:
                self.tts.speak(f"Arquivo {name} criado.")
        except Exception as e:
            self.tts.speak("Erro ao criar o arquivo.")
            print(f"  create_file: {e}")

    def write_file(self, target: str, content: str):
        path = resolve_path(target)
        if not path:
            self.tts.speak("Só posso escrever em arquivos dentro das pastas permitidas.")
            return
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content or "")
            self.tts.speak(f"Conteúdo escrito em {os.path.basename(path)}.")
        except Exception as e:
            self.tts.speak("Erro ao escrever no arquivo.")
            print(f"  write_file: {e}")

    def append_file(self, target: str, content: str):
        path = resolve_path(target)
        if not path:
            self.tts.speak("Só posso editar arquivos dentro das pastas permitidas.")
            return
        try:
            os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
            with open(path, 'a', encoding='utf-8') as f:
                if os.path.getsize(path) > 0:
                    f.write('\n')
                f.write(content or "")
            self.tts.speak(f"Texto adicionado em {os.path.basename(path)}.")
        except Exception as e:
            self.tts.speak("Erro ao anexar no arquivo.")
            print(f"  append_file: {e}")

    def read_file(self, target: str):
        path = resolve_path(target)
        if not path or not os.path.isfile(path):
            self.tts.speak("Arquivo não encontrado.")
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(500)
            if not content.strip():
                self.tts.speak("O arquivo está vazio.")
            else:
                self.tts.speak(f"Conteúdo: {content}")
        except Exception as e:
            self.tts.speak("Erro ao ler o arquivo.")
            print(f"  read_file: {e}")

    def delete_path(self, target: str):
        path = resolve_path(target)
        if not path or not os.path.exists(path):
            self.tts.speak("Não encontrei isso para apagar.")
            return
        try:
            name = os.path.basename(path)
            if os.path.isdir(path):
                shutil.rmtree(path)
                self.tts.speak(f"Pasta {name} apagada.")
            else:
                os.remove(path)
                self.tts.speak(f"Arquivo {name} apagado.")
        except Exception as e:
            self.tts.speak("Erro ao apagar.")
            print(f"  delete_path: {e}")

    def list_folder(self, target: str):
        path = resolve_path(target)
        if not path or not os.path.isdir(path):
            self.tts.speak("Pasta não encontrada.")
            return
        try:
            items = sorted(os.listdir(path))
            if not items:
                self.tts.speak(f"A pasta {os.path.basename(path)} está vazia.")
                return
            count = len(items)
            first = ", ".join(items[:5])
            if count <= 5:
                self.tts.speak(f"{count} itens: {first}.")
            else:
                self.tts.speak(f"{count} itens. Os primeiros são: {first}.")
        except Exception as e:
            self.tts.speak("Erro ao listar.")
            print(f"  list_folder: {e}")

    def open_folder(self, target: str):
        path = resolve_path(target)
        if not path or not os.path.exists(path):
            self.tts.speak("Pasta não encontrada.")
            return
        try:
            os.startfile(path)
            self.tts.speak(f"Abrindo {os.path.basename(path)}.")
        except Exception as e:
            self.tts.speak("Erro ao abrir.")
            print(f"  open_folder: {e}")