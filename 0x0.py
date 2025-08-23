__version__ = (1, 0, 3)


import os
import subprocess
from .. import loader, utils

@loader.tds
class upl0x0Mod(loader.Module):
    """Upload files to 0x0.st from replies"""
    strings = {"name": "0x0"}

    async def oxocmd(self, message):
        """Reply to a file to upload it to 0x0.st"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("Reply to a file to upload.")
            return

        file_path = await reply.download_media()
        await message.edit("Uploading to 0x0.st...")

        try:
            curl_cmd = ["curl", "-F", f"file=@{file_path}", "https://0x0.st"]
            process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            
            if process.returncode == 0 and output:
                url = output.decode().strip()
                if url.startswith("https://0x0.st/"):
                    await message.edit(f"Uploaded: {url}")
                else:
                    await message.edit(f"Upload failed. Response: {url}")
            else:
                error_msg = error.decode() if error else "Unknown error"
                await message.edit(f"Upload failed. Error: {error_msg}")
        except Exception as e:
            await message.edit(f"Error: {str(e)}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)