import asyncio
from telegram import Update, Message
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay
from telegram import ChatPermissions
from managebot.message_loader import get_message
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from managebot.utils.permissions import update_user_permissions

async def welcome_and_add_user(update, context):
    status = load_user_status()
    added = False

    for member in update.message.new_chat_members:
        user_id = str(member.id)
        user_name = member.full_name

        if user_id not in status:
            status[user_id] = {"warn_count": 0, "role": "restricted", "message_count": 0}  # 默认限制成员
            added = True

        # 禁言新用户
        # 设置权限
        await update_user_permissions(
            chat_id=update.effective_chat.id,
            user_id=int(user_id),
            role=status[user_id]["role"],
            bot=context.bot
        )

        # 发送欢迎信息
        welcome_template = get_message("welcome_message")
        welcome_text = welcome_template.format(user_name=user_name)
        welcome_msg = await update.message.reply_text(welcome_text)
        asyncio.create_task(delete_message_after_delay(
            context, welcome_msg.chat.id, welcome_msg.message_id, 10
        ))

        # 发送滑块验证按钮
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("点击解锁验证", callback_data=f"verify_{user_id}")]
        ])
        verify_msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"{user_name} 请点击按钮验证以解除限制 👇",
            reply_markup=keyboard
        )
        asyncio.create_task(delete_message_after_delay(
            context, verify_msg.chat.id, verify_msg.message_id, 60
        ))

    if added:
        save_user_status(status)

async def verify_callback(update: Update, context):
    query = update.callback_query
    await query.answer()  # 显示 loading 状态

    data = query.data
    if not data.startswith("verify_"):
        return

    user_id = data.split("_")[1]
    if str(query.from_user.id) != user_id:
        await query.answer("⚠️ 你不能帮别人验证哦！", show_alert=True)
        return

    status = load_user_status()
    if user_id in status and status[user_id].get("role") == "restricted":
        # 把角色改成 normal
        status[user_id]["role"] = "normal"
        save_user_status(status)

        try:
            await update_user_permissions(
                chat_id=update.effective_chat.id,
                user_id=int(user_id),
                role="normal",
                bot=context.bot
            )
            await query.edit_message_text("✅ 验证通过，已解除限制，欢迎加入！")
        except Exception as e:
            print(f"解除禁言失败: {e}")
            await query.edit_message_text("❌ 验证失败，请联系管理员")

async def member_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = load_user_status()
    user = update.message.left_chat_member
    if user:
        user_id = str(user.id)
        if user_id in status:
            del status[user_id]
            save_user_status(status)

async def auto_delete_system_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message: Message = update.message

    # 判断是否为服务消息（加入、离开群）
    if message.new_chat_members or message.left_chat_member:
        try:
            await message.delete()
        except Exception as e:
            print(f"删除系统消息失败: {e}")