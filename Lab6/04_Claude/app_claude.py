import os
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
import uuid
import anthropic

# =========================
# Environment Variables
# =========================

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
CLAUDE_MODEL = os.getenv(
    "CLAUDE_MODEL",
    "claude-opus-5-5",
)

if not ANTHROPIC_API_KEY:
    raise RuntimeError(
        "找不到 ANTHROPIC_API_KEY，請先在 .env 填入 API Key。"
    )


if not SECRET_KEY or SECRET_KEY == "CHANGE_ME":
    raise RuntimeError(
        "請在 .env 設定安全的 SECRET_KEY。"
    )


# =========================
# Flask
# =========================

app = Flask(
    __name__,
    template_folder="templates_claude",
    static_folder="static_claude",
)
app.secret_key = SECRET_KEY


# Lab 用簡化帳號
# 正式系統不應以明文保存密碼
USERS = {
    "admin": "1234",
}


# =========================
# Claude
# =========================

claude_client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
    timeout=120.0,
    max_retries=1,
)

# 對話歷史存在伺服器的記憶體裡
# key 是對話編號，value 是這段對話的訊息清單
CONVERSATIONS = {}


def ask_claude(message, history):

    messages = history + [
        {"role": "user", "content": message}
    ]

    params = {
        "model": CLAUDE_MODEL,
        "max_tokens": 16000,
        "output_config": {"effort": "low"},
        "messages": messages,
    }

    # 模型拒答時，由 API 自動改用備援模型重試
    # Haiku 沒有這個功能，所以不送
    if "haiku" not in CLAUDE_MODEL:
        params["betas"] = ["server-side-fallback-2026-07-01"]
        params["fallbacks"] = "default"

    response = claude_client.beta.messages.create(
        **params
    )

    # 拒答時 content 可能是空的，要先檢查
    # 回傳原本的 history，這一輪就不會被記住
    if response.stop_reason == "refusal":
        return "Claude 無法回答這個問題，請換個方式提問。", history

    reply = "".join(
        block.text
        for block in response.content
        if block.type == "text"
    ).strip()

    if not reply:
        reply = "Claude 沒有回傳文字內容。"

    # 要存完整的 response.content，不能只存文字
    new_history = messages + [
        {"role": "assistant", "content": response.content}
    ]

    return reply, new_history



# =========================
# Login Required
# =========================

def login_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user" not in session:

            # API 不做 redirect
            if request.path.startswith("/api/"):
                return jsonify({
                    "error": "請先登入"
                }), 401

            return redirect(
                url_for("login")
            )

        return view(*args, **kwargs)

    return wrapped


# =========================
# Login
# =========================

@app.route(
    "/",
    methods=["GET", "POST"],
)
def login():

    if request.method == "POST":

        username = (
            request.form
            .get("username", "")
            .strip()
        )

        password = request.form.get(
            "password",
            "",
        )

        if (
            username in USERS
            and USERS[username] == password
        ):

            session.clear()

            session["user"] = username

            return redirect(
                url_for("chat_room")
            )

        return render_template(
            "login.html",
            msg="帳號或密碼錯誤",
        )

    if "user" in session:
        return redirect(
            url_for("chat_room")
        )

    return render_template(
        "login.html"
    )


# =========================
# Chat Page
# =========================

@app.get("/chat")
@login_required
def chat_room():

    return render_template(
        "chat.html",
        username=session["user"],
    )


# =========================
# Claude API
# =========================

@app.post("/api/chat")
@login_required
def api_chat():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    message = str(
        data.get("message", "")
    ).strip()

    if not message:
        return jsonify({
            "error": "訊息不可為空"
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "訊息過長"
        }), 400

    # 取得對話編號，第一次聊天時建立一個
    conversation_id = session.get("conversation_id")

    if not conversation_id:
        conversation_id = uuid.uuid4().hex
        session["conversation_id"] = conversation_id

    history = CONVERSATIONS.get(conversation_id, [])

    try:

        reply, new_history = ask_claude(message, history)

        CONVERSATIONS[conversation_id] = new_history

        return jsonify({
            "reply": reply
        })

    except anthropic.AuthenticationError as error:

        print("[Claude API Error]", error.status_code, error.message)

        return jsonify({
            "error": "Claude API Key 無效，請檢查 .env。"
        }), 502

    except anthropic.RateLimitError as error:

        print("[Claude API Error]", error.status_code, error.message)

        return jsonify({
            "error": "請求太頻繁，請稍後再試。"
        }), 429

    except anthropic.APIStatusError as error:

        print("[Claude API Error]", error.status_code, error.message)

        return jsonify({
            "error": "Claude API 呼叫失敗，請看伺服器終端機的訊息。"
        }), 502

    except anthropic.APIConnectionError as error:

        print("[Claude API Error]", type(error).__name__)

        return jsonify({
            "error": "連不到 Claude，請檢查網路後再試。"
        }), 502



# =========================
# Reset Conversation
# =========================

@app.post("/api/reset")
@login_required
def reset_chat():

    conversation_id = session.pop("conversation_id", None)
    CONVERSATIONS.pop(conversation_id, None)


    return jsonify({
        "ok": True
    })


# =========================
# Logout
# =========================

@app.post("/logout")
@login_required
def logout():

    CONVERSATIONS.pop(session.get("conversation_id"), None)

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================
# Run Server
# =========================

if __name__ == "__main__":

    print(
        "=== Lab6 Flask Server ==="
    )

    print(
        "Listening on "
        "http://0.0.0.0:3000"
    )

    print(
        "Debug mode is OFF"
    )

    app.run(
        host="0.0.0.0",
        port=3000,
        debug=False,
    )
