""" # хуйню навайбкодил, надеюсь вам понравится)
😘 fork info: added root/sudo checks, proper os detection, error handling, dependencies check, makefile improvements
"""

"""
██████████████████████████████████████████████████████████████████████████████████
█░░░░░░░░██░░░░░░░░█░░░░░░██░░░░░░█░░░░░░░░░░░░███░░░░░░██░░░░░░█░░░░░░██░░░░░░░░█
█░░▄▀▄▀░░██░░▄▀▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀░░░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀▄▀░░█
█░░░░▄▀░░██░░▄▀░░░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░▄▀▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░░░█
███░░▄▀▄▀░░▄▀▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░███
███░░░░▄▀▄▀▄▀░░░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░███
█████░░▄▀▄▀▄▀░░█████░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░███
███░░░░▄▀▄▀▄▀░░░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░░░░░▄▀░░███
███░░▄▀▄▀░░▄▀▄▀░░███░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░█░░▄▀░░██░░▄▀░░███
█░░░░▄▀░░██░░▄▀░░░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░░░▄▀▄▀░░█░░▄▀░░░░░░▄▀░░█░░▄▀░░██░░▄▀░░░░█
█░░▄▀▄▀░░██░░▄▀▄▀░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀▄▀░░░░█░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀▄▀░░█
█░░░░░░░░██░░░░░░░░█░░░░░░░░░░░░░░█░░░░░░░░░░░░███░░░░░░░░░░░░░░█░░░░░░██░░░░░░░░█
██████████████████████████████████████████████████████████████████████████████████
"""
# meta developer: @xuduk
from .. import loader, utils
import subprocess
import traceback
import shutil
import platform
import os
import asyncio

@loader.tds
class UwufetchMod(loader.Module):
    """Модуль для простого запуска Uwufetch"""
    strings = {
        "name": "Uwufetch",
        "not_supported": "<emoji document_id=5210952531676504517>❌</emoji> Your operating system is not supported",
        "no_git": "<emoji document_id=5210952531676504517>❌</emoji> Git is not installed. Please install it using your system's package manager.",
        "no_make": "<emoji document_id=5210952531676504517>❌</emoji> Make is not installed. Please install it using your system's package manager."
    }
    
    strings_ru = {
        "not_supported": "<emoji document_id=5210952531676504517>❌</emoji> Ваша операционная система не поддерживается",
        "no_git": "<emoji document_id=5210952531676504517>❌</emoji> Для установки необходим git. Установите его через пакетный менеджер вашей системы",
        "no_make": "<emoji document_id=5210952531676504517>❌</emoji> Для установки необходим make. Установите его через пакетный менеджер вашей системы"
    }

    @loader.command()
    async def uwufetchcmd(self, message):
        """- запустить uwufetch"""
        message = await utils.answer(message, "<emoji document_id=5328273493261821119>💖</emoji>")
        try:
            result = subprocess.run(["uwufetch"], capture_output=True, text=True)
            
            clean_result = subprocess.run(
                ["sed", "-E", r's/\x1B\[[0-9;]*[mK]//g; s/\x1B\[[0-9;]*[A-Z]//g'],
                input=result.stdout, capture_output=True, text=True
            )

            output = clean_result.stdout
            await utils.answer(message, f"<pre>­{output}</pre>")

        except FileNotFoundError:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji> Установи uwufetch через <code>{self.get_prefix()}installuwufetch</code>")

    async def _check_dependencies(self):
        """Проверка наличия необходимых зависимостей"""
        if not shutil.which("git"):
            return False, "git"
        if not shutil.which("make"):
            return False, "make"
        return True, None

    def _is_root(self):
        """Проверка, запущен ли процесс от рута"""
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False

    def _has_sudo(self):
        """Проверка наличия sudo"""
        return shutil.which("sudo") is not None

    @loader.command()
    async def installuwufetchcmd(self, message):
        """- установить uwufetch"""
        if platform.system() not in ["Linux", "Darwin"]:
            return await utils.answer(
                message, 
                self.strings["not_supported"]
            )

        deps_ok, missing_dep = await self._check_dependencies()
        if not deps_ok:
            await utils.answer(
                message, 
                self.strings[f"no_{missing_dep}"]
            )
            return

        message = await utils.answer(message, "<emoji document_id=5326015457155620929>⏳</emoji>")
        try:
            # Проверяем, существует ли уже директория
            if os.path.exists("uwufetch"):
                shutil.rmtree("uwufetch")

            # Определяем нужен ли sudo
            needs_sudo = platform.system() == 'Linux' and not self._is_root()
            if needs_sudo and not self._has_sudo():
                return await utils.answer(
                    message,
                    "<emoji document_id=5328145443106873128>❌</emoji> Для установки необходимы права root. Запустите от root или установите sudo."
                )

            install = (
                "git clone https://github.com/TheDarkBug/uwufetch.git && "
                "cd uwufetch && "
                "make build && "
                f"{'sudo ' if needs_sudo else ''}make install"
            )

            process = subprocess.run(
                install, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if process.returncode == 0:
                await utils.answer(message, "<emoji document_id=5237699328843200968>✅</emoji> Uwufetch успешно установлен")
            else:
                await utils.answer(
                    message, 
                    f"<emoji document_id=5210952531676504517>❌</emoji> Ошибка при установке Uwufetch\n<pre>{process.stderr}</pre>"
                )

        except Exception as e:
            await utils.answer(
                message, 
                f"<emoji document_id=5210952531676504517>❌</emoji> Ошибка при установке Uwufetch\n<pre>{str(e)}</pre>"
            )

    @loader.command()
    async def uninstalluwufetchcmd(self, message):
        """- удалить uwufetch"""
        if platform.system() not in ["Linux", "Darwin"]:
            return await utils.answer(message, self.strings["not_supported"])

        needs_sudo = platform.system() == 'Linux' and not self._is_root()
        if needs_sudo and not self._has_sudo():
            return await utils.answer(
                message,
                "<emoji document_id=5210952531676504517>❌</emoji> Для удаления необходимы права root. Запустите от root или установите sudo."
            )

        message = await utils.answer(message, "<emoji document_id=5326015457155620929>⏳</emoji>")
        try:
            if not os.path.exists("uwufetch"):
                # Если директории нет, пробуем удалить только бинарный файл
                uninstall = f"{'sudo ' if needs_sudo else ''}make -C /usr/local uninstall"
            else:
                uninstall = (
                    "cd uwufetch && "
                    f"{'sudo ' if needs_sudo else ''}make uninstall"
                )

            process = subprocess.run(
                uninstall, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            if os.path.exists("uwufetch"):
                shutil.rmtree("uwufetch")

            if process.returncode == 0:
                await utils.answer(message, "<emoji document_id=5237699328843200968>✅</emoji> Uwufetch успешно удален")
            else:
                error_msg = await utils.answer(
                    message, 
                    f"<emoji document_id=5210952531676504517>❌</emoji> Ошибка при удалении Uwufetch\n<pre>{process.stderr}</pre>"
                )
                await asyncio.sleep(self.config["delete_timeout"])
                await error_msg.delete()

        except Exception as e:
            error_msg = await utils.answer(
                message, 
                f"<emoji document_id=5210952531676504517>❌</emoji> Ошибка при удалении Uwufetch\n<pre>{str(e)}</pre>"
            )
            await asyncio.sleep(self.config["delete_timeout"])
            await error_msg.delete()
