from telethon.tl.types import PeerChannel
from telethon.tl.functions.messages import GetHistoryRequest
from telethon import TelegramClient
import asyncio
import json
import config
from telethon.tl.types import PeerUser
from collections import defaultdict
from typing import Set

async def export_user_data(group_id: int, output_path: str = "data/user_data.json", progress_callback=None, max_retries=3) -> str:
    proxy = ('socks5', '127.0.0.1', 10808)

    async def with_retries(func, *args, **kwargs):
        last_exc = None
        for attempt in range(1, max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exc = e
                print(f"尝试第{attempt}次失败，异常: {e}")
                await asyncio.sleep(2)
        raise RuntimeError(f"操作失败，重试{max_retries}次后依然错误: {last_exc}")

    async with TelegramClient("session_export", config.TELETHON_API_ID, config.TELETHON_API_HASH, proxy=proxy) as client:
        group_id = int(group_id)
        dialogs = await client.get_dialogs()
        entity = None
        for d in dialogs:
            if d.id == group_id:
                entity = d.entity
                break
        if entity is None:
            entity = await client.get_input_entity(PeerChannel(channel_id=group_id))

        # 获取消息总数
        history_info = await with_retries(client, GetHistoryRequest(
            peer=entity,
            offset_id=0,
            offset_date=None,
            add_offset=0,
            limit=1,
            max_id=0,
            min_id=0,
            hash=0
        ))
        total_messages = history_info.count

        if progress_callback:
            await progress_callback(0, total_messages)

        offset_id = 0  # 从最新消息开始拉取
        limit = 100
        processed_count = 0
        progress_step = 500

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("[\n")  # 写入json数组开头
            first_item = True

            while True:
                history = await with_retries(client, GetHistoryRequest(
                    peer=entity,
                    offset_id=offset_id,
                    offset_date=None,
                    add_offset=0,
                    limit=limit,
                    max_id=0,
                    min_id=0,
                    hash=0
                ))
                messages = history.messages
                if not messages:
                    print("没有更多消息，结束。")
                    break

                output_list = []
                user_cache = {}

                for msg in messages:
                    if msg.from_id:
                        
                        if isinstance(msg.from_id, PeerUser):
                            raw_user_id = msg.from_id.user_id
                            user_id = str(raw_user_id)

                            # 查找用户名（带缓存）
                            if user_id in user_cache:
                                username = user_cache[user_id]
                            else:
                                try:
                                    user = await client.get_entity(raw_user_id)
                                    username = user.username if getattr(user, "username", None) else "无用户名"
                                except Exception as e:
                                    print(f"获取用户 {user_id} 信息失败：{e}")
                                    username = "未知"
                                user_cache[user_id] = username
                        else:
                            user_id = "channel_or_bot"
                            username = "匿名/频道"

                        user_id = str(raw_user_id)

                        # 查找用户名（带缓存）
                        if user_id in user_cache:
                            username = user_cache[user_id]
                        else:
                            try:
                                user = await client.get_entity(raw_user_id)
                                username = user.username if hasattr(user, "username") and user.username else "无用户名"
                            except Exception as e:
                                print(f"获取用户 {user_id} 信息失败：{e}")
                                username = "未知"
                            user_cache[user_id] = username
                    else:
                        user_id = "unknown"
                        username = "未知"

                    if hasattr(msg, 'message') and msg.message:
                        content = msg.message
                    else:
                        content = "非文本"

                    output_list.append({
                        "user_id": user_id,
                        "username": username,
                        "content": content
                    })

                for item in output_list:
                    if not first_item:
                        f.write(",\n")
                    else:
                        first_item = False
                    f.write(json.dumps(item, ensure_ascii=False))

                processed_count += len(messages)
                if progress_callback and processed_count % progress_step < limit:
                    await progress_callback(processed_count, total_messages)

                # 取最旧消息ID，准备下一次请求
                last_message_id = messages[-1].id
                print(f"已处理消息数: {processed_count}, 当前offset_id: {offset_id}, 最旧消息ID: {last_message_id}")

                # 防止死循环：
                if last_message_id == offset_id or last_message_id <= 1:
                    print("offset_id 没有变化或者过小，结束循环。")
                    break

                offset_id = last_message_id - 1

            f.write("\n]\n")  # 写入json数组结尾

        generate_user_summary(
            input_path="data/user_data.json",
            output_path="data/user_status.json"
        )
        return output_path

def generate_user_summary(
    input_path: str = "data/user_data.json",
    output_path: str = "data/user_summary.json",
    signed_up_users: Set[str] = None
):
    """
    根据消息数据生成用户统计信息。
    
    :param input_path: 输入的消息 JSON 文件路径
    :param output_path: 输出的统计结果 JSON 文件路径
    :param signed_up_users: 已注册用户 ID 的集合（可选）
    """
    signed_up_users = signed_up_users or set()

    # 读取原始消息 JSON
    with open(input_path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    # 初始化用户统计字典
    user_stats = defaultdict(lambda: {
        "warn_count": 0,
        "role": "normal",
        "message_count": 0
    })

    # 遍历消息，统计用户消息数
    for msg in messages:
        user_id = msg.get("user_id")
        if user_id == "unknown":
            continue  # 跳过未知用户
        user_stats[user_id]["message_count"] += 1

    # 标记已注册用户
    for user_id in signed_up_users:
        if user_id in user_stats:
            user_stats[user_id]["signed_up"] = True

    # 保存为 JSON 文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False, indent=2)

    print(f"✅ 用户统计已生成 -> {output_path}")
