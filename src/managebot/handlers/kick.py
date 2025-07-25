from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("请回复需要踢出的用户消息后再使用此命令")
        return
    
    user_to_kick = update.message.reply_to_message.from_user
    await context.bot.ban_chat_member(update.effective_chat.id, user_to_kick.id)
    await update.message.reply_text(f"已将 {user_to_kick.full_name} 移出群聊")

# 注册方式
# app.add_handler(CommandHandler("kick", kick))
