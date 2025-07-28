from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from managebot.user_storage import load_user_status, save_user_status
from managebot.utils.message_tools import delete_message_after_delay
import asyncio
import time
from managebot.user_storage import load_user_status, save_user_status
import json
import os
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

async def handle_send_media_category(query, user_id: str):
    keyboard = [
        [InlineKeyboardButton("📷 风景", callback_data=f'media_landscape_{user_id}')],
        [InlineKeyboardButton("👤 人物", callback_data=f'media_people_{user_id}')],
        [InlineKeyboardButton("🔙 返回", callback_data=f'menu_back_{user_id}')]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("请选择媒体分类：", reply_markup=markup)

async def handle_media_selection(query, user_id: str, category: str):
    user_data = load_user_status()
    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id]["media_category"] = category
    user_data[user_id]["awaiting_media"] = True
    save_user_status(user_data)

    await query.edit_message_text(f"你选择了『{category}』分类，请发送图片或视频：")
# ===== callback_data 到处理函数的映射 =====

callback_handlers = {
    'btn1': handle_query_info,
    'btn2': handle_sign_up,
    'btn3': handle_send_media_category,
}

def build_main_menu(user_id: str):
    timestamp = int(time.time())  # 当前时间戳（秒）
    print("user_id", user_id, "timestamp", timestamp)

    keyboard = [
        [InlineKeyboardButton("查询信息", callback_data=f'btn1_{user_id}_{timestamp}')],
        [InlineKeyboardButton("报名", callback_data=f'btn2_{user_id}_{timestamp}')]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_file_menu(user_id: str):
    timestamp = int(time.time())  # 当前时间戳（秒）
    print("user_id", user_id, "timestamp", timestamp)

    keyboard = [
        [InlineKeyboardButton("查询信息", callback_data=f'btn1_{user_id}_{timestamp}')],
        [InlineKeyboardButton("报名", callback_data=f'btn2_{user_id}_{timestamp}')],
        [InlineKeyboardButton("发送图片或视频", callback_data=f'btn3_{user_id}_{timestamp}')]
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
        if action_key == "media":
            category = parts[2] if len(parts) > 2 else "未知"
            await handler(query, user_clicking, category)
        else:
            result = await handler(query, user_clicking)
            if result:
                sent_msg = await query.edit_message_text(text=result)
                asyncio.create_task(delete_message_after_delay(
                    context, sent_msg.chat.id, sent_msg.message_id, delay=180
                ))

MEDIA_LOG_FILE = "media_log.json"
PRIVATE_GROUP_ID = -1001234567890  # 替换成你的私有群组 ID

async def handle_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_data = load_user_status()
    if user_id not in user_data or not user_data.get("awaiting_media"):
        return  # 用户不在媒体上传状态

    category = user_data.get("media_category", "未分类")

    file_info = None
    media_type = None

    if update.message.photo:
        # 多张照片取最后一张（最大尺寸）
        photo = update.message.photo[-1]
        file_info = photo.file_id
        media_type = "photo"
        await context.bot.send_photo(chat_id=PRIVATE_GROUP_ID, photo=file_info)
    elif update.message.video:
        video = update.message.video
        file_info = video.file_id
        media_type = "video"
        await context.bot.send_video(chat_id=PRIVATE_GROUP_ID, video=file_info)
    else:
        await update.message.reply_text("请发送图片或视频。")
        return

    # 写入记录 JSON
    media_record = {
        "user_id": user_id,
        "category": category,
        "media_type": media_type,
        "file_id": file_info
    }

    # 追加保存
    if os.path.exists(MEDIA_LOG_FILE):
        with open(MEDIA_LOG_FILE, "r", encoding="utf-8") as f:
            media_data = json.load(f)
    else:
        media_data = []

    media_data.append(media_record)
    with open(MEDIA_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(media_data, f, ensure_ascii=False, indent=2)

    # 提示用户完成
    await update.message.reply_text("✅ 已成功上传并保存。")

    # 重置用户状态
    user_data[user_id]["awaiting_media"] = False
    user_data[user_id]["media_category"] = ""
    save_user_status(user_data)