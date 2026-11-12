"""Minimal Spanish-first chat client. Python 3.10+, standard library only."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SYSTEM = (
    "Sos un asistente amable y conciso. Respondé en el idioma del usuario. "
    "Si no sabés algo, decilo. No afirmes haber realizado acciones externas. "
    "No solicites contraseñas ni datos de pago."
)


def ask(messages, api_key, model):
    """Send one conversation to Anthropic; never log credentials or errors bodies."""
    payload = {"model": model, "max_tokens": 512, "system": SYSTEM,
               "messages": messages}
    request = Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode(),
        headers={"x-api-key": api_key, "anthropic-version": "2026-10-21",
                 "content-type": "application/json"}, method="POST",
    )
    try:
        with urlopen(request, timeout=60) as response:
            result = json.load(response)
    except HTTPError as exc:
        hints = {401: "Revisá ANTHROPIC_API_KEY.", 403: "Acceso denegado.",
                 429: "Límite de uso alcanzado; esperá antes de reintentar.",
                 400: "Revisá el modelo y los límites de la solicitud."}
        raise RuntimeError(f"API HTTP {exc.code}. " + hints.get(exc.code, "Reintentá más tarde.")) from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError("No se pudo conectar con Anthropic.") from None
    except (ValueError, UnicodeError):
        raise RuntimeError("La API devolvió una respuesta inválida.") from None
    if not isinstance(result, dict) or not isinstance(result.get("content"), list):
        raise RuntimeError("La API devolvió una respuesta inválida.")
    answer = "\n".join(block["text"] for block in result["content"]
                       if isinstance(block, dict) and block.get("type") == "text"
                       and isinstance(block.get("text"), str)).strip()
    if not answer:
        raise RuntimeError("La API no devolvió texto.")
    if result.get("stop_reason") == "max_tokens":
        answer += "\n[Respuesta recortada por el límite de salida.]"
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Ejemplo local, sin API ni costo")
    parser.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6"))
    args = parser.parse_args()
    if args.demo:
        print("DEMO LOCAL — respuesta fija, sin conexión ni IA.")
        print("Vos: ¿Cómo organizo mis tareas?")
        print("Asistente: Elegí una prioridad, dividila en pasos y empezá por el primero.")
        return 0
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("Falta ANTHROPIC_API_KEY. Probá --demo sin credenciales.", file=sys.stderr)
        return 1
    print("Asistente simple · /salir para terminar · /nuevo para borrar el contexto")
    print("Cada mensaje se envía a Anthropic y consume saldo de API. No ingreses secretos.")
    history = []
    while True:
        try:
            question = input("Vos: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if question == "/salir":
            return 0
        if question == "/nuevo":
            history.clear()
            print("Contexto borrado.")
            continue
        if not question:
            continue
        if len(question) > 4000:
            print("Usá hasta 4000 caracteres por mensaje.")
            continue
        # Keep at most six complete previous turns; never start with an assistant.
        pending = history[-12:] + [{"role": "user", "content": question}]
        try:
            answer = ask(pending, api_key, args.model)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            continue
        except KeyboardInterrupt:
            print()
            return 0
        history = pending + [{"role": "assistant", "content": answer}]
        print("Asistente:", answer)


if __name__ == "__main__":
    sys.exit(main())
