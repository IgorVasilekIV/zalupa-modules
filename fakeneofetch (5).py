"""
    Фейк/кастом фетч для рофлов
    (ох уж этот рн7)
"""
# meta developer: @HikkaZPM

from .. import loader, utils
from telethon import events
import asyncio
import logging
import platform
import os
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@loader.tds
class FakeNeofetchMod(loader.Module):
    """Имитация neofetch --stdout"""
    
    strings = {
        "name": "Fakeneofetch",
        "loading": "<b>Загрузка системной информации...</b>",
        "custom_host_reset": "<b>Кастомный хост сброшен до стандартного</b>",
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "CUSTOM_OS", "Arch Linux", "Кастомный хост для отображения",
            "CUSTOM_HOSTNAME", "archbtw", "Кастомный хостнейм для отображения",
            "CUSTOM_USER", "root", "Кастомное имя пользователя",
            "CUSTOM_KERNEL", "Linux 6.2.0-arch1", "Кастомное ядро",
            "CUSTOM_UPTIME", "69 days, 4 hours, 20 minutes", "Кастомное время работы",
            "CUSTOM_PACKAGES", "1337", "Кастомное количество пакетов",
            #"CUSTOM_SHELL", "fish", "Оболочка",
            #"CUSTOM_RESOLUTION", "3840x2160", "Разрешение экрана",
            #"CUSTOM_DE", "hyprland", "Окружение рабочего стола",
            #"CUSTOM_THEME", "Dracula", "Кастомная тема",
            "CUSTOM_CPU", "AMD Ryzen 9 7950X", "Процессор",
            #"CUSTOM_GPU", "NVIDIA RTX 4090", "Видеокарта",
            "CUSTOM_MEMORY", "64GB / 128GB", "Память (использовано / всего)",
            "ENABLE_DELAY", True, "Включить задержку перед выводом",
            "DELAY", "1.5", "Задержка перед выводом (секунды окда)",
        )
    
    async def client_ready(self, client, db):
        """Вызывается при готовности клиента"""
        self._client = client
        self._db = db
        self._me = await client.get_me()
    
    @loader.command(ru_doc="Показать фейковый neofetch с кастомным хостом")
    async def fneo(self, message):
        """Показывает фейковый вывод neofetch с кастомным хостом"""
        msg = await utils.answer(message, self.strings["loading"])
        
        if self.config["ENABLE_DELAY"]:
            await asyncio.sleep(self.config['DELAY'])
        
        current_time = datetime.now().strftime("%H:%M:%S")
        
        system_info = f"""
{self.config['CUSTOM_USER']}@{self.config['CUSTOM_HOSTNAME']}
--------------------------
OS: {self.config['CUSTOM_OS']}
Kernel: {self.config['CUSTOM_KERNEL']}
Uptime: {self.config['CUSTOM_UPTIME']}
Packages: {self.config['CUSTOM_PACKAGES']}
"""
#Shell: {self.config['CUSTOM_SHELL']}
#Resolution: {self.config['CUSTOM_RESOLUTION']}
#DE: {self.config['CUSTOM_DE']}
#Theme: {self.config['CUSTOM_THEME']}
"""
CPU: {self.config['CUSTOM_CPU']}
"""
# GPU: {self.config['CUSTOM_GPU']}
"""
Memory: {self.config['CUSTOM_MEMORY']}
"""
        
        output = f"{system_info}"

        execution_time = f"\n<code>Выполнено за {self.config['DELAY']} секунд.</code>"
        output += execution_time

        await utils.answer(msg, output + "</pre>")
        
    @loader.command(ru_doc="Сбросить все настройки до стандартных")
    async def resetneofetch(self, message):
        """Сбрасывает все настройки neofetch до стандартных"""

        self.config["CUSTOM_HOST"] = "Arch Linux"
        self.config["CUSTOM_HOSTNAME"] = "archbtw"
        self.config["CUSTOM_USER"] = "root"
        self.config["CUSTOM_KERNEL"] = "Linux 6.2.0-arch1"
        self.config["CUSTOM_UPTIME"] = "69 days, 4 hours, 20 minutes"
        self.config["CUSTOM_PACKAGES"] = "1337"
        self.config["CUSTOM_SHELL"] = "fish"
        self.config["CUSTOM_RESOLUTION"] = "3840x2160"
        self.config["CUSTOM_DE"] = "hyprland"
        self.config["CUSTOM_THEME"] = "Dracula"
        self.config["CUSTOM_CPU"] = "AMD Ryzen 9 7950X"
        self.config["CUSTOM_GPU"] = "NVIDIA RTX 4090"
        self.config["CUSTOM_MEMORY"] = "64GB / 128GB"
        self.config["DELAY"] = "1.5"
                
        await utils.answer(message, self.strings["custom_host_reset"])
