@echo off
chcp 65001 > nul
setlocal

echo.
echo  ========================================================
echo    Compilando Jarvis.exe (pode demorar alguns minutos)
echo  ========================================================
echo.

python -m pip install pyinstaller -q

if exist "build\"  rmdir /s /q "build"
if exist "dist\"   rmdir /s /q "dist"
if exist "Jarvis.spec" del "Jarvis.spec"

for /f "delims=" %%A in ('python -c "import customtkinter, os; print(os.path.dirname(customtkinter.__file__))"') do set "CTK_PATH=%%A"

echo  customtkinter em: %CTK_PATH%
echo.
echo  Compilando...
echo.

pyinstaller ^
  --onefile ^
  --noconsole ^
  --name "Jarvis" ^
  --add-data "%CTK_PATH%;customtkinter/" ^
  --hidden-import "tkinter" ^
  --hidden-import "pyaudio" ^
  --hidden-import "pyttsx3" ^
  --hidden-import "pyttsx3.drivers" ^
  --hidden-import "pyttsx3.drivers.sapi5" ^
  --hidden-import "edge_tts" ^
  --hidden-import "pygame" ^
  --hidden-import "speech_recognition" ^
  --hidden-import "faster_whisper" ^
  --hidden-import "spotipy" ^
  --hidden-import "pycaw" ^
  --hidden-import "comtypes" ^
  --hidden-import "screen_brightness_control" ^
  --hidden-import "PIL" ^
  --hidden-import "psutil" ^
  --hidden-import "pygetwindow" ^
  --hidden-import "pyautogui" ^
  --hidden-import "customtkinter" ^
  --hidden-import "groq" ^
  --collect-all "customtkinter" ^
  --collect-all "speech_recognition" ^
  main.py

echo.
if exist "dist\Jarvis.exe" (
    echo  ========================================================
    echo    SUCESSO! Arquivo em: dist\Jarvis.exe
    echo  ========================================================
    echo.
    echo  IMPORTANTE: copie o config.py para a mesma pasta do .exe
) else (
    echo  [ERRO] Compilacao falhou. Veja o log acima.
)

echo.
pause