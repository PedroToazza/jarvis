"""
commands/ai_parser.py — Gemini 1.5 Flash (Google, grátis 1500 req/dia)
"""
import json
import config

try:
    import google.generativeai as genai
    _GEMINI_OK = True
except ImportError:
    _GEMINI_OK = False


SYSTEM_PROMPT = """Você é o parser de comandos de voz do Jarvis em português brasileiro.
Retorne APENAS JSON no formato: { "actions": [ {"action": "...", "target": "..."}, ... ] }

REGRA CRÍTICA: Se o comando não for claro ou não bater com NENHUMA ação abaixo, retorne {"actions":[{"action":"chat","target":"<texto original>"}]}. NUNCA invente ou devolva múltiplas ações quando o usuário falou apenas uma coisa.

AÇÕES:
- "open_app": abrir app (target: chrome, google, spotify, vscode, calculadora, configurações, wifi, bluetooth, bloco de notas, gerenciador de tarefas)
- "open_url": abrir site (target: URL com https://)
- "close": fechar app ou aba (target: nome)
- "minimize": minimizar janela (target: nome do app, ou "todas")
- "search_google" (target: consulta)
- "search_youtube" (target: consulta)
- "spotify_play" (target: música), "spotify_playlist", "spotify_album", "spotify_artist"
- "spotify_pause", "spotify_resume", "spotify_next", "spotify_prev", "spotify_current"
- "set_volume" (target: 0-100, "up", "down", "mute", "unmute")
- "set_brightness" (target: 0-100, "up", "down")
- "set_timer" (target: "10 minutos")
- "set_reminder" (target: "duração|mensagem")
- "screenshot" (sem target)
- "file_create_folder" (target: "desktop/nome")
- "file_create" / "file_write" / "file_append" (target: "caminho|conteudo")
- "file_read" / "file_delete" / "file_list" / "file_open" (target: caminho)
- "tell_time", "tell_date", "help", "exit"
- "chat" (target: a pergunta) — para QUALQUER pergunta ou conversa
- "explain_more" — se usuário pedir "me explica mais", "conta mais", "detalha"

REGRAS:
- "google" / "abrir google" → SEMPRE {"action":"open_app","target":"google"}
- NUNCA abra configurações quando pedirem "google"
- SITES populares (youtube, gmail, netflix, github, facebook, instagram) → open_url
- APPS e CONFIGURAÇÕES → open_app
- PERGUNTAS → chat
- Arquivos com prefixo "desktop/", "documentos/" ou "downloads/"
- Responda APENAS o JSON.

EXEMPLOS:
"abrir google" → {"actions":[{"action":"open_app","target":"google"}]}
"abrir chrome" → {"actions":[{"action":"open_app","target":"chrome"}]}
"abrir calculadora e bloco de notas" → {"actions":[{"action":"open_app","target":"calculadora"},{"action":"open_app","target":"bloco de notas"}]}
"abrir youtube" → {"actions":[{"action":"open_url","target":"https://youtube.com"}]}
"fechar chrome" → {"actions":[{"action":"close","target":"chrome"}]}
"minimizar tudo" → {"actions":[{"action":"minimize","target":"todas"}]}
"minimizar chrome" → {"actions":[{"action":"minimize","target":"chrome"}]}
"pesquisar vídeos de slime no youtube" → {"actions":[{"action":"search_youtube","target":"vídeos de slime"}]}
"tocar Metallica" → {"actions":[{"action":"spotify_artist","target":"Metallica"}]}
"volume 50" → {"actions":[{"action":"set_volume","target":"50"}]}
"timer de 10 minutos" → {"actions":[{"action":"set_timer","target":"10 minutos"}]}
"tirar print" → {"actions":[{"action":"screenshot","target":""}]}
"qual a capital do Japão" → {"actions":[{"action":"chat","target":"qual a capital do Japão"}]}
"me explica mais" → {"actions":[{"action":"explain_more","target":""}]}
"conta mais detalhes" → {"actions":[{"action":"explain_more","target":""}]}
"que horas são" → {"actions":[{"action":"tell_time","target":""}]}
"encerrar" → {"actions":[{"action":"exit","target":""}]}
"""


CHAT_SHORT = (
    "Você é o Jarvis, assistente pessoal em português brasileiro. "
    "Responda de forma DIRETA e CURTA: máximo 1-2 frases, como se falasse "
    "em voz alta. Sem markdown, listas ou formatação. Vá direto ao ponto."
)

CHAT_DETAILED = (
    "Você é o Jarvis, assistente pessoal em português brasileiro. "
    "Dê uma resposta MAIS DETALHADA desta vez, com 3-5 frases explicando bem. "
    "Continue natural (sem markdown/listas). Parágrafo fluente."
)


class AIParser:
    def __init__(self):
        self.client = None
        self._last_question = None
        self._last_answer = None

        api_key = getattr(config, 'GEMINI_API_KEY', '').strip()
        if not _GEMINI_OK:
            print("ℹ️  'google-generativeai' não instalado."); return
        if not api_key or "COLE_SUA_CHAVE" in api_key:
            print("ℹ️  GEMINI_API_KEY ausente."); return
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self.client = True
            print("🧠 IA ativa (Gemini 1.5 Flash)")
        except Exception as e:
            print(f"⚠️  Gemini: {e}")

    def available(self) -> bool:
        return self.client is not None

    def parse(self, text: str):
        if not self.client: return None
        try:
            prompt = f"{SYSTEM_PROMPT}\n\nComando: \"{text}\"\n\nJSON:"
            resp = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0,
                    "max_output_tokens": 400,
                    "response_mime_type": "application/json",
                })
            data = json.loads(resp.text.strip())
            actions = data.get("actions") or []
            if not actions and "action" in data:
                actions = [{"action": data["action"], "target": data.get("target", "")}]
            clean = []
            for a in actions:
                act = str(a.get("action", "")).strip()
                tgt = str(a.get("target", "")).strip()
                if act: clean.append({"action": act, "target": tgt})
            if len(clean) > 5:
                print(f"  ⚠️  IA devolveu {len(clean)} ações (bug). Tratando como chat.")
                return [{"action": "chat", "target": text}]
            if clean:
                desc = " | ".join(f"{a['action']}→{a['target'][:30]}" for a in clean)
                print(f"  🧠 IA: {desc}")
            return clean or None
        except Exception as e:
            print(f"  IA parse: {e}")
            return None

    def chat(self, text: str, detailed: bool = False):
        if not self.client: return None
        try:
            system = CHAT_DETAILED if detailed else CHAT_SHORT
            prompt = f"{system}\n\nPergunta: {text}\n\nResposta:"
            resp = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 350 if detailed else 120,
                })
            answer = resp.text.strip()
            if not detailed:
                self._last_question = text
                self._last_answer = answer
            return answer
        except Exception as e:
            print(f"  Chat erro: {e}")
            return None

    def explain_more(self):
        if not self._last_question:
            return "Não tenho nada para explicar agora."
        return self.chat(self._last_question, detailed=True)