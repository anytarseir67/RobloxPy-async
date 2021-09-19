import sys, webbrowser, time, random
from . import Utils, errors, asset, group, game
from typing import List, Type, Union
from async_property import async_property
from asyncinit import asyncinit

robloxpy = sys.modules['robloxpy_async']
ClientId = None

@asyncinit
class BaseUser():
    async def __init__(self, id: Union[int, str], fetch: bool = True):
        await self._update(id, fetch)

    def __repr__(self) -> str:
        return self.name or str(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseUser):
            return self.id == other.id
        return False

    async def _update(self, id: Union[int, str], fetch: bool) -> None:
        session = await robloxpy.get_session()
        if type(id) != int:
            async with session.get(Utils.APIURL + f'users/get-by-username?username={id}') as resp:
                data = await resp.json()
                id = data['Id']
        if fetch:
            async with session.get(f"{Utils.UserAPIV1}/{id}") as resp:
                try:
                    rawData = await resp.json()
                    self.id = id
                    self.name = rawData['name']
                    self.display_name = rawData['displayName']
                    self.description = rawData['description']
                    self.created_at = rawData['created']
                    self.banned = rawData['isBanned']
                except (KeyError, AttributeError):
                    raise errors.InvalidId
        else:
            self.id = id
            self.name = None
            self.display_name = None
            self.description = None
            self.created_at = None
            self.banned = None

    @async_property
    async def online(self) -> bool:
        """
        Returns if the user is online.
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.UserAPI}{self.id}/onlinestatus") as resp:
            data = await resp.json()
        return data['IsOnline']

    @async_property
    async def name_history(self) -> List[str]:
        """
        Returns the users previous names.
        """
        session = await robloxpy.get_session()
        Cursor = ""
        Done = False
        PastNames = []
        while(Done == False):
            async with session.get(Utils.UserAPIV1 + f"{self.id}/username-history?limit=100&sortOrder=Asc&cursor={Cursor}") as resp:
                data = await resp.json()
                Names = data['data']
            if((data['nextPageCursor'] == "null") or data['nextPageCursor'] == None):
                Done = True
            else:
                Done = False
                Cursor = data['nextPageCursor']
            for Name in Names:
                PastNames.append(Name['name'])
            if(data['nextPageCursor'] == 'None'):
                Done = True
        return PastNames

    @async_property
    async def rap(self) -> int:
        """
        Returns the users recent average price.
        """
        session = await robloxpy.get_session()
        TotalValue = 0
        Cursor = ""
        Done = False
        while(Done == False):
            try:
                async with session.get(Utils.Inventory1URL + f"/{self.id}/assets/collectibles?sortOrder=Asc&limit=100&cursor={Cursor}") as resp:
                    data = await resp.json()
                if data['nextPageCursor'] == "null" or data['nextPageCursor'] == None:
                    Done = True
                else:
                    Done = False
                    Cursor = data['nextPageCursor']
                for Item in data["data"]:
                    try:
                        RAP = int(Item['recentAveragePrice'])
                        TotalValue = TotalValue + RAP
                    except:
                        TotalValue = TotalValue
                if data['nextPageCursor'] == 'None':
                    Done = True
            except Exception as ex:
                Done = True
        return TotalValue

    @async_property
    async def status(self) -> str:
        """
        Returns the users status.
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.UserAPIV1}{str(self.id)}/status") as resp:
            data = await resp.json()
        return data['status']

    async def _headshot(self, size: int = 720) -> str:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}users/avatar-headshot?userIds={self.id}&size={size}x{size}&format=png") as resp:
            data = await resp.json()
        return data['data'][0]['imageUrl']

    @async_property
    async def headshot(self) -> Type[asset.ImageAsset]:
        """
        Returns the users headshot as an ImageAsset.
        """
        return asset.ImageAsset(await self._headshot())

    async def _bust(self, size: int = 420) -> str:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}users/avatar-bust?userIds={self.id}&size={size}x{size}&format=png") as resp:
            data = await resp.json()
        return data['data'][0]['imageUrl']

    @async_property
    async def bust(self) -> Type[asset.ImageAsset]:
        """
        Returns the users bust as an ImageAsset.
        """
        return asset.ImageAsset(await self._bust())

    async def groups(self) -> List[Type[group.Group]]:
        """
        Returns the groups the user is in
        """
        groups = []
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GroupAPIV2}users/{self.id}/groups/roles") as resp:
            data = await resp.json()
        for _group in data['data']:
            groups.append(group.Group(_group['group']['id']))
        return groups

    async def limiteds(self) -> List[Type[asset.MarketAsset]]:
        """
        Returns the users limited items 
        """
        Limiteds = []
        Cursor = ""
        Done = False
        session = await robloxpy.get_session()
        while(Done == False):
            try:
                async with session.get(f"{Utils.InventoryURLV1}users/{self.id}/assets/collectibles?limit=100&sortOrder=Asc") as resp:
                    Items = await resp.json()
                if Items['nextPageCursor'] == "null" or Items['nextPageCursor'] == None:
                    Done = True
                else:
                    Done = False
                    Cursor = Items['nextPageCursor']
                for Item in Items["data"]:
                    try:
                        Limiteds.append(asset.MarketAsset(Item['assetId']))
                    except:
                        continue
                if Items['nextPageCursor'] == 'None':
                    Done = True
                
            except Exception as ex:
                Done = True
        return Limiteds

class PartialUser():
    __slots__ = ('id')
    def __init__(self, id: int):
        self.id = id

    def __repr__(self) -> str:
        return str(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, BaseUser):
            return self.id == other.id
        return False

    async def fetch(self) -> 'User':
        """
        Returns the User instance for the PartialUser
        """
        return await User(self.id)

class User(BaseUser):
    @async_property
    async def following(self) -> bool:
        """
        returns if the client user is following this user.
        redundant, might be removed
        """
        session = robloxpy.CurrentCookie
        async with session.post(f"{Utils.FriendsAPI}user/following-exists?UserID={str(self.id)}&followerUserID={self.id}", data={'targetUserIDs': str(self.id)}) as resp:
            data = await resp.json()
        return data['followings'][0]['isFollowing']

    async def send_message(self, Subject: str, Body: str) -> Union[str, dict]:
        """
        Sends the given message to the user
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        async with robloxpy.CurrentCookie.post(Utils.PrivateMessageAPIV1 + 'messages/send', data={'userId': ClientId, 'subject': Subject, 'body': Body, 'recipientId': self.id}) as resp:
            return await resp.json()


    async def follow(self) ->  Union[bool, str]:
        """
        Follows a user.
        captcha blocked, might be removed.
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        async with robloxpy.CurrentCookie.post(f"{Utils.FriendsAPI}users/{self.id}/follow", data={'targetUserID': self.id}) as resp:
            try:
                return resp.json()['success']
            except:
                return resp.json()['errors']

    async def unfollow(self) ->  Union[bool, str]:
        """
        unfollows the user
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        async with robloxpy.CurrentCookie.post(f"{Utils.FriendsAPI}users/{self.id}/unfollow", data={'targetUserID': self.id}) as resp:
            try:
                return resp.json()['success']
            except:
                return resp.json()['errors']

    async def block(self) -> Union[bool, str]:
        """
        Blocks the user
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        async with robloxpy.CurrentCookie.post(f"{Utils.APIURL}userblock/block?userId={self.id}", data={'targetUserID': self.id}) as resp:
            try:
                return resp.json()['success']
            except:
                return resp.json()['errors']

    async def unblock(self) -> Union[bool, str]:
        """
        Unlocks the user
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie
        async with robloxpy.CurrentCookie.post(f"{Utils.APIURL}userblock/unblock?userId={self.id}", data={'targetUserID': self.id}) as resp:
            try:
                return resp.json()['success']
            except:
                return resp.json()['errors']


class ClientUser(BaseUser):
    async def __init__(self, id: Union[int, str]) -> None:
        await super().__init__(id)
        global ClientId
        ClientId = self.id

    async def blocked_users(self) -> List[Type[User]]:
        """
        Returns users which are blocked
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        async with robloxpy.CurrentCookie.get(f"{Utils.SettingsURL}") as resp:
            data = await resp.json()
        BlockedUsers = []
        for _User in data['BlockedUsersModel']['BlockedUsers']:
            BlockedUsers.append(User(_User['uid']))
        return BlockedUsers

    async def following_user(self, targetUser: Union[Type[User], int]) -> bool:
        """
        Checks if the current account is following a user
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        if isinstance(targetUser, BaseUser):
            targetUser = targetUser.id

        async with robloxpy.CurrentCookie.post(f"{Utils.FriendsAPI}user/following-exists?UserID={str(targetUser)}&followerUserID={self.id}", data={'targetUserIDs': str(targetUser)}) as resp:
            data = await resp.json()
        return data['followings'][0]['isFollowing']

    async def join_game(self, place: Union[int, Type[game.Place]]) -> None:
        """
        Joins the given game
        """
        if robloxpy.CurrentCookie == None:
            raise errors.NoCookie

        if isinstance(place, game.Place):
            place = place.id

        async with robloxpy.CurrentCookie.post(url = Utils.GameAuthUrl) as resp:
            ticket = resp.headers["rbx-authentication-ticket"]
        BrowserID = random.randint(10000000000, 99999999999)
        webbrowser.open(f"roblox-player:1+launchmode:play+gameinfo:{ticket}+launchtime:{int(time.time()*1000)}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{BrowserID}%26placeId%3D{place}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{BrowserID}+robloxLocale:en_us+gameLocale:en_us")


