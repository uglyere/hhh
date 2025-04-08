from telethon.tl import types, functions
from telethon.tl.tlobject import TLObject
from telethon.tl.types import (
    InputMediaUploadedPhoto,
    InputMediaUploadedDocument,
    InputSingleMedia,
    InputMediaPhotoExternal,
    InputPeerUser,
    InputPeerChat,
    InputPeerChannel,
    MessageEntityBold,
    MessageEntityItalic,
    InputDocument,
)
import os
import random

class MySendMultiMediaRequest(TLObject):
    CONSTRUCTOR_ID = 0x37b74355

    def __init__(self, *, peer, multi_media, reply_to=None, silent=False, background=False, clear_draft=False, schedule_date=None):
        self.peer = peer
        self.multi_media = multi_media
        self.reply_to = reply_to
        self.silent = silent
        self.background = background
        self.clear_draft = clear_draft
        self.schedule_date = schedule_date

    def to_dict(self):
        return {
            "_": "MySendMultiMediaRequest",
            "peer": self.peer,
            "multi_media": self.multi_media,
            "reply_to": self.reply_to,
            "silent": self.silent,
            "background": self.background,
            "clear_draft": self.clear_draft,
            "schedule_date": self.schedule_date,
        }

    def __bytes__(self):
        flags = 0
        if self.silent:
            flags |= 1 << 5
        if self.background:
            flags |= 1 << 6
        if self.clear_draft:
            flags |= 1 << 7
        if self.reply_to is not None:
            flags |= 1 << 0
        if self.schedule_date is not None:
            flags |= 1 << 10

        return b''.join((
            int.to_bytes(self.CONSTRUCTOR_ID, 4, 'little'),
            int.to_bytes(flags, 4, 'little'),
            self.serialize_bytes(self.peer),
            self.serialize_bytes(self.reply_to) if self.reply_to else b'',
            self.serialize_bytes(self.multi_media),
            self.serialize_bytes(self.schedule_date) if self.schedule_date else b'',
        ))

# Использование
async def custom_send_multi_media(client, chat_id, photo_paths, caption=None, reply_to_msg_id=None):
    media_list = []
    for path in photo_paths:
        if not os.path.exists(path):
            continue
        file = await client.upload_file(path)
        input_media = InputMediaUploadedPhoto(file=file)
        media = InputSingleMedia(
            media=input_media,
            message=caption or "",
            entities=[],
            random_id=random.randint(0, 0x7FFFFFFF)
        )
        media_list.append(media)

    if not media_list:
        return

    peer = await client.get_input_entity(chat_id)
    reply_to = types.InputReplyToMsgId(msg_id=reply_to_msg_id) if reply_to_msg_id else None

    req = MySendMultiMediaRequest(
        peer=peer,
        multi_media=media_list,
        reply_to=reply_to,
    )

    result = await client._call_function('messages.sendMultiMedia', req)
    return result
