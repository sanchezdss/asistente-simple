# Asistente simple

A small Spanish-first terminal assistant using the Anthropic Messages API.
Built from scratch with Python's standard library. No application framework,
database, customer records, or third-party Python dependencies.

## Status

Initial prototype created on 2026-11-11. No adoption or usage metrics yet.
Local demo and mocked API tests are available. A live API call has not been
validated in this initial version. This is a learning tool, not a production
customer support system. It cannot execute tools or access your files.

## Run without an API key

Requires Python 3.10 or newer:

```sh
python3 assistant.py --demo
```

The demo prints a clearly labelled, fixed sample conversation. It does not
use a model, access the network, or incur charges.

## Chat with Claude

Create an Anthropic API key and provide it through the `ANTHROPIC_API_KEY`
environment variable using your shell or secret manager. Never put a key in
source code, an issue, or a commit. The app does not read `.env` files.

```sh
python3 assistant.py
```

Optional model selection:

```sh
python3 assistant.py --model claude-sonnet-4-6
```

`ANTHROPIC_MODEL` also sets the default model. Access depends on your API account.
Each normal chat turn is a paid API request, including the recent conversation
context. A Claude subscription does not include API credits.

Commands: `/nuevo` clears local history; `/salir` exits. EOF and Ctrl+C also exit.
The app keeps up to six previous turns and limits input to 4000 characters and
output to 512 tokens per request. It does not retry automatically.

## Privacy and limitations

Conversation history lives in memory only; the app does not save transcripts.
Your terminal may retain output. During normal chat, your messages and recent
context are sent to Anthropic. See [Anthropic privacy information](https://privacy.claude.com/).
Do not enter sensitive data. Responses can be incorrect and need human review.

## Tests

```sh
python3 -B -m unittest discover -s tests -v
```

Tests mock the API transport. They require no credentials and spend no API credits.

## Contributing

Small, focused improvements are welcome: open an issue describing the problem,
or submit a pull request with a clear explanation and relevant tests. Use
synthetic data in examples and never include credentials or customer information.

## License and API reference

MIT — see LICENSE. Created with AI assistance.

[Messages API](https://platform.claude.com/docs/en/api/messages/create)
and [API versioning](https://platform.claude.com/docs/en/api/versioning).
