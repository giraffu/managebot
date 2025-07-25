from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay
import asyncio

# ===== 回调按钮对应的处理函数 =====

async def handle_query_info(query, user_id: str):
    try:
        user_data = load_user_status()

        if user_id in user_data:
            info = user_data[user_id]
            signed_up = info.get("signed_up", False)

            return (
                f"【用户信息】\n"
                f"用户 ID：{user_id}\n"
                f"身份：{info['role']}\n"
                f"警告次数：{info['warn_count']}\n"
                f"发言次数：{info['message_count']}\n"
                f"报名状态：{'✅ 已报名' if signed_up else '❌ 未报名'}"
            )
        else:
            return "未找到你的记录。"
    except Exception as e:
        return f"读取用户数据失败：{e}"

async def handle_sign_up(query, user_id: str):
    try:
        user_data = load_user_status()

        if user_id not in user_data:
            user_data[user_id] = {
                "warn_count": 0,
                "role": "normal",
                "message_count": 0
            }

        user_data[user_id]["signed_up"] = True
        save_user_status(user_data)

        return "✅ 报名成功！你现在已报名。"
    except Exception as e:
        return f"报名失败：{e}"
    
# ===== callback_data 到处理函数的映射 =====

callback_handlers = {
    'btn1': handle_query_info,
    'btn2': handle_sign_up
}

# 用户发送“开始”时触发
async def start_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"[菜单触发] 用户 {user.id} 发送了：开始")

    keyboard = [
        [InlineKeyboardButton("查询信息", callback_data='btn1')],
        [InlineKeyboardButton("报名", callback_data='btn2')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    sent_msg = await update.message.reply_text(
        "你好，我是机器人，请点击下方按钮开始操作：",
        reply_markup=reply_markup
    )
    # 删除用户原始消息（如“开始”或 /start）
    asyncio.create_task(delete_message_after_delay(
        context, update.message.chat.id, update.message.message_id, delay=30
    ))
    # 10秒后删除带按钮的消息
    asyncio.create_task(delete_message_after_delay(
        context, sent_msg.chat.id, sent_msg.message_id, delay=30
    ))


# ===== 按钮点击事件统一入口 =====
    
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    handler = callback_handlers.get(data)

    if handler:
        result = await handler(query, user_id)
    else:
        result = f"未知的操作：{data}"

    # 编辑消息，展示结果
    sent_msg = await query.edit_message_text(text=result)

    # 10秒后删除这个回调响应后的消息
    asyncio.create_task(delete_message_after_delay(
        context, sent_msg.chat.id, sent_msg.message_id, delay=30
    ))
