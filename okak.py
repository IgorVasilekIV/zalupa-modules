# meta banner: https://raw.githubusercontent.com/Fixyres/Modules/refs/heads/main/IMG_20250112_185329_901.jpg
# meta developer: @Foxy437 & okak(@IgorVasilekIV)

from .. import loader, utils

@loader.tds
class okakMod(loader.Module):
    """окак"""

    strings = {
        "name": "окак"
    }

    async def okakcmd(self, m):
        """okak"""
        await utils.asyncio.sleep(1)
        self.db.set("okak", "on", not self.db.get("okak", "on", False))
        if self.db.get("okak", "on", False):
            await m.edit("<emoji document_id=5211078941153974712>😨</emoji>okak ACTIVATED")

    async def watcher(self, m):
        if self.db.get("okak", "on", False) and m.out:
            await m.edit("окак")
