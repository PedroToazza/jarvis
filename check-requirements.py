#!/usr/bin/env python3
"""
check-requirements.py — Verifica se todas as dependências estão instaladas
Rode isto ANTES de tentar 'python main.py' ou 'python build.py'
"""
import sys
import subprocess
from pathlib import Path


REQUIRED_MODULES = [
    'speech_recognition',
    'faster_whisper',
    'pyaudio',
    'pyttsx3',
    'edge_tts',
    'pygame',
    'groq',
    'spotipy',
    'pycaw',
    'screen_brightness_control',
    'comtypes',
    'PIL',  # Pillow
    'psutil',
    'pygetwindow',
    'pyautogui',
    'customtkinter',
    'numpy',
]

OPTIONAL_MODULES = [
    'google.generativeai',  # Gemini IA
    'tkinter',  # GUI (sistema)
]


def check_module(module_name):
    """Verifica se um módulo está instalado."""
    # Tratar casos especiais
    import_name = module_name
    if module_name == 'PIL':
        import_name = 'PIL'
    elif module_name == 'google.generativeai':
        import_name = 'google.generativeai'
    elif module_name == 'speech_recognition':
        import_name = 'speech_recognition'
    elif module_name == 'faster_whisper':
        import_name = 'faster_whisper'
    elif module_name == 'screen_brightness_control':
        import_name = 'screen_brightness_control'
    elif module_name == 'pygetwindow':
        import_name = 'pygetwindow'
    elif module_name == 'pyautogui':
        import_name = 'pyautogui'
    elif module_name == 'customtkinter':
        import_name = 'customtkinter'
    
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False


def main():
    print("=" * 70)
    print("  🔍 VERIFICADOR DE DEPENDÊNCIAS — JARVIS")
    print("=" * 70)
    
    # Verificar Python
    print(f"\n🐍 Python: {sys.version.split()[0]} ({sys.executable})")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ requerido!")
        return False
    print("✅ Python OK")
    
    # Verificar pip
    print("\n📦 Verificando pip...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip OK")
    except Exception as e:
        print(f"❌ pip não encontrado: {e}")
        print("   No Fedora: sudo dnf install python3-pip")
        print("   No Ubuntu: sudo apt install python3-pip")
        return False
    
    # Verificar módulos obrigatórios
    print("\n📋 Módulos obrigatórios:")
    missing_required = []
    for module in sorted(REQUIRED_MODULES):
        if check_module(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ❌ {module}")
            missing_required.append(module)
    
    # Verificar módulos opcionais
    print("\n📋 Módulos opcionais:")
    for module in sorted(OPTIONAL_MODULES):
        if check_module(module):
            print(f"  ✅ {module}")
        else:
            print(f"  ⚠️  {module} (opcional)")
    
    # Resultado final
    print("\n" + "=" * 70)
    if missing_required:
        print(f"❌ FALTAM {len(missing_required)} DEPENDÊNCIAS!")
        print("\nPara instalar todas as dependências, execute:")
        print("\n  pip install -r requirements.txt\n")
        return False
    else:
        print("✅ TODAS AS DEPENDÊNCIAS ESTÃO INSTALADAS!")
        print("\nVocê pode agora executar:")
        print("  • python main.py       (iniciar Jarvis)")
        print("  • python build.py      (compilar executável)")
        print()
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
