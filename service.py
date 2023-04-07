import xbmcplugin
from smartcard.CardType import AnyCardType
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardRequestTimeoutException
from smartcard.util import toHexString
import time
import sys
import requests
import xbmcaddon
import web_pdb


# nfc handling heavily inspired by https://github.com/Z3R0-CDS/NFC_UID
class Environment():
    __last_chip__ = ""
    __loop__ = True

def nfc_reader(url,debug=True ,set_timeout=120, set_cooldown = 3):
    """
    Returns UID of NFC Chip/Card
    debug -> def = True          | Output for errors etc. will be enabled
    set_timeout -> def 120/2min  | Sets timeout in seconds. Timeout for scan card.
    """
    try:
        getuid=[0xFF, 0xCA, 0x00, 0x00, 0x00]
        act = AnyCardType()
        cr = CardRequest( timeout=set_timeout, cardType=act )
        cs = cr.waitforcard()
        cs.connection.connect()
        data, sw1, sw2 = cs.connection.transmit(getuid)
        data = toHexString(data)
        data = data.replace(" ", "")
        if data != "" and data != None and data != Environment.__last_chip__:
            Environment.__last_chip__ = data
            if debug:
                print("Connection timed out... New request starting")
            requests.post("{}/{}".format(url,data))
            time.sleep(set_cooldown)
        cs=None
    except CardRequestTimeoutException:
        if debug:
            print("Connection timed out... New request starting")
    except Exception as x:
        if debug:
                print(f"Error: {x}")
    
if __name__ == "__main__":
    monitor = xbmc.Monitor()
    myaddon = xbmcaddon.Addon()
    while not monitor.abortRequested():
        nfc_reader(myaddon.getSetting('URL'))

