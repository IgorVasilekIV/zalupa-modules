"""
    Фейк фетч для рофлов
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

# Настраиваем логгер
logger = logging.getLogger(__name__)

# Определяем класс модуля
@loader.tds
class FakeNeofetchMod(loader.Module):
    """Имитация neofetch с лого"""
    
    strings = {
        "name": "FakeNeofetch",
        "loading": "<b>Загрузка системной информации...</b>",
        "custom_host_reset": "<b>Кастомный хост сброшен до стандартного</b>",
        "arch_logo": """                   -`                    
                  .o+`                   
                 `ooo/                   
                `+oooo:                  
               `+oooooo:                
               -+oooooo+:                
             `/:-:++oooo+:               
            `/++++/+++++++:              
           `/++++++++++++++:             
          `/+++ooooooooooooo/`           
         ./ooosssso++osssssso+`          
        .oossssso-````/ossssss+`         
       -osssssso.      :ssssssso.        
      :osssssss/        osssso+++.       
     /ossssssss/        +ssssooo/-       
   `/ossssso+/:-        -:/+osssso+-     
  `+sso+:-`                 `.-/+oso:    
 `++:.                           `-/+/   
 .`                                 `/   """
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            "CUSTOM_OS", "Arch Linux", "Кастомный хост для отображения",
            "CUSTOM_HOSTNAME", "archbtw", "Кастомный хостнейм для отображения",
            "CUSTOM_USER", "root", "Кастомное имя пользователя",
            "CUSTOM_KERNEL", "Linux 6.2.0-arch1", "Кастомное ядро",
            "CUSTOM_UPTIME", "69 days, 4 hours, 20 minutes", "Кастомное время работы",
            "CUSTOM_PACKAGES", "1337", "Кастомное количество пакетов",
            "CUSTOM_CPU", "AMD Ryzen 9 7950X", "Кастомный процессор",
            "CUSTOM_MEMORY", "64GB / 128GB", "Кастомная память (использовано / всего)",
            "ENABLE_DELAY", True, "Включить задержку перед выводом",
            "DELAY", "1.5", "Задержка перед выводом (секунды окда)",
            "SHOW_COLORS", False, "Показывать цветовую схему",
            "BREAK", "--------------------------", "Разбивка на строки"
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
            await asyncio.sleep(float(self.config['DELAY']))
        
        # Используем логотип из strings
        logo = self.strings["arch_logo"]
        
        # Формируем системную информацию
        system_info = f"""
{self.config['CUSTOM_USER']}@{self.config['CUSTOM_HOSTNAME']}
{self.config['BREAK']}
OS: {self.config['CUSTOM_OS']}
Kernel: {self.config['CUSTOM_KERNEL']}
Uptime: {self.config['CUSTOM_UPTIME']}
Packages: {self.config['CUSTOM_PACKAGES']}
CPU: {self.config['CUSTOM_CPU']}
Memory: {self.config['CUSTOM_MEMORY']}"""
        
        # Добавляем цветовую схему, если включено
        if self.config["SHOW_COLORS"]:
            colors = """
Colors: 
🟥 🟧 🟨 🟩 🟦 🟪 ⬛ ⬜"""
            system_info += colors
        
        # Формируем полный вывод
        output = f"<pre>{logo}{system_info}\n\nВыполнено за {self.config['DELAY']} секунд.</pre>"

        await utils.answer(msg, output)
        
    @loader.command(ru_doc="Сбросить все настройки до стандартных")
    async def resetneofetch(self, message):
        """Сбрасывает все настройки neofetch до стандартных"""
        self.config["CUSTOM_OS"] = "Arch Linux"
        self.config["CUSTOM_HOSTNAME"] = "archbtw"
        self.config["CUSTOM_USER"] = "root"
        self.config["CUSTOM_KERNEL"] = "Linux 6.2.0-arch1"
        self.config["CUSTOM_UPTIME"] = "69 days, 4 hours, 20 minutes"
        self.config["CUSTOM_PACKAGES"] = "1337"
        self.config["CUSTOM_CPU"] = "AMD Ryzen 9 7950X"
        self.config["CUSTOM_MEMORY"] = "64GB / 128GB"
        self.config["BREAK"] = "--------------------------"
        self.config["DELAY"] = "1.5"
        
        await utils.answer(message, self.strings["custom_host_reset"])
