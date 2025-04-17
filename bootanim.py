"""
ARCHIVED
"""
# чатгпт кормит, больные мозги тоже
#
# meta banner (change) https://files.catbox.moe/nldg9c.jpg
# meta pic: https://files.catbox.moe/nldg9c.jpg
# meta developer: @HikkaZPM
#
# The module is made as a joke, all coincidences are random :P
# 
#       кот вахуи
#       /\_____/\
#      /  o   o  \
#     ( ==  ^  == )
#      )         (
#     (           )
#    ( (  )   (  ) )
#   (__(__)___(__)__)
# 
#
from hikkatl.types import Message
from .. import loader, utils
from hikkatl.errors import ChannelPrivateError
import asyncio
import logging
logger = logging.getLogger(__name__)

@loader.tds
class BootAnimModUPD(loader.Module):
    """Модуль для создания boot animation через группу (фиксированный ID)"""
    
    strings = {"name": "BootAnimUPD"}

# coming soon...