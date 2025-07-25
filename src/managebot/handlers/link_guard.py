import re
from telegram import Update
from telegram.ext import ContextTypes

link_pattern = re.compile(r"(https?://\S+|t\.me/\S+)")

async def link_guard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = await context.bot.get_chat_member(update.effective_chat.id, update.message.from_user.id)
    if member.status in ["administrator", "creator"]:
        return
    
    if link_pattern.search(update.message.text):
        await update.message.delete()
        await update.message.reply_text(f"{update.message.from_user.full_name}，禁止发布邀请链接！")