from telegram import Update, Message
from telegram.ext import Application, MessageHandler, filters, ContextTypes

async def auto_delete_system_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message

    # 判断是否为服务消息（加入、离开群）
    if message.new_chat_members or message.left_chat_member:
        try:
            await message.delete()
        except Exception as e:
            print(f"删除系统消息失败: {e}")