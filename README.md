# 🤖 Jarvis — Assistente de Voz Pessoal

Assistente de voz offline para Windows 11, feito em Python.  
Reconhece comandos por voz, detecta palmas e controla seu PC.

---

## 📁 Estrutura do projeto

```
jarvis/
├── main.py                  # ponto de entrada
├── config.py                # carrega configurações do ambiente/.env
├── build.py                 # compila para executável (Windows/macOS/Linux)
├── .env.example             # template de variáveis de ambiente
├── .gitignore               # ignora .env e arquivos sensíveis
├── listener.py              # reconhecimento de voz (Vosk)
├── clap_detector.py         # detecção de palmas
├── tts_engine.py            # síntese de voz (pyttsx3/Edge-TTS)
├── gui.py                   # interface gráfica (customtkinter)
├── commands/
│   ├── __init__.py          # roteador de comandos
│   ├── ai_parser.py         # parser IA (Gemini)
│   ├── system_commands.py   # apps, volume, brilho, arquivos
│   ├── web_commands.py      # Google, hora, data
│   ├── spotify_commands.py  # controle do Spotify
│   └── outros...
├── requirements.txt         # dependências Python
└── README.md                # este arquivo
```

---

## 🚀 Instalação (passo a passo)

### 1. Pré-requisitos

- **Python 3.10+** — https://www.python.org/downloads/  
  *(marque "Add Python to PATH" na instalação)*
- **Git** — para clonar o repositório

**Dependências do sistema (opcional, para desenvolvimento local):**
- **Windows:** Microsoft C++ Build Tools (https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- **Linux:** `sudo dnf install python3-tkinter` (Fedora) ou `sudo apt install python3-tk` (Ubuntu)
- **macOS:** já incluído

### 2. Instalar o Jarvis

```bash
# Clonar o repositório
git clone https://github.com/PedroToazza/jarvis.git
cd jarvis

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env com suas credenciais
cp .env.example .env
# Abra .env e preencha com suas chaves de API
```

### 3. Configurar as APIs

Veja a seção **"🔐 Configuração de APIs (Segura)"** abaixo para obter suas chaves.

### 4. Executar

```bash
python main.py
```

O Jarvis iniciará e estará pronto para receber comandos por voz!

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

## 🔐 Configuração de APIs (Segura)

As credenciais da API são carregadas de um arquivo `.env` **que não é versionado no Git** — mantendo suas chaves seguras!

### Arquivo `.env` — como usar

1. **Crie um arquivo `.env` na raiz do projeto:**

```bash
cp .env.example .env
```

2. **Edite o `.env` com suas credenciais reais:**

```env
# Google Gemini (IA)
GEMINI_API_KEY=sua_chave_gemini_aqui

# Spotify (opcional)
SPOTIFY_CLIENT_ID=seu_client_id_aqui
SPOTIFY_CLIENT_SECRET=seu_client_secret_aqui
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

### Obter as Chaves

**Google Gemini (IA gratuita — 1500 requisições/dia):**
1. Acesse https://aistudio.google.com/apikey
2. Clique em "Get API Key" / "Create API Key"
3. Copie a chave e cole em `GEMINI_API_KEY` no `.env`

**Spotify (Opcional — para controlar música):**
1. Acesse https://developer.spotify.com/dashboard
2. Faça login com sua conta Spotify
3. Clique em "Create App"
4. Preencha nome e descrição
5. Em **Redirect URIs**, adicione: `http://localhost:8888/callback`
6. Copie **Client ID** e **Client Secret**
7. Cole em `SPOTIFY_CLIENT_ID` e `SPOTIFY_CLIENT_SECRET` no `.env`

### ⚠️ Segurança

- ✅ Arquivo `.env` está em `.gitignore` — **nunca será versionado**
- ✅ Use `.env.example` como template
- ✅ **Nunca** coloque credenciais direto no código
- ✅ Se vazar uma chave, revogue no painel da API

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

### Erro: `ModuleNotFoundError: No module named 'X'`

Se receber um erro dizendo que um módulo não está instalado:

| Módulo | Solução |
|---|---|
| `tkinter` | `sudo dnf install python3-tkinter` (Fedora/RHEL) ou `sudo apt install python3-tk` (Ubuntu) |
| `pyaudio` | `pip install pipwin && pipwin install pyaudio` |
| `pyttsx3` | `pip install pyttsx3` |
| `vosk` | `pip install vosk` |
| qualquer outro | `pip install <nome_do_modulo>` |

**O Jarvis roda mesmo sem alguns módulos opcionais:**
- Sem `tkinter` → executa em modo texto (sem interface gráfica)
- Sem `pyttsx3` → responde apenas em texto (sem áudio local)
- Sem `spotipy` → comandos Spotify não funcionam

### Outros problemas

| Problema | Solução |
|---|---|
| Modelo de voz não encontrado | Execute `python download_model.py` |
| Jarvis não entende bem | Fale mais devagar; verifique o microfone |
| Palmas disparando por acidente | Aumente `CLAP_THRESHOLD` em `config.py` |
| Spotify: "Premium required" | Necessário ter Spotify Premium |
| Brilho não funciona | Alguns monitores externos não suportam |
| Build.py não funciona | Execute `pip install pyinstaller` e tente novamente |

---

## 💾 Desenvolvimento Local

### Clonar o repositório

```bash
git clone https://github.com/PedroToazza/jarvis.git
cd jarvis
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais
python main.py
```

### Criar executável

```bash
python build.py
```

---

## 📋 Checklist para novos usuários

- [ ] Python 3.10+ instalado
- [ ] Dependências instaladas: `pip install -r requirements.txt`
- [ ] Arquivo `.env` criado (copie `.env.example`)
- [ ] Credenciais das APIs preenchidas no `.env`
- [ ] Modelo de voz baixado: `python download_model.py`
- [ ] Teste com: `python main.py`
- [ ] Build (opcional): `python build.py`

---

## 📜 Licença

Projeto pessoal — use e modifique à vontade.
