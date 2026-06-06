from pyrogram import filters
from Elevenyts import app
from pyrogram.types import Message
import asyncio

running_tagall = {}


# ✅ owner + admin check
async def is_admin_or_owner(chat_id, user_id):
    member = await app.get_chat_member(chat_id, user_id)
    return member.status in ("administrator", "creator")


@app.on_message(filters.command("tagall") & filters.group)
async def tag_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 🔒 ADMIN / OWNER ONLY
    if not await is_admin_or_owner(chat_id, user_id):
        return await message.reply_text("❌ Only group admins or owner can use this command.")

    if running_tagall.get(chat_id):
        return await message.reply_text("⚠️ TagAll already running. Use /stoptagall first.")

    text = " ".join(message.command[1:])
    if not text:
        text = "Attention everyone!"

    stop_flag = {"stop": False}
    running_tagall[chat_id] = stop_flag

    sent = await message.reply_text("🔄 TagAll started...")

    users = []
    async for member in app.get_chat_members(chat_id):
        if member.user and not member.user.is_bot:
            users.append(member.user.mention)

    batch = 20

    try:
        for i in range(0, len(users), batch):
            if stop_flag["stop"]:
                await sent.edit("⛔ TagAll stopped.")
                return

            chunk = users[i:i + batch]

            await message.reply_text(
                f"{text}\n\n" + " ".join(chunk),
                disable_web_page_preview=True
            )

            await asyncio.sleep(2)

        await sent.edit("✅ TagAll completed!")

    finally:
        running_tagall.pop(chat_id, None)


@app.on_message(filters.command("stoptagall") & filters.group)
async def stop_tag_all(_, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # 🔒 ADMIN / OWNER ONLY
    if not await is_admin_or_owner(chat_id, user_id):
        return await message.reply_text("❌ Only group admins or owner can use this command.")

    if chat_id in running_tagall:
        running_tagall[chat_id]["stop"] = True
        return await message.reply_text("🛑 Stopping TagAll...")

    await message.reply_text("❌ No TagAll is running.")
