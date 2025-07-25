#exportdata.py
from telegram import Update
from telegram.ext import ContextTypes
from managebot.utils.exporter import export_user_data
import config

async def export_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user
    status_message = await update.message.reply_text("📦 正在准备导出数据...")

    try:
        member = await context.bot.get_chat_member(chat.id, user.id)
        print(f"member.status: {member.status}")
        if member.status not in ["administrator", "creator"]:
            await status_message.edit_text("❌ 你没有权限使用此命令。")
            return

        # ✅ 自定义进度回调
        async def progress_callback(current, total):
            percent = (current / total) * 100 if total else 0
            await status_message.edit_text(
                f"📊 消息处理进度：{current}/{total} 条 ({percent:.1f}%)"
            )

        await export_user_data(chat.id, progress_callback=progress_callback)
        await status_message.edit_text("✅ 数据导出完成！")

    except Exception as e:
        await status_message.edit_text(f"❌ 导出失败：{e}")
