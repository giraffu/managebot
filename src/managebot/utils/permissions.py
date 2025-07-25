from telegram import ChatPermissions

PERMISSION_GROUPS = {
    "muted": ChatPermissions(
        can_send_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
    ),
    "restricted": ChatPermissions(
        can_send_messages=True,      # 只能发文字、联系人、位置等
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_send_audios=False,
        can_send_documents=False,
        can_send_photos=False,
        can_send_videos=False,
        can_send_video_notes=False,
        can_send_voice_notes=False,
    ),
    "normal": ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_send_audios=True,
        can_send_documents=True,
        can_send_photos=True,
        can_send_videos=True,
        can_send_video_notes=True,
        can_send_voice_notes=True,
    )
}

async def update_user_permissions(chat_id: int, user_id: int, role: str, bot):
    permissions = PERMISSION_GROUPS.get(role, PERMISSION_GROUPS["muted"])
    await bot.restrict_chat_member(chat_id, user_id, permissions=permissions)
