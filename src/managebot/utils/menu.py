from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay
import asyncio
import time
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

def build_main_menu(user_id: str):
    timestamp = int(time.time())  # 当前时间戳（秒）
    print("user_id", user_id, "timestamp", timestamp)

    keyboard = [
        [InlineKeyboardButton("查询信息", callback_data=f'btn1_{user_id}_{timestamp}')],
        [InlineKeyboardButton("报名", callback_data=f'btn2_{user_id}_{timestamp}')]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== 按钮点击事件统一入口 =====
    
async def button_click_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_clicking = str(query.from_user.id)
    data = query.data
    print("user_clicking ", user_clicking)

    parts = data.split("_", 2)
    if len(parts) < 2:
        await query.answer("⚠️ 数据格式错误", show_alert=True)
        return

    action_key, target_user_id = parts[0], parts[1]

    # 拒绝其他人点击
    if user_clicking != target_user_id:
        print("⚠️ 你不能操作别人的菜单",target_user_id,user_clicking)
        return

    handler = callback_handlers.get(action_key)

    if handler:
        result = await handler(query, user_clicking)
    else:
        result = f"未知的操作：{action_key}"

    # 编辑消息
    sent_msg = await query.edit_message_text(text=result)

    # 延时删除
    asyncio.create_task(delete_message_after_delay(
        context, sent_msg.chat.id, sent_msg.message_id, delay=180
    ))

