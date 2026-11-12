import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from assistant import ask, main


class AssistantTests(unittest.TestCase):
    def test_request_and_text_blocks(self):
        response = io.BytesIO(json.dumps({"content": [
            {"type": "text", "text": "Hola"}, {"type": "text", "text": "¿Cómo estás?"}
        ]}).encode())
        with patch("assistant.urlopen", return_value=response) as transport:
            self.assertEqual(ask([{"role": "user", "content": "Hola"}], "test-only", "test-model"), "Hola\n¿Cómo estás?")
        request = transport.call_args.args[0]
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(payload["model"], "test-model")
        self.assertEqual(payload["messages"], [{"role": "user", "content": "Hola"}])

    def test_http_error_does_not_expose_response(self):
        error = HTTPError("https://api.anthropic.com", 401, "private detail", {}, io.BytesIO(b"private body"))
        with patch("assistant.urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "^API HTTP 401.*") as caught:
                ask([], "test-only", "test-model")
        self.assertNotIn("private", str(caught.exception))

    def test_network_failure(self):
        with patch("assistant.urlopen", side_effect=URLError("private detail")):
            with self.assertRaisesRegex(RuntimeError, "No se pudo conectar"):
                ask([], "test-only", "test-model")

    def test_invalid_response(self):
        for body in [b"not json", b"[]", b'{"content": []}']:
            with self.subTest(body=body), patch("assistant.urlopen", return_value=io.BytesIO(body)):
                with self.assertRaises(RuntimeError):
                    ask([], "test-only", "test-model")

    def test_demo_never_calls_network(self):
        with patch("sys.argv", ["assistant.py", "--demo"]), patch("assistant.urlopen") as transport, patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(main(), 0)
            self.assertIn("DEMO LOCAL", output.getvalue())
            transport.assert_not_called()

    def test_failed_turn_does_not_enter_history_and_reset_works(self):
        with patch("sys.argv", ["assistant.py"]), patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-only"}), patch("builtins.input", side_effect=["fallo", "hola", "/nuevo", "otra", "/salir"]), patch("assistant.ask", side_effect=[RuntimeError("Error"), "Hola", "Hola otra vez"]) as api, patch("sys.stdout", new_callable=io.StringIO), patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(main(), 0)
            self.assertEqual(api.call_args_list[1].args[0], [{"role": "user", "content": "hola"}])
            self.assertEqual(api.call_args_list[2].args[0], [{"role": "user", "content": "otra"}])


if __name__ == "__main__":
    unittest.main()
