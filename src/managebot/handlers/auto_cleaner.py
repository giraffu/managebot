import asyncio
from telegram import Update
from telegram.ext import ContextTypes

async def auto_cleaner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await asyncio.sleep(60)  # 等待60秒
    try:
        await context.bot.delete_message(update.effective_chat.id, update.message.message_id)
    except:
        pass  # 防止权限不足报错

# 注册方式：监听特定关键词
# app.add_handler(MessageHandler(filters.TEXT & filters.Regex(".*敏感词.*"), auto_cleaner))
