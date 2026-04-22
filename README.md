# 🤖 Jarvis — Assistente de Voz Pessoal

Assistente de voz offline para Windows 11, feito em Python.  
Reconhece comandos por voz, detecta palmas e controla seu PC.

---

## 📁 Estrutura do projeto

```
jarvis/
├── main.py                  # ponto de entrada
├── config.py                # carrega configurações do ambiente/.env
├── listener.py              # reconhecimento de voz (Vosk)
├── clap_detector.py         # detecção de palmas
├── tts_engine.py            # síntese de voz (pyttsx3)
├── commands/
│   ├── __init__.py          # roteador de comandos
│   ├── system_commands.py   # apps, volume, brilho, arquivos
│   ├── web_commands.py      # Google, hora, data
│   └── spotify_commands.py  # controle do Spotify
├── download_model.py        # baixa o modelo de voz automaticamente
├── requirements.txt
└── build.bat                # compila para .exe
```

---

## 🚀 Instalação (passo a passo)

### 1. Pré-requisitos

- **Python 3.10+** — https://www.python.org/downloads/  
  *(marque "Add Python to PATH" na instalação)*
- **Microsoft C++ Build Tools** — necessário para compilar o PyAudio  
  https://visualstudio.microsoft.com/visual-cpp-build-tools/

### 2. Instalar dependências

Abra o terminal na pasta do projeto e execute:

```batch
pip install -r requirements.txt
```

> ⚠️ Se o `pyaudio` falhar, instale pelo pipwin:
> ```batch
> pip install pipwin
> pipwin install pyaudio
> ```

### 3. Baixar o modelo de voz (português)

```batch
python download_model.py
```

Isso baixa ~40 MB e cria a pasta `model/` automaticamente.

### 4. Configurar o Spotify *(opcional)*

> Sem o Spotify, todos os outros comandos funcionam normalmente.  
> A detecção de palmas também funciona — mas não abrirá música.

**Passo a passo:**

1. Acesse https://developer.spotify.com/dashboard  
2. Faça login com sua conta Spotify  
3. Clique em **"Create app"**  
4. Preencha qualquer nome e descrição  
5. Em **Redirect URIs**, adicione: `http://localhost:8888/callback`  
6. Copie o **Client ID** e o **Client Secret**  
7. Crie um arquivo `.env` na raiz do projeto e coloque:

```env
SPOTIFY_CLIENT_ID=cole_seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=cole_seu_client_secret_aqui
```

Na primeira execução, uma janela do navegador abrirá pedindo autorização — clique em "Aceitar".

> ⚠️ **Spotify Premium** é necessário para controle remoto de reprodução.  
> Com conta gratuita, o Spotify já precisa estar tocando ativamente.

### 5. Executar

```batch
python main.py
```

---

## 🎤 Como usar

### Ativar o Jarvis
Diga em voz alta: **"Jarvis"**  
Ele responderá *"Sim?"* — então fale seu comando.

### Comandos disponíveis

| O que dizer | O que acontece |
|---|---|
| `"Jarvis, abrir Chrome"` | Abre o Google Chrome |
| `"Jarvis, abrir Calculadora"` | Abre a calculadora |
| `"Jarvis, abrir Bloco de Notas"` | Abre o Notepad |
| `"Jarvis, pesquisar receitas de bolo"` | Abre o Google |
| `"Jarvis, que horas são?"` | Fala a hora atual |
| `"Jarvis, que dia é hoje?"` | Fala a data atual |
| `"Jarvis, volume 60"` | Ajusta volume para 60% |
| `"Jarvis, aumentar volume"` | Sobe 10% |
| `"Jarvis, diminuir brilho"` | Desce brilho 10% |
| `"Jarvis, brilho 80"` | Ajusta brilho para 80% |
| `"Jarvis, tocar Back in Black"` | Toca no Spotify |
| `"Jarvis, pausar"` | Pausa a música |
| `"Jarvis, próxima música"` | Avança faixa |
| `"Jarvis, que música está tocando?"` | Fala o nome |
| `"Jarvis, mover relatorio.pdf para C:\Docs"` | Move arquivo |
| `"Jarvis, renomear foto.jpg para viagem.jpg"` | Renomeia |
| `"Jarvis, ajuda"` | Lista os comandos |
| `"Jarvis, encerrar"` | Desliga o assistente |

### 👏 Atalho de palmas
Bata **duas palmas** rapidamente → Jarvis toca **Back in Black** do AC/DC no Spotify.

---

## 📦 Compilar para Executável

Para gerar um executável standalone (não precisa de Python instalado), use o script multiplataforma:

**Windows, macOS ou Linux:**

```bash
python build.py
```

O script vai:
- ✅ Instalar PyInstaller automaticamente (se necessário)
- ✅ Compilar um executável único para seu SO
- ✅ Copiar arquivos de configuração para a pasta `dist/`

**Resultado final:**
- Windows: `dist\Jarvis.exe`
- macOS: `dist/Jarvis`
- Linux: `dist/Jarvis`

**Próxima etapa:**
1. Navegue para a pasta `dist/`
2. Crie um arquivo `.env` (copie e edite `.env.example`)
3. Preencha com suas credenciais da API
4. Execute o Jarvis!

> **Dica:** O arquivo `.env` deve estar na mesma pasta do executável para que as credenciais sejam carregadas.

---

## ⚙️ Ajuste fino

Edite `config.py` para personalizar:

| Configuração | Padrão | Descrição |
|---|---|---|
| `WAKE_WORD` | `"jarvis"` | Palavra de ativação |
| `COMMAND_TIMEOUT` | `6` | Segundos para captar o comando |
| `CLAP_THRESHOLD` | `0.15` | Sensibilidade das palmas (↑ = menos sensível) |
| `CLAP_MAX_INTERVAL` | `0.8` | Intervalo máximo entre as duas palmas |
| `TTS_RATE` | `165` | Velocidade da voz |

### Adicionar novos aplicativos

Em `commands/system_commands.py`, adicione ao dicionário `KNOWN_APPS`:

```python
"meu app": r"C:\caminho\para\meuapp.exe",
```

---

## 🔧 Solução de problemas

| Problema | Solução |
|---|---|
| `No module named 'vosk'` | `pip install vosk` |
| `No module named 'pyaudio'` | `pipwin install pyaudio` |
| Modelo não encontrado | Execute `python download_model.py` |
| Jarvis não entende bem | Fale mais devagar; verifique o microfone |
| Palmas disparando por acidente | Aumente `CLAP_THRESHOLD` em `config.py` |
| Spotify: "Premium required" | Necessário ter Spotify Premium |
| Brilho não funciona | Alguns monitores externos não suportam |

---

## 📜 Licença

Projeto pessoal — use e modifique à vontade.
