from telegram import Update
from telegram.ext import ContextTypes
from managebot.utils.menu import build_main_menu, build_file_menu
from managebot.utils.message_tools import delete_message_after_delay
import asyncio

async def start_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    chat_type = chat.type  # "private", "group", "supergroup", etc.

    print(f"[菜单触发] 用户 {user.id} 在聊天 {chat.id}（类型: {chat_type}）发送了 /start")

    # 根据聊天类型构建菜单
    if chat_type == "private":
        reply_markup = build_file_menu(str(user.id))  # 私聊显示视频菜单
        welcome_text = "你好，这是视频菜单，请点击选择视频："
    else:
        reply_markup = build_main_menu(str(user.id))   # 群聊显示主菜单
        welcome_text = "你好，我是机器人，请点击下方按钮开始操作："

    sent_msg = await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    # 根据聊天类型构建菜单
    if chat_type != "private":
        # 删除原始消息和机器人消息（可选）
        asyncio.create_task(delete_message_after_delay(
            context, chat.id, update.message.message_id, delay=180
        ))
        asyncio.create_task(delete_message_after_delay(
            context, chat.id, sent_msg.message_id, delay=180
        ))
