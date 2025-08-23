# meta version: 1.0.1


from telethon import events
import requests
import os
from .. import loader, utils

@loader.tds
class Upload0x0Mod(loader.Module):
    """Upload files to 0x0.st from replies"""
    strings = {"name": "0x0Uploader"}

    async def oxocmd(self, message):
        """Reply to a file to upload it to 0x0.st"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("Reply to a file to upload.")
            return

        file_path = await reply.download_media()
        await message.edit("Uploading to 0x0.st...")

        try:
            with open(file_path, "rb") as f:
                resp = requests.post("https://0x0.st", files={"file": f})
            if resp.status_code == 200 and resp.text.startswith("https://0x0.st/"):
                await message.edit(f"Uploaded: {resp.text.strip()}")
            else:
                await message.edit("Upload failed.")
        except Exception as e:
            await message.edit(f"Error: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)