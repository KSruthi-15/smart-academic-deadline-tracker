
import asyncio
import streamlit as st
from telegram import Bot


async def _send_message(token, chat_id, message):
    async with Bot(token=token) as bot:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
        )


def send_telegram(message):
    try:
        asyncio.run(
            _send_message(
                st.secrets["TELEGRAM_BOT_TOKEN"],
                st.secrets["TELEGRAM_CHAT_ID"],
                message,
            )
        )
        return True, "Deadline reminder sent to Telegram!"

    except Exception as error:
        return False, f"Telegram error: {error}"
