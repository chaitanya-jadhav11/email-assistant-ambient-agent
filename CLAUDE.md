# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

An "ambient" email assistant that triages and responds to Gmail using a LangGraph workflow with human-in-the-loop (HITL) review via Agent Inbox and long-term memory of user preferences.

Python 3.12, managed with `uv`. LLM is OpenAI `gpt-4.1` (see `src/email_assistant/models/llm.py`).

## Common commands

```bash
# Install deps
uv sync

# Run the LangGraph dev server (loads graphs from langgraph.json on port 2024)
langgraph dev

# Run a module (note: uses `src.email_assistant.*` import paths)
uv run -m src.email_assistant.graphs.main_graph
uv run -m src.email_assistant.tools.gmail.setup_gmail
uv run -m src.email_assistant.tools.gmail.setup_cron --email=<email> --url "http://127.0.0.1:2024"
uv run -m src.email_assistant.db.db_test

# Run Gmail ingestion against the local LangGraph dev server (second terminal)
python src/email_assistant/tools/gmail/run_ingest.py --email <email> --minutes-since 1000
```

Pytest is a dependency but no tests currently exist in the repo. `db_test.py` is a manual script, not pytest tests.

## External dependencies that must be running

- **PostgreSQL** at `localhost:5432`, database `langgraph_db`, user `postgres`. Connection string is **hardcoded** in `src/email_assistant/db/db.py` (not read from `POSTGRES_URI` in `.env` despite `.env.example` suggesting otherwise). `init_db()` calls `store.setup()` + `checkpointer.setup()` to create tables — invoked at import time from `triage_router.py` and `interrupt_handler.py`.
- **Gmail / Calendar OAuth credentials** at `src/email_assistant/tools/gmail/.secrets/secrets.json` and `token.json` (created by `setup_gmail.py`). Scopes: `gmail.modify`, `calendar`.
- **`.env`** with at least `OPENAI_API_KEY`. Optional: `LANGSMITH_*`, `GMAIL_TOKEN`/`GMAIL_SECRET` (env-based credential fallback used by `run_ingest.py`).

## Architecture

Two graphs are exposed via `langgraph.json`:

1. **`email_assistant_gmail`** (`src/email_assistant/graphs/main_graph.py`) — the main per-email workflow.
2. **`cron`** (`src/email_assistant/graphs/cron.py`) — a single-node graph that wraps `fetch_and_process_emails` so it can be scheduled as a LangGraph Platform cron. The cron pushes each fetched email into the main graph via the LangGraph SDK.

### Main graph (outer)

`START → triage_router → {triage_interrupt_handler | response_agent | END}`

- **`triage_router`** classifies the email as `respond` / `notify` / `ignore` using `llm_router` (structured output via `RouterSchema`). It reads `triage_preferences` from the Postgres store (with `default_triage_instructions` as fallback) and uses `Command(goto=...)` to dispatch.
- **`triage_interrupt_handler`** raises a LangGraph `interrupt()` so a human can review `notify`-classified emails in Agent Inbox, then ends.
- **`response_agent`** is the inner compiled subgraph.

### Response agent (inner)

`START → llm_call → should_continue → {interrupt_handler → llm_call | mark_as_read_node → END}`

- **`llm_call`** invokes `llm_with_tools` (forced tool choice). Tools are bound in `models/llm.py`: `send_email_tool`, `schedule_meeting_tool`, `check_calendar_tool`, plus the sentinel `Question` and `Done` tools defined in `tools/base.py`. The system prompt is injected with `response_preferences` and `cal_preferences` pulled from the store.
- **`should_continue`** routes on the last message's tool calls: `Done` → `mark_as_read_node`; anything else → `interrupt_handler`.
- **`interrupt_handler`** is the HITL chokepoint. It executes non-HITL tools (e.g. `check_calendar_tool`) directly, but for `send_email_tool`/`schedule_meeting_tool`/`Question` it raises `interrupt(...)` and waits for an Agent Inbox response of type `accept` | `edit` | `ignore` | `response`. Each branch optionally calls `update_memory(...)` to evolve `response_preferences`, `cal_preferences`, or `triage_preferences` — this is the learning loop.
- **`mark_as_read_node`** calls the Gmail API to mark the thread read.

### State

`MainState` (in `graphs/states/state.py`) extends `MessagesState` with `email_input: dict` and `classification_decision`. `StateInput` is the public input shape (just `email_input`).

### Memory

`memory.py` reads/writes JSON payloads under namespaces like `("email_assistant", "triage_preferences" | "response_preferences" | "cal_preferences")`, key `"user_preferences"`. `get_memory` seeds defaults from `prompts.py` (`default_triage_instructions`, `default_response_preferences`, `default_cal_preferences`, `default_background`). `update_memory` uses a structured-output LLM call (`UserPreferences` schema) driven by `MEMORY_UPDATE_INSTRUCTIONS` to merge user feedback into the stored profile.

### Gmail ingestion flow

`run_ingest.py` (used both standalone and via the `cron` graph): builds a Gmail search query from CLI args (`--minutes-since`, `--email`, `--include-read`), fetches matching threads, applies sender / latest-in-thread filters (unless `--skip-filters`), then pushes each email into the configured LangGraph deployment via `langgraph_sdk`. See `src/email_assistant/tools/gmail/README-Gmail-Integration-Tools.md` for the full filter semantics — particularly that `--skip-filters` does **not** bypass `is:unread`.

## Repo-specific gotchas

- Imports use the full `src.email_assistant.*` path (not `email_assistant.*`). The project is installed as itself via `dependencies = ["."]` in `langgraph.json`, but module entrypoints assume the `src` prefix.
- `main_graph.py` writes PNGs of both compiled graphs to `src/graph_flow_diagram/` and calls `print_ascii()` on import — expected side effect, not dead code.
- The outer graph is compiled **without** a checkpointer (`email_assistant_graph = overall_workflow.compile()`). The commented-out line notes "checkpointer not worked with langgraph dev". The inner `response_agent` is also compiled without one. Persistence in dev relies on `.langgraph_api/` pickles managed by the dev server, not the Postgres checkpointer — even though `PostgresSaver` is wired up in `db.py`.
- `init_db()` is called at module import time from `triage_router.py` and `interrupt_handler.py`. Importing those modules without a running Postgres will fail.
- `tools/registry.py` is empty; tool resolution lives in `tools/base.py::get_tools` / `get_tools_by_name`.
- The DB connection string and the cron default `email` (`chaitanyabj@gmail.com`) are hardcoded — be aware when forking or deploying.

## Agent Inbox

After running `langgraph dev`, interrupted threads can be reviewed at https://dev.agentinbox.ai/ with:
- Deployment URL: `http://127.0.0.1:2024`
- Graph ID: `email_assistant_gmail`
