import sys
from asyncinit import asyncinit
from async_property import async_property
from . import Utils
from typing import List, Union

User = None
PartialUser = None
robloxpy = sys.modules['robloxpy']

@asyncinit
class Group():
    __slots__ = ('id', 'name', 'description', 'owner', 'member_count', 'builders_club_only', 'public_entry')
    async def __init__(self, id: int) -> None:
        await self._update(id)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Group):
            return self.id == other.id
        return False

    async def _update(self, id: int) -> None:
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GroupAPIV1}{id}") as data:
            raw_json = await data.json()
        self.id = raw_json['id']
        self.name = raw_json['name']
        self.description = raw_json['description']
        if raw_json['owner'] != None:
            self.owner = PartialUser(raw_json['owner']['userId'])
        else:
            self.owner = None
        self.member_count = raw_json['memberCount']
        self.builders_club_only = raw_json['isBuildersClubOnly']
        self.public_entry = raw_json['publicEntryAllowed']

    @async_property
    async def allies(self) -> List['Group']:
        """
        Returns the groups allies as a list of Group instances.
        """
        _allies = []
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GroupAPIV1}{self.id}/relationships/allies?model.startRowIndex=0&model.maxRows=100000") as resp:
            data = await resp.json()
        for group in data['relatedGroups']:
            _allies.append(await Group(group['id']))
        return _allies

    @async_property
    async def enemies(self) -> List['Group']:
        """
        Returns the groups enemies as a list of Group instances.
        """
        _enemies = []
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.GroupAPIV1}{self.id}/relationships/enemies?model.startRowIndex=0&model.maxRows=100000") as resp:
            data = await resp.json()
        for group in data['relatedGroups']:
            _enemies.append(Group(group['id']))
        return _enemies

    async def members(self, fetch: bool = False) -> Union[List['PartialUser'], List['User']]:
        """
        Returns a list of all members in the group. this method can be extraordinarily slow depending on group size.
        by default the members are not fetched and do not contain any attributes, this can be changed be setting fetch to True, be aware this has a high chance of being rate limited
        """
        Cursor = ""
        Done = False
        _members = []
        session = await robloxpy.get_session()
        while(Done == False):
            async with session.get(f"{Utils.GroupAPIV1}{self.id}/users?limit=100&sortOrder=Asc&cursor={Cursor}") as resp:
                data = await resp.json()
            _users = data['data']
            if data['nextPageCursor'] == "null" or data['nextPageCursor'] == None:
                Done = True
            else:
                Done = False
                Cursor = data['nextPageCursor']
            for _user in _users:
                try:
                    if not fetch:
                        _members.append(PartialUser(_user['user']['userId']))
                        continue
                    _members.append(await User(_user['user']['userId']))
                except:
                    pass
            if data['nextPageCursor'] == 'None':
                Done = True
        return _members

def _get_user():
    global User
    global PartialUser
    from . import user as usr
    User = usr.User
    PartialUser = usr.PartialUser
_get_user()