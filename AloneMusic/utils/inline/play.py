#
# Copyright (C) 2021-2022 by TheAloneteam@Github, < https://github.com/TheAloneTeam >.
#
# This file is part of < https://github.com/TheAloneTeam/AloneMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TheAloneTeam/AloneMusic/blob/master/LICENSE >
#
# All rights reserved.

import math
from typing import Union
from pyrogram.types import InlineKeyboardButton
from AloneMusic import app
from AloneMusic.utils.formatters import time_to_seconds

def track_markup(_, videoid, user_id, channel, fplay, thumb: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text="🎵 ᴀᴜᴅɪᴏ", callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text="🎥 ᴠɪᴅᴇᴏ", callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"MusicThumb {videoid}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur, autoplay: Union[bool, str] = None, thumb: Union[bool, str] = None, chat_filter: Union[bool, str] = None, more: bool = False):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    remaining_sec = max(0, duration_sec - played_sec)
    
    rem_min, rem_sec = divmod(remaining_sec, 60)
    remaining = f"{rem_min:02d}:{rem_sec:02d}"
    
    percentage = (played_sec / duration_sec) * 100 if duration_sec else 0
    umm = math.floor(percentage)

    # Sleek Progress Bar Design
    bars = ["▰", "▱"]
    total_bars = 10
    completed_bars = int(umm / 10)
    bar = f"|{bars[0]*completed_bars}◈{bars[1]*(total_bars-completed_bars)}|"

    if not more:
        buttons = [
            [InlineKeyboardButton(text=f"{played} {bar} {remaining}", url=f"https://t.me/{app.username}?startgroup=true")],
            [
                InlineKeyboardButton(text="▶️", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="⏸️", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="⏭️", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="🔄", callback_data=f"ADMIN Replay|{chat_id}"),
                InlineKeyboardButton(text="⏹️", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="📂 ᴍᴏʀᴇ", callback_data=f"ADMIN More|{chat_id}"),
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    else:
        f_text = chat_filter.replace('Normal', 'ɴᴏʀᴍᴀʟ').replace('Bass', 'ʙᴀss').replace('Echo', 'ᴇᴄʜᴏ').replace('Slowed', 'sʟᴏᴡᴇᴅ').replace('Nightcore', 'ɴɪɢʜᴛᴄᴏʀᴇ') if chat_filter else "ɴᴏʀᴍᴀʟ"
        buttons = [
            [InlineKeyboardButton(text=f"{played} {bar} {remaining}", url=f"https://t.me/{app.username}?startgroup=true")],
            [
                InlineKeyboardButton(text="▶️", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="⏸️", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="⏭️", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="🔄", callback_data=f"ADMIN Replay|{chat_id}"),
                InlineKeyboardButton(text="⏹️", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="🔄 ᴀᴜᴛᴏᴘʟᴀʏ : 🟢" if autoplay else "🔄 ᴀᴜᴛᴏᴘʟᴀʏ : 🔴", callback_data=f"ADMIN Autoplay|{chat_id}"),
                InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"ADMIN Thumb|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text=f"🪄 {f_text}", callback_data=f"ADMIN Filter|{chat_id}"),
                InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"ADMIN Back|{chat_id}"),
            ],
            [InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")],
        ]
    return buttons

def stream_markup(_, chat_id, autoplay: Union[bool, str] = None, thumb: Union[bool, str] = None, chat_filter: Union[bool, str] = None, more: bool = False):
    if not more:
        buttons = [
            [
                InlineKeyboardButton(text="▶️", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="⏸️", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="🔄", callback_data=f"ADMIN Replay|{chat_id}"),
                InlineKeyboardButton(text="⏭️", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="⏹️", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="📂 ᴍᴏʀᴇ", callback_data=f"ADMIN More|{chat_id}"),
                InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close"),
            ],
        ]
    else:
        f_text = chat_filter.replace('Normal', 'ɴᴏʀᴍᴀʟ').replace('Bass', 'ʙᴀss').replace('Echo', 'ᴇᴄʜᴏ').replace('Slowed', 'sʟᴏᴡᴇᴅ').replace('Nightcore', 'ɴɪɢʜᴛᴄᴏʀᴇ') if chat_filter else "ɴᴏʀᴍᴀʟ"
        buttons = [
            [
                InlineKeyboardButton(text="▶️", callback_data=f"ADMIN Resume|{chat_id}"),
                InlineKeyboardButton(text="⏸️", callback_data=f"ADMIN Pause|{chat_id}"),
                InlineKeyboardButton(text="🔄", callback_data=f"ADMIN Replay|{chat_id}"),
                InlineKeyboardButton(text="⏭️", callback_data=f"ADMIN Skip|{chat_id}"),
                InlineKeyboardButton(text="⏹️", callback_data=f"ADMIN Stop|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text="🔄 ᴀᴜᴛᴏᴘʟᴀʏ : 🟢" if autoplay else "🔄 ᴀᴜᴛᴏᴘʟᴀʏ : 🔴", callback_data=f"ADMIN Autoplay|{chat_id}"),
                InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"ADMIN Thumb|{chat_id}"),
            ],
            [
                InlineKeyboardButton(text=f"🪄 {f_text}", callback_data=f"ADMIN Filter|{chat_id}"),
                InlineKeyboardButton(text="🔙 ʙᴀᴄᴋ", callback_data=f"ADMIN Back|{chat_id}"),
            ],
            [InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data="close")],
        ]
    return buttons

def playlist_markup(_, videoid, user_id, ptype, channel, fplay, thumb: Union[bool, str] = None):
    buttons = [
        [
            InlineKeyboardButton(text="🎵 ᴀᴜᴅɪᴏ", callback_data=f"AlonePlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text="🎥 ᴠɪᴅᴇᴏ", callback_data=f"AlonePlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"PlaylistThumb {videoid}|{user_id}|{ptype}|{channel}|{fplay}"),
            InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]
    return buttons

def livestream_markup(_, videoid, user_id, mode, channel, fplay, thumb: Union[bool, str] = None):
    buttons = [
        [InlineKeyboardButton(text="🎬 sᴛᴀʀᴛ ʟɪᴠᴇ", callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}")],
        [
            InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"LiveThumb {videoid}|{user_id}|{mode}|{channel}|{fplay}"),
            InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data=f"forceclose {videoid}|{user_id}"),
        ],
    ]
    return buttons

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay, thumb: Union[bool, str] = None):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(text="🎵 ᴀᴜᴅɪᴏ", callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}"),
            InlineKeyboardButton(text="🎥 ᴠɪᴅᴇᴏ", callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(text="◁", callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text="🖼️ ᴛʜᴜᴍʙ : 🟢" if thumb else "🖼️ ᴛʜᴜᴍʙ : 🔴", callback_data=f"SliderThumb {videoid}|{user_id}|{query}|{query_type}|{channel}|{fplay}"),
            InlineKeyboardButton(text="▷", callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}"),
        ],
        [InlineKeyboardButton(text="🗑️ ᴄʟᴏsᴇ", callback_data=f"forceclose {query}|{user_id}")],
    ]
    return buttons
