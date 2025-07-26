from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from managebot.handlers.member_listeners import welcome_and_add_user, member_left, verify_callback,auto_delete_system_message
from managebot.handlers.kick import kick
from managebot.handlers.mute import mute, unmute
from managebot.handlers.word_filter import word_filter
from managebot.handlers.link_guard import link_guard
import config
from telegram import Update
from managebot.handlers.start_menu import start_menu_handler
from managebot.handlers.exportdata import export_data_handler
from managebot.utils.menu import button_click_handler
app = ApplicationBuilder().token(config.BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_and_add_user))
app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify_"))
app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, member_left))
app.add_handler(CommandHandler("kick", kick))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("unmute", unmute))

app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    auto_delete_system_message
))

# 用户菜单触发（优先匹配 "开始"）
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^开始$"), start_menu_handler), group=0)

# 敏感词过滤
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, word_filter), group=1)

# 链接守卫
app.add_handler(MessageHandler(filters.TEXT & filters.ALL, link_guard), group=2)
# /start 命令处理器
app.add_handler(CommandHandler("start", start_menu_handler))

# 按钮点击时触发
app.add_handler(CallbackQueryHandler(button_click_handler, pattern=r"^btn"))

#app.add_handler(CommandHandler("export", export_data_handler))
app.run_polling()