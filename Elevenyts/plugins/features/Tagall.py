import asyncio

from pyrogram import filters, types
from pyrogram.enums import ChatMemberStatus

from Elevenyts import app


# ================= STORAGE ================= #

# True = everyone can use /tagall
# False = only admins can use /tagall
TAGALL_ENABLED = {}

# Running status for stop command
RUNNING_TAGALL = {}


# ================= ADMIN CHECK ================= #

async def is_admin(chat_id: int, user_id: int):
    try:
        member = await app.get_chat_member(chat_id, user_id)

        return member.status in [
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR
        ]

    except:
        return False


# ================= ENABLE TAGALL ================= #

@app.on_message(filters.group & filters.command("enabletagall"))
async def enable_tagall(_, message: types.Message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(
            "❌ Only admins can use this command."
        )

    TAGALL_ENABLED[message.chat.id] = True

    await message.reply_text(
        "✅ Normal users can now use /tagall"
    )


# ================= DISABLE TAGALL ================= #

@app.on_message(filters.group & filters.command("disabletagall"))
async def disable_tagall(_, message: types.Message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(
            "❌ Only admins can use this command."
        )

    TAGALL_ENABLED[message.chat.id] = False

    await message.reply_text(
        "✅ Only admins can now use /tagall"
    )


# ================= STOP TAGALL ================= #

@app.on_message(filters.group & filters.command("stoptagall"))
async def stop_tagall(_, message: types.Message):

    if not message.from_user:
        return

    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text(
            "❌ Only admins can stop tagall."
        )

    if not RUNNING_TAGALL.get(message.chat.id):
        return await message.reply_text(
            "❌ No active tagall is running."
        )

    RUNNING_TAGALL[message.chat.id] = False

    await message.reply_text(
        "🛑 Tagall stopped successfully."
    )


# ================= TAGALL ================= #

@app.on_message(filters.group & filters.command("tagall"))
async def tag_all_members(_, message: types.Message):

    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check admin
    admin = await is_admin(chat_id, user_id)

    # Check settings
    enabled = TAGALL_ENABLED.get(chat_id, False)

    # If disabled and user not admin
    if not admin and not enabled:
        return await message.reply_text(
            "❌ Only admins can use /tagall"
        )

    # Prevent multiple running tagalls
    if RUNNING_TAGALL.get(chat_id):
        return await message.reply_text(
            "❌ A tagall is already running."
        )

    RUNNING_TAGALL[chat_id] = True

    # Extra message after command
    extra_msg = " ".join(message.command[1:])

    if extra_msg:
        header = (
            f"<blockquote><b>{extra_msg}</b></blockquote>\n\n"
        )
    else:
        header = (
            "<blockquote><b>📢 Tagging all members</b></blockquote>\n\n"
        )

    mentions = []
    total = 0

    try:

        async for member in app.get_chat_members(chat_id):

            # Stop instantly
            if not RUNNING_TAGALL.get(chat_id):
                return

            user = member.user

            # Skip bots
            if user.is_bot:
                continue

            # Skip deleted accounts
            if user.is_deleted:
                continue

            # Add mention
            mentions.append(
                f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
            )

            total += 1

            # Send every 5 users
            if len(mentions) == 5:

                await message.reply_text(
                    header + " | ".join(mentions),
                    disable_web_page_preview=True
                )

                mentions = []

                # Anti flood delay
                await asyncio.sleep(2)

        # Send remaining users
        if mentions and RUNNING_TAGALL.get(chat_id):

            await message.reply_text(
                header + " | ".join(mentions),
                disable_web_page_preview=True
            )

        RUNNING_TAGALL[chat_id] = False

        await message.reply_text(
            f"✅ Tagall completed.\n👥 Total users tagged: {total}"
        )

    except Exception as e:

        RUNNING_TAGALL[chat_id] = False

        await message.reply_text(
            f"❌ Error:\n<code>{e}</code>"
        )
