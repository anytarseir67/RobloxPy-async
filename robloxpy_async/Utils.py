import aiohttp, os, sys
from json.decoder import JSONDecodeError

robloxpy = sys.modules['robloxpy']

TestCookie = ""

#URL List

MobileAPI = "https://www.roblox.com/mobileapi/"
FriendsAPI = "https://friends.roblox.com/v1/"
APIURL = "https://api.roblox.com/"
UserAPI = "https://api.roblox.com/users/"
UserAPIV1 = "https://users.roblox.com/v1/users/"
GroupAPIV1 = "https://groups.roblox.com/v1/groups/"
GroupAPIV2 = "https://groups.roblox.com/v2/"
EconomyURL = "https://economy.roblox.com/v1/"
EconomyURLV2 = "https://economy.roblox.com/v2/"
InventoryURLV1 = "https://inventory.roblox.com/v1/"
InventoryURLV2 = "https://inventory.roblox.com/v2/"
SettingsURL = "https://www.roblox.com/my/settings/json"
PrivateMessageAPIV1 = "https://privatemessages.roblox.com/v1/"
GamesAPI = "https://games.roblox.com/v1/"
DevelopAPIV2 = "https://develop.roblox.com/v2/"
GameAuthUrl = "https://auth.roblox.com/v1/authentication-ticket/"
ThumnnailAPIV1 = "https://thumbnails.roblox.com/v1/"

async def SetProxy(ProxyIP: str) -> None:
    """
    Set the proxy to currently be used, this is global
    Format: IP:Port
    """
    #Format 144.217.101.245:3129
    if(ProxyIP != None):
        proxy = 'http://' + str(ProxyIP)
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy

async def CheckProxy(proxyAddress: str = None) -> str:
    """
    Check the current IP address being given by the program
    """
    await SetProxy(proxyAddress)
    session = await robloxpy.get_session()
    async with session.get('https://api.ipify.org/?format=json') as resp:
        data = await resp.json()
    return data['ip']

async def CheckCookie(Cookie: str = None) -> bool:
    """
    If you want to check the current used cookie just run the function without any arguments, if you wish to check a specific cookie then enter the cookie as a string
    """
    try:
        Cookie = Cookie or robloxpy.RawCookie
        session = aiohttp.ClientSession(cookies={'.ROBLOSECURITY': Cookie})
        async with session.post('https://auth.roblox.com/') as resp:
            token = resp.headers['x-csrf-token']
        async with session.get(MobileAPI + 'userinfo', headers={'x-csrf-token': token}) as resp:
            data = await resp.json()
        await session.close()
        try:
            Temp = data['UserID']
            return True
        except (KeyError, JSONDecodeError):
            return False
    except TypeError:
        return False
