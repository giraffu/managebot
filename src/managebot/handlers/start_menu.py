from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay
import asyncio
from managebot.utils.menu import build_main_menu

async def start_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat  # 获取聊天对象
    print(f"[菜单触发] 用户 {user.id} 在聊天 {chat.id} 发送了：开始")

    # ✅ 传入用户 ID
    reply_markup = build_main_menu(str(user.id))

    sent_msg = await update.message.reply_text(
        "你好，我是机器人，请点击下方按钮开始操作：",
        reply_markup=reply_markup
    )

    # 删除原始消息和机器人消息
    asyncio.create_task(delete_message_after_delay(
        context, update.message.chat.id, update.message.message_id, delay=180
    ))
    asyncio.create_task(delete_message_after_delay(
        context, sent_msg.chat.id, sent_msg.message_id, delay=180
    ))