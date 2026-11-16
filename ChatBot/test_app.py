"""Offline tests for the Gemini chatbot's local features."""

import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import dotenv  # noqa: F401
except ImportError:
    dotenv_module = types.ModuleType("dotenv")
    dotenv_module.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_module

try:
    from google import genai  # noqa: F401
except ImportError:
    google_module = sys.modules.setdefault("google", types.ModuleType("google"))
    genai_module = types.ModuleType("google.genai")
    genai_module.Client = object
    google_module.genai = genai_module
    sys.modules["google.genai"] = genai_module

import fplib
from ChatBot import app


class ChatbotTests(unittest.TestCase):
    def test_imports_the_shared_root_library(self):
        project_library = Path(__file__).resolve().parents[1] / "fplib.py"
        self.assertEqual(Path(fplib.__file__).resolve(), project_library)

    def test_prepare_user_message_normalizes_and_validates(self):
        self.assertEqual(app.prepare_user_message("  HELLO   THERE "), "hello there")
        with self.assertRaises(ValueError):
            app.prepare_user_message("   ")
        with self.assertRaises(ValueError):
            app.prepare_user_message("x" * 2001)

    def test_detect_sentiment(self):
        self.assertEqual(app.detect_sentiment("I am happy and great"), "positive")
        self.assertEqual(app.detect_sentiment("Saya sedih dan kecewa"), "negative")
        self.assertEqual(app.detect_sentiment("Python list comprehension"), "neutral")

    def test_build_context_keeps_valid_messages(self):
        history = [
            {"role": "system", "text": "ignore this"},
            {"role": "user", "text": "hello python"},
            {"role": "assistant", "text": "Hello!"},
        ]
        self.assertEqual(
            app.build_context(history),
            "USER: hello python\nASSISTANT: Hello!",
        )

    def test_build_context_can_be_disabled(self):
        with patch.object(app, "MAX_CONTEXT_MESSAGES", 0):
            self.assertEqual(app.build_context([{"role": "user", "text": "hello"}]), "")

    def test_load_history_filters_invalid_records(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            history_file = Path(temporary_directory) / "history.json"
            history_file.write_text(
                json.dumps(
                    [
                        {"role": "user", "text": "hello"},
                        {"role": "system", "text": "ignore"},
                        {"role": "assistant", "text": 42},
                    ]
                ),
                encoding="utf-8",
            )
            with patch.object(app, "HISTORY_FILE", history_file):
                self.assertEqual(app.load_history(), [{"role": "user", "text": "hello"}])

    def test_rupiah_command_formats_amount(self):
        with patch("builtins.print") as print_mock:
            handled, history = app.handle_command("/rupiah 1500000", [])

        self.assertTrue(handled)
        self.assertEqual(history, [])
        print_mock.assert_called_once_with("PustakaBot: Rp1.500.000\n")

    def test_add_message_returns_a_new_history(self):
        history = [{"role": "user", "text": "hello"}]

        with patch.object(app, "save_history") as save_mock:
            updated_history = app.add_message(history, "assistant", "Hi!")

        self.assertEqual(len(history), 1)
        self.assertEqual(updated_history[-1]["text"], "Hi!")
        save_mock.assert_called_once_with(updated_history)

    def test_clear_command_clears_and_saves_history(self):
        history = [{"role": "user", "text": "hello"}]
        with patch.object(app, "save_history") as save_mock:
            handled, updated_history = app.handle_command("/clear", history)

        self.assertTrue(handled)
        self.assertEqual(history, [{"role": "user", "text": "hello"}])
        self.assertEqual(updated_history, [])
        save_mock.assert_called_once_with(updated_history)

    def test_ask_gemini_strips_response_text(self):
        class FakeModels:
            def generate_content(self, **_kwargs):
                return types.SimpleNamespace(text="  Hello!  ")

        client = types.SimpleNamespace(models=FakeModels())
        self.assertEqual(app.ask_gemini(client, [], "Hi"), "Hello!")


if __name__ == "__main__":
    unittest.main()
