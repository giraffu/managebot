# managebot/utils/message_tools.py
import asyncio

async def delete_message_after_delay(context, chat_id: int, message_id: int, delay: int = 10):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"删除消息失败 (chat_id={chat_id}, message_id={message_id}): {e}")