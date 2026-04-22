#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# This file is part of < https://github.com/TheAloneTeam/AloneMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/AloneMusic/blob/master/LICENSE >
#
# All rights reserved.

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from AloneMusic import app
from AloneMusic.utils.database import is_thumb_on
from AloneMusic.utils.decorators import language
from config import BANNED_USERS


@app.on_message(filters.command(["thumb", "thumbnail"]) & filters.group & ~BANNED_USERS)
@language
async def thumb_command(client, message: Message, _):
    thumb_state = await is_thumb_on(message.chat.id)
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴇɴᴀʙʟᴇ" if not thumb_state else "ᴅɪsᴀʙʟᴇ",
                callback_data=f"THUMBNAILCHANGE"
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ", callback_data="close"
            ),
        ],
    ]
    return await message.reply_text(
        _["thumb_1"],
        reply_markup=InlineKeyboardMarkup(buttons),
    )
