import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from managebot.message_loader import get_message
from managebot.utils.permissions import update_user_permissions
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay

async def word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        if update.effective_chat.type not in ["group", "supergroup"]:
            return

        text = update.message.text.lower()
        user_id = str(update.message.from_user.id)
        user_name = update.message.from_user.full_name
        chat_id = update.effective_chat.id

        BAD_WORDS = get_message("bad_words")

        # 加载用户数据
        status = load_user_status()
        user_info = status.get(user_id, {
            "warn_count": 0,
            "role": "normal",
            "message_count": 0
        })

        # ✅ 每发一条消息就 +1
        user_info["message_count"] += 1

        if any(word in text for word in BAD_WORDS):
            await update.message.delete()

            # 如果已经是 muted，就无需再警告或禁言
            if user_info.get("role") == "muted":
                status[user_id] = user_info
                save_user_status(status)
                return

            user_info["warn_count"] += 1

            if user_info["warn_count"] >= 3:
                user_info["role"] = "muted"
                await update_user_permissions(chat_id, int(user_id), "muted", context.bot)

                mute_text = get_message("mute_message").format(user_name=user_name)
                mute_msg = await context.bot.send_message(chat_id=chat_id, text=mute_text)
                asyncio.create_task(delete_message_after_delay(context, mute_msg.chat.id, mute_msg.message_id, 10))

            else:
                warn_text = get_message("warn_message").format(
                    user_name=user_name,
                    warn_count=user_info["warn_count"]
                )
                warn_msg = await context.bot.send_message(chat_id=chat_id, text=warn_text)
                asyncio.create_task(delete_message_after_delay(context, warn_msg.chat.id, warn_msg.message_id, 10))

        # 保存用户信息（无论是否触发敏感词）
        status[user_id] = user_info
        save_user_status(status)

    except Exception as e:
        print(f"敏感词检测异常: {e}")
