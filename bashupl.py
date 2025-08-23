__version__ = (1, 0, 7)


import os
import subprocess
from .. import loader, utils

@loader.tds
class BashUploadMod(loader.Module):
    """Upload files to bashupload.com from replies"""
    strings = {"name": "BashUpload"}

    async def bashcmd(self, message):
        """Reply to a file to upload it to bashupload.com"""
        reply = await message.get_reply_message()
        if not reply or not reply.file:
            await message.edit("Reply to a file to upload.")
            return

        file_path = await reply.download_media()
        file_name = os.path.basename(file_path)
        await message.edit("Uploading to bashupload.com...")

        try:
            curl_cmd = ["curl", "--upload-file", file_path, f"https://bashupload.com/{file_name}"]
            process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate()
            
            if process.returncode == 0 and output:
                output_text = output.decode()
                # Find the download URL in the response
                import re
                if match := re.search(r"wget (https://bashupload\.com/[^\s]+)", output_text):
                    url = match.group(1)
                    await message.edit(f"Uploaded: {url}")
                else:
                    await message.edit(f"Failed to parse upload URL from response: {output_text}")
            else:
                error_msg = error.decode() if error else "Unknown error"
                await message.edit(f"Upload failed. Error: {error_msg}")
        except Exception as e:
            await message.edit(f"Error: {str(e)}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)