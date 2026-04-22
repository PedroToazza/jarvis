#!/usr/bin/env python3
"""
build.py — Compilar Jarvis para executável em qualquer OS
Funciona em: Windows, macOS, Linux
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


def run_command(cmd, description=""):
    """Executa comando e retorna se foi bem-sucedido."""
    if description:
        print(f"\n📦 {description}...")
    print(f"  → {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Comando não encontrado: {cmd[0]}")
        return False


def main():
    print("=" * 60)
    print("  🤖 JARVIS — BUILD MULTIPLATAFORMA")
    print("=" * 60)
    
    os_name = platform.system()
    python_exe = sys.executable
    project_dir = Path(__file__).parent
    
    print(f"\n🖥️  SO detectado: {os_name}")
    print(f"🐍 Python: {python_exe}")
    print(f"📁 Projeto: {project_dir}\n")
    
    # 0. Verificar se requirements foram instalados
    print("0️⃣  Verificando dependências de projeto...")
    try:
        import speech_recognition
        print("  ✅ Dependências do projeto instaladas")
    except ImportError:
        print("  ⚠️  Dependências do projeto não instaladas!")
        print("  Execute primeiro: pip install -r requirements.txt")
        return False
    
    # 1. Verificar/instalar PyInstaller
    print("\n1️⃣  Verificando dependências de build...")
    try:
        import PyInstaller
        print("  ✅ PyInstaller já instalado")
    except ImportError:
        print("  ⚠️  PyInstaller não encontrado, instalando...")
        if not run_command([python_exe, "-m", "pip", "install", "pyinstaller"], 
                          "Instalando PyInstaller"):
            print("❌ Falha ao instalar PyInstaller")
            print("   Tente: pip install pyinstaller")
            return False
    
    # 2. Limpar builds anteriores
    print("\n2️⃣  Limpando builds anteriores...")
    for folder in ['build', 'dist']:
        folder_path = project_dir / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"  🗑️  Removido: {folder}")
    
    for spec_file in project_dir.glob('*.spec'):
        spec_file.unlink()
        print(f"  🗑️  Removido: {spec_file.name}")
    
    # 3. Criar arquivo de especificação do PyInstaller
    print("\n3️⃣  Preparando especificação do build...")
    
    # Nome do executável
    exe_name = "Jarvis"
    
    # Argumentos base do PyInstaller
    pyinstaller_args = [
        python_exe, "-m", "PyInstaller",
        "--name", exe_name,
        "--onefile",                           # Um único executável
        "--windowed" if os_name == "Windows" else "--console",  # Interface (sem console no Windows)
        "--add-data", f"{project_dir / 'config.py'}:.",
        "--add-data", f"{project_dir / '.env.example'}:.",
        "--collect-all", "edge_tts",
        "--collect-all", "customtkinter",
        str(project_dir / "main.py"),
    ]
    
    # Adicionar ícone se existir (apenas Windows e macOS)
    icon_path = project_dir / "jarvis.ico"
    if icon_path.exists():
        if os_name == "Windows":
            pyinstaller_args.insert(6, "--icon")
            pyinstaller_args.insert(7, str(icon_path))
        elif os_name == "Darwin":
            # macOS usa .icns
            icns_path = project_dir / "jarvis.icns"
            if icns_path.exists():
                pyinstaller_args.insert(6, "--icon")
                pyinstaller_args.insert(7, str(icns_path))
    
    # 4. Compilar
    print("\n4️⃣  Compilando executável...")
    if not run_command(pyinstaller_args, f"Compilando com PyInstaller"):
        print("❌ Compilação falhou")
        return False
    
    # 5. Copiar .env.example para dist (se executável for executável)
    print("\n5️⃣  Finalizando distribuição...")
    dist_dir = project_dir / "dist"
    
    if dist_dir.exists():
        # Copiar .env.example
        src_env_example = project_dir / ".env.example"
        if src_env_example.exists():
            dst_env_example = dist_dir / ".env.example"
            shutil.copy(src_env_example, dst_env_example)
            print(f"  📋 Copiado: .env.example → dist/")
        
        # Copiar config.py se houver
        src_config = project_dir / "config.py"
        if src_config.exists():
            dst_config = dist_dir / "config.py"
            shutil.copy(src_config, dst_config)
            print(f"  ⚙️  Copiado: config.py → dist/")
    
    # 6. Caminho do executável final
    if os_name == "Windows":
        exe_file = dist_dir / f"{exe_name}.exe"
    else:
        exe_file = dist_dir / exe_name
    
    if exe_file.exists():
        print(f"\n✅ Build concluído com sucesso!")
        print(f"\n📍 Executável: {exe_file}")
        print(f"📏 Tamanho: {exe_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"\n💡 Próximas etapas:")
        print(f"  1. Crie um arquivo .env na mesma pasta do executável")
        print(f"  2. Preencha com suas credenciais (veja .env.example)")
        print(f"  3. Execute: {exe_file.name}")
        return True
    else:
        print(f"❌ Executável não foi criado em {exe_file}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
    
    # 2. Limpar builds anteriores
    print("\n2️⃣  Limpando builds anteriores...")
    for folder in ['build', 'dist']:
        folder_path = project_dir / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"  🗑️  Removido: {folder}")
    
    for spec_file in project_dir.glob('*.spec'):
        spec_file.unlink()
        print(f"  🗑️  Removido: {spec_file.name}")
    
    # 3. Criar arquivo de especificação do PyInstaller
    print("\n3️⃣  Preparando especificação do build...")
    
    # Nome do executável
    exe_name = "Jarvis"
    
    # Argumentos base do PyInstaller
    pyinstaller_args = [
        python_exe, "-m", "PyInstaller",
        "--name", exe_name,
        "--onefile",                           # Um único executável
        "--windowed" if os_name == "Windows" else "--console",  # Interface (sem console no Windows)
        "--add-data", f"{project_dir / 'config.py'}:.",
        "--add-data", f"{project_dir / '.env.example'}:.",
        "--collect-all", "edge_tts",
        "--collect-all", "customtkinter",
        str(project_dir / "main.py"),
    ]
    
    # Adicionar ícone se existir (apenas Windows e macOS)
    icon_path = project_dir / "jarvis.ico"
    if icon_path.exists():
        if os_name == "Windows":
            pyinstaller_args.insert(6, "--icon")
            pyinstaller_args.insert(7, str(icon_path))
        elif os_name == "Darwin":
            # macOS usa .icns
            icns_path = project_dir / "jarvis.icns"
            if icns_path.exists():
                pyinstaller_args.insert(6, "--icon")
                pyinstaller_args.insert(7, str(icns_path))
    
    # 4. Compilar
    print("\n4️⃣  Compilando executável...")
    if not run_command(pyinstaller_args, f"Compilando com PyInstaller"):
        print("❌ Compilação falhou")
        return False
    
    # 5. Copiar .env.example para dist (se executável for executável)
    print("\n5️⃣  Finalizando distribuição...")
    dist_dir = project_dir / "dist"
    
    if dist_dir.exists():
        # Copiar .env.example
        src_env_example = project_dir / ".env.example"
        if src_env_example.exists():
            dst_env_example = dist_dir / ".env.example"
            shutil.copy(src_env_example, dst_env_example)
            print(f"  📋 Copiado: .env.example → dist/")
        
        # Copiar config.py se houver
        src_config = project_dir / "config.py"
        if src_config.exists():
            dst_config = dist_dir / "config.py"
            shutil.copy(src_config, dst_config)
            print(f"  ⚙️  Copiado: config.py → dist/")
    
    # 6. Caminho do executável final
    if os_name == "Windows":
        exe_file = dist_dir / f"{exe_name}.exe"
    else:
        exe_file = dist_dir / exe_name
    
    if exe_file.exists():
        print(f"\n✅ Build concluído com sucesso!")
        print(f"\n📍 Executável: {exe_file}")
        print(f"📏 Tamanho: {exe_file.stat().st_size / (1024*1024):.2f} MB")
        print(f"\n💡 Próximas etapas:")
        print(f"  1. Crie um arquivo .env na mesma pasta do executável")
        print(f"  2. Preencha com suas credenciais (veja .env.example)")
        print(f"  3. Execute: {exe_file.name}")
        return True
    else:
        print(f"❌ Executável não foi criado em {exe_file}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
