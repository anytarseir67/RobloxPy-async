import webbrowser, time, sys, random
from asyncinit import asyncinit
from async_property import async_property
from . import Utils, asset, errors
from typing import Type, Tuple
robloxpy = sys.modules['robloxpy_async']

user = None

@asyncinit
class Place():
    __slots__ = ('id', 'name', 'description', 'url', 'builder', 'playable', 'universe', 'price')

    async def __init__(self, id: int) -> None:
        await self._update(id)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Place):
            return self.id == other.id
        return False

    async def _update(self, id: int) -> None:
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        session = robloxpy.CurrentCookie
        async with session.get(f"{Utils.GamesAPI}games/multiget-place-details?placeIds={id}") as resp:
            data = await resp.json()
        data = data[0]
        self.id = data['placeId']
        self.name = data['name']
        self.description = data['description']
        self.url = data['url']
        self.builder = await user.User(data['builderId'])
        self.playable = data['isPlayable']
        self.universe = await Universe(data['universeId'])
        self.price = data['price']

    async def _icon(self, size: int = 512) -> str:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}places/gameicons?format=Png&isCircular=false&placeIds={self.id}&size={size}x{size}") as resp:
            data = await resp.json()
        return data['data'][0]['imageUrl']

    @async_property
    async def icon(self) -> Type[asset.ImageAsset]:
        """
        Returns the places icon as an ImageAsset.
        """
        return asset.ImageAsset(await self._icon())
    
    async def _thumbnail(self, width: int = 768, height: int = 432) -> str:
        if self.universe == None:
            raise errors.NoUniverse
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}games/multiget/thumbnails?format=Png&isCircular=false&universeIds={self.universe.id}&size={width}x{height}") as resp:
            data = await resp.json()
        return data['data'][0]['imageUrl']

    @async_property
    async def thumbnail(self) -> Type[asset.ImageAsset]:
        """
        Returns the places thumbnail as an ImageAsset.
        """
        return asset.ImageAsset(await self._thumbnail())

    @async_property
    async def playing(self) -> int:
        """
        Returns the current ammount of players in the places universe.
        """
        if self.universe == None:
            raise errors.NoUniverse
        return await self.universe.playing

    @async_property
    async def visits(self) -> int:
        """
        Returns the total visits for the places universe.
        """
        if self.universe == None:
            raise errors.NoUniverse
        return await self.universe.visits

    @async_property
    async def favorites(self) -> int:
        """
        Returns the total favorites for the places universe.
        """
        if self.universe == None:
            raise errors.NoUniverse
        return await self.universe.favorites

    @async_property
    async def votes(self) -> int:
        """
        Returns the "score" of the places universe (upvotes - downvotes).
        """
        dat = await self.raw_votes()
        return dat[0] - dat[1]

    async def raw_votes(self) -> Tuple[int]:
        """
        Returns the raw vote data from the api. Returned as (upvotes, downvotes)
        """
        if self.universe == None:
            raise errors.NoUniverse
        return await self.universe.raw_votes()

    async def join(self) -> None:
        """
        Joins the given game
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie
            
        async with robloxpy.CurrentCookie.post(url = Utils.GameAuthUrl) as resp:
            ticket = resp.headers["rbx-authentication-ticket"]
        BrowserID = random.randint(10000000000, 99999999999)
        webbrowser.open(f"roblox-player:1+launchmode:play+gameinfo:{ticket}+launchtime:{int(time.time()*1000)}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{BrowserID}%26placeId%3D{self.id}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{self.id}+robloxLocale:en_us+gameLocale:en_us")

@asyncinit
class Universe():
    __slots__ = ('id', 'name', 'description', 'creator', 'price', 'allowed_gear_genres', 'genre_enforced', 'copying_allowed', 'max_players', 'created_at', 'updated_at', 'vip_servers', 'avatar_type', 'genre', 'all_genre', 'rating')
    
    async def __init__(self, id: int) -> None:
        await self._update(id)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Universe):
            return self.id == other.id
        return False
        
    async def _update(self, id: int) -> None:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games?universeIds={id}") as resp:
            data = await resp.json()
        data = data['data'][0]
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.creator = await user.User(data['creator']['id'])
        self.price = data['price']
        self.allowed_gear_genres = data["allowedGearGenres"]
        self.genre_enforced = data['isGenreEnforced']
        self.copying_allowed = data['copyingAllowed']
        self.max_players = data['maxPlayers']
        self.created_at = data['created']
        self.updated_at = data['updated']
        self.vip_servers = data['createVipServersAllowed']
        self.avatar_type = data['universeAvatarType']
        self.genre = data['genre']
        self.all_genre = data['isAllGenre']
        self.rating = data['gameRating']

    @async_property
    async def root_place(self) -> Type[Place]:
        """
        Returns the root place as a Place
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games?universeIds={self.id}") as resp:
            data = await resp.json()
        return await Place(data['data'][0]['rootPlaceId'])
    
    @async_property
    async def playing(self) -> int:
        """
        Returns the current ammount of players in the universe
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games?universeIds={self.id}") as resp:
            data = await resp.json()
        return data['data'][0]['playing']

    @async_property
    async def visits(self) -> int:
        """
        Returns the total visits for the universe.
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games?universeIds={self.id}") as resp:
            data = await resp.json()
        return data['data'][0]['visits']

    @async_property
    async def favorites(self) -> int:
        """
        Returns the total favorites for the universe.
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games?universeIds={self.id}") as resp:
            data = await resp.json()
        return data['data'][0]['favoritedCount']

    @async_property
    async def votes(self) -> int:
        """
        Returns the "score" for the universe (upvotes - downvotes).
        """
        dat = await self.raw_votes()
        return dat[0] - dat[1]

    async def raw_votes(self) -> Tuple[int]:
        """
        Returns the raw vote data from the api. Returned as (upvotes, downvotes)
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GamesAPI}games/votes?universeIds={self.id}") as resp:
            data = await resp.json()
        data = data['data'][0]
        return (data['upVotes'], data['downVotes'])

    async def _icon(self, size: int = 512) -> str:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}games/icons?format=Png&isCircular=false&size={size}x{size}&universeIds={self.id}") as resp:
            data = await resp.json()
        return data['data'][0]['imageUrl']

    @async_property
    async def icon(self) -> Type[asset.ImageAsset]:
        """
        Returns the universes icon as an ImageAsset
        """
        return asset.ImageAsset(await self._icon())

    async def join(self) -> None:
        """
        Joins the given game
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie
        async with robloxpy.CurrentCookie.post(url = Utils.GameAuthUrl) as resp:
            ticket = resp.headers["rbx-authentication-ticket"]
        BrowserID = random.randint(10000000000, 99999999999)
        root_place = await self.root_place.id
        webbrowser.open(f"roblox-player:1+launchmode:play+gameinfo:{ticket}+launchtime:{int(time.time()*1000)}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{BrowserID}%26placeId%3D{root_place}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{root_place}+robloxLocale:en_us+gameLocale:en_us")

def _get_user():
    global user
    from . import user as usr
    user = usr
_get_user()