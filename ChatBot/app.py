"""PustakaBot: a beginner-friendly terminal chatbot powered by Gemini."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai

import fplib


# --------------------------------------------------------------------------
# Konfigurasi & konstanta
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
HISTORY_FILE = BASE_DIR / "chat_history.json"
load_dotenv(BASE_DIR / ".env")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
MAX_CONTEXT_MESSAGES = max(0, int(os.getenv("MAX_CONTEXT_MESSAGES", "12")))
COMMANDS = ("/help", "/history", "/analytics", "/rupiah", "/clear", "/exit")

# Small bilingual word lists for lightweight sentiment detection.
POSITIVE_WORDS = {
    "good", "great", "happy", "love", "awesome", "excellent", "thanks",
    "thank", "senang", "bagus", "hebat", "suka", "terima", "mantap",
    "berhasil", "terbantu", "bahagia",
}
NEGATIVE_WORDS = {
    "bad", "sad", "angry", "hate", "terrible", "worried", "problem",
    "error", "susah", "buruk", "sedih", "marah", "benci", "bingung",
    "gagal", "kecewa", "sulit",
}


# --------------------------------------------------------------------------
# Penyimpanan riwayat
# --------------------------------------------------------------------------
def load_history() -> list[dict[str, Any]]:
    """Load saved conversation messages, or start with an empty history."""
    if not HISTORY_FILE.exists():
        return []
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            # Keep only well-formed message records.
            return fplib.filter_data(
                lambda item: isinstance(item, dict)
                and item.get("role") in {"user", "assistant"}
                and isinstance(item.get("text"), str),
                data,
            )
    except (json.JSONDecodeError, OSError):
        print("[Notice] Saved history could not be read; starting a new chat.")
    return []


def save_history(history: list[dict[str, Any]]) -> None:
    """Persist conversation history as readable JSON."""
    HISTORY_FILE.write_text(
        json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def add_message(
    history: list[dict[str, Any]], role: str, text: str
) -> list[dict[str, Any]]:
    message = {
        "role": role,
        "text": text,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "sentiment": detect_sentiment(text) if role == "user" else "assistant",
    }
    updated_history = history + [message]
    save_history(updated_history)
    return updated_history


# --------------------------------------------------------------------------
# Pemrosesan pesan
# --------------------------------------------------------------------------
def detect_sentiment(text: str) -> str:
    """Detect a simple positive, negative, or neutral sentiment."""
    words = fplib.bersih_teks(text, hapus_tanda_baca=True).split()
    positive_count = fplib.total_nilai(
        fplib.ubah_data(lambda word: 1 if word in POSITIVE_WORDS else 0, words)
    )
    negative_count = fplib.total_nilai(
        fplib.ubah_data(lambda word: 1 if word in NEGATIVE_WORDS else 0, words)
    )
    if positive_count > negative_count:
        return "positive"
    if negative_count > positive_count:
        return "negative"
    return "neutral"


def prepare_user_message(raw_text: str) -> str:
    """Validate and clean input through the library's functional pipeline."""
    pipeline = fplib.alur_proses(
        lambda value: value.strip(),
        lambda value: fplib.bersih_teks(value),
    )
    cleaned = pipeline(raw_text)
    valid = fplib.cek_valid(
        lambda value: isinstance(value, str) and len(value) > 0,
        [cleaned],
        mode="semua",
    )
    if not valid:
        raise ValueError("Message cannot be empty.")
    if len(cleaned) > 2000:
        raise ValueError("Please keep your message under 2,000 characters.")
    return cleaned


# --------------------------------------------------------------------------
# Konteks percakapan & Gemini
# --------------------------------------------------------------------------
def build_context(history: list[dict[str, Any]]) -> str:
    """Create a compact context string from recent user/assistant turns."""
    valid_messages = fplib.filter_data(
        lambda item: item.get("role") in {"user", "assistant"}
        and isinstance(item.get("text"), str),
        history,
    )
    if MAX_CONTEXT_MESSAGES == 0:
        return ""

    chunks = fplib.potong_data(valid_messages, 2)
    recent_chunks = chunks[-((MAX_CONTEXT_MESSAGES + 1) // 2) :]
    recent_messages = fplib.gabung_rekursif(recent_chunks)
    formatted = fplib.ubah_data(
        lambda item: f"{item['role'].upper()}: {item['text']}",
        recent_messages,
    )
    return "\n".join(formatted)


def ask_gemini(
    client: genai.Client, history: list[dict[str, Any]], question: str
) -> str:
    """Send the latest question and recent conversation context to Gemini."""
    context = build_context(history)
    system_instruction = (
        "You are PustakaBot, a friendly and helpful student assistant. "
        "Reply in the same language as the user's latest message (especially "
        "Indonesian or English). Use the conversation context to understand "
        "follow-up questions. Explain concepts clearly and avoid pretending "
        "to know facts you do not know. Keep answers reasonably concise."
    )
    prompt = (
        f"{system_instruction}\n\n"
        f"Recent conversation:\n{context or '(No earlier conversation)'}\n\n"
        f"LATEST USER MESSAGE: {question}\n\nPustakaBot:"
    )
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    return answer.strip()


# --------------------------------------------------------------------------
# Analitik percakapan
# --------------------------------------------------------------------------
def show_analytics(history: list[dict[str, Any]]) -> None:
    """Print simple statistics using the supplied functional library."""
    user_messages = fplib.filter_data(lambda item: item["role"] == "user", history)
    assistant_messages = fplib.filter_data(
        lambda item: item["role"] == "assistant", history
    )
    lengths = fplib.ubah_data(lambda item: len(item["text"]), user_messages)
    sentiment_groups = fplib.kelompok_data(
        lambda item: item.get("sentiment", "neutral"), user_messages
    )
    all_words_nested = fplib.ubah_data(
        lambda item: fplib.bersih_teks(item["text"], hapus_tanda_baca=True).split(),
        user_messages,
    )
    all_words = fplib.gabung_rekursif(all_words_nested)
    frequencies = fplib.hitung_frekuensi(all_words)
    common_words = fplib.urut_data(
        list(frequencies.items()), kunci=lambda pair: pair[1], terbalik=True
    )[:5]
    shortest, longest = fplib.nilai_ekstrem(lengths)
    average_length = fplib.rerata_nilai(lengths)
    total_characters = fplib.total_nilai(lengths)

    print("\n========== CHAT ANALYTICS ==========")
    print(f"User messages       : {len(user_messages)}")
    print(f"Bot responses       : {len(assistant_messages)}")
    print(f"Total user characters: {total_characters}")
    print(f"Average message size: {average_length:.1f} characters")
    print(f"Shortest / longest  : {shortest or 0} / {longest or 0} characters")
    print("Sentiment summary   :")
    for sentiment in ("positive", "neutral", "negative"):
        count = len(sentiment_groups.get(sentiment, []))
        print(f"  - {sentiment.title():8}: {count}")
    print("Most used words     :")
    if common_words:
        for word, count in common_words:
            print(f"  - {word}: {count}")
    else:
        print("  - No words recorded yet.")
    print("===================================\n")


# --------------------------------------------------------------------------
# Tampilan & perintah lokal
# --------------------------------------------------------------------------
def show_help() -> None:
    print(
        "\nCommands:\n"
        "  /help             Show this help\n"
        "  /history          Show recent conversation\n"
        "  /analytics        Show conversation statistics\n"
        "  /rupiah 1500000   Format a number as Indonesian Rupiah\n"
        "  /clear            Clear saved conversation history\n"
        "  /exit             Exit PustakaBot\n"
    )


def show_history(history: list[dict[str, Any]]) -> None:
    if not history:
        print("No conversation history yet.\n")
        return
    print("\n========== RECENT HISTORY ==========")
    for item in history[-10:]:
        label = "You" if item["role"] == "user" else "PustakaBot"
        print(f"{label}: {item['text']}")
    print("====================================\n")


def handle_command(
    text: str, history: list[dict[str, Any]]
) -> tuple[bool, list[dict[str, Any]]]:
    """Handle local commands and return whether one matched with updated history."""
    command = fplib.cari_item(
        lambda item: text == item or text.startswith(item + " "),
        COMMANDS,
    )
    if command is None:
        return False, history
    if command == "/help":
        show_help()
    elif command == "/history":
        show_history(history)
    elif command == "/analytics":
        show_analytics(history)
    elif command == "/rupiah":
        amount_text = text[len("/rupiah") :].strip()
        try:
            amount = float(amount_text.replace(".", "").replace(",", "."))
            print(f"PustakaBot: {fplib.format_rupiah(amount)}\n")
        except ValueError:
            print("Usage: /rupiah 1500000\n")
    elif command == "/clear":
        history = []
        save_history(history)
        print("PustakaBot: Conversation history cleared.\n")
    elif command == "/exit":
        print("PustakaBot: See you next time! Goodbye.\n")
        raise SystemExit(0)
    return True, history


# --------------------------------------------------------------------------
# Alur CLI
# --------------------------------------------------------------------------
def main() -> None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        print("Gemini API key not found.")
        print("1. Copy ChatBot/.env.example to ChatBot/.env")
        print("2. Add your key to GEMINI_API_KEY in ChatBot/.env")
        print("3. Run python -m ChatBot.app again from the repository root")
        return

    client = genai.Client(api_key=api_key)
    history = load_history()

    print("=" * 48)
    print("             PUSTAKABOT AI")
    print("       Gemini-powered terminal chatbot")
    print("=" * 48)
    print(f"Model: {MODEL_NAME}")
    print(f"Loaded {len(history)} saved messages.")
    print("Type /help to see commands, or /exit to quit.")
    print("You can chat in Indonesian or English.\n")

    while True:
        try:
            raw_text = input("You: ")
            if not raw_text.strip():
                continue
            command_text = raw_text.strip().lower()
            command_handled, history = handle_command(command_text, history)
            if command_handled:
                continue

            question = prepare_user_message(raw_text)
            sentiment = detect_sentiment(question)
            history = add_message(history, "user", question)
            print(f"[Detected sentiment: {sentiment}]")

            try:
                answer = ask_gemini(client, history[:-1], question)
            except Exception as error:  # API/network errors should not crash the CLI.
                print(f"PustakaBot: I couldn't reach Gemini: {error}\n")
                continue

            history = add_message(history, "assistant", answer)
            print(f"\nPustakaBot: {answer}\n")

        except ValueError as error:
            print(f"PustakaBot: {error}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nPustakaBot: Goodbye!")
            break


if __name__ == "__main__":
    main()
