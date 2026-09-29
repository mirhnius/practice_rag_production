"""
Week 7 (optional) — Telegram bot.

A thin conversational front-end over /api/v1/ask-agentic. Build this
once the agentic endpoint works and you want a mobile interface.
Docs: https://python-telegram-bot.org · get a token from @BotFather.

This is explicitly optional / stretch scope for Week 7 — the LangGraph
workflow in src/services/agents/ is the core learning goal.
"""

import requests
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to a plain-text message by calling the agentic RAG endpoint.

    TODO:
    - text = update.message.text
    - call your own running app's POST /api/v1/ask-agentic with
      {"query": text} (requests.post, or call the graph in-process if
      you'd rather not depend on the HTTP server being up)
    - await update.message.reply_text(answer, plus maybe the sources)
    """
    raise NotImplementedError


def build_bot(token: str) -> Application:
    """TODO:
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app

    Run it with app.run_polling() from a small standalone entrypoint,
    e.g. a scripts/run_telegram_bot.py you add once this works.
    """
    raise NotImplementedError
