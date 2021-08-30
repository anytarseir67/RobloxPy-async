from . import group
from . import user
from . import Utils
from . import errors
from . import asset
from . import game
import aiohttp
import sys

__version__ = "1.0.0.a1"

this = sys.modules[__name__]

this.CurrentCookie = None
this.RawCookie = None

async def get_session():
    if this.session == None:
        this.session = aiohttp.ClientSession()
    return this.session

this.session = None

async def SetCookie(Cookie: str) -> None:
    """
    Set the current cookie for internal commands.
    """
    try:
        CurrentCookie = {'.ROBLOSECURITY': Cookie}
        session = aiohttp.ClientSession(cookies=CurrentCookie)
        async with session.post('https://auth.roblox.com/') as Header:
            session.headers['x-csrf-token'] = Header.headers['x-csrf-token']
        session.headers["Origin"] = "https://www.roblox.com"
        session.headers["Referer"] = "https://www.roblox.com/"
    except:
        raise errors.InvalidCookie()
    if await Utils.CheckCookie(Cookie) == False:
        raise errors.InvalidCookie()
    this.CurrentCookie = session
    this.RawCookie = Cookie

async def close() -> None:
    """
    closes both instances of ClientSession.
    """
    try:
        await this.CurrentCookie.close()
    except:
        pass
    try:
        await this.session.close()
    except:
        pass