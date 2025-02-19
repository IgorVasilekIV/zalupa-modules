# meta developer: @MrAmigoch (with support from @IgorVasilekIV)
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

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class Femboy(loader.Module):
    """Femboy Modul"""

    strings = {
        "name": "FemBoy",

        "p_on": "<b><emoji <emoji document_id=5341813983252851777>🌟</emoji> Режим Femboy^^ включен!</b>",
        "p_off": "<b><emoji <emoji document_id=5318833180915027058>😭</emoji> режим Femboy выключен!</b>",
    }

## secret🤫
