import sys
from asyncinit import asyncinit
from . import user, Utils, errors
from typing import Union, Type, BinaryIO
from os import PathLike
from io import IOBase

robloxpy = sys.modules['robloxpy']

class ImageAsset():
    __slots__ = ('url')

    def __init__(self, url: str) -> None:
        self.url = url

    def __repr__(self):
        return self.url

    def __eq__(self, other: object) -> bool:
        if isinstance(other, ImageAsset):
            return self.url == other.url
        return False

    async def read(self) -> bytes:
        """
        Returns the image in bytes.
        """
        session = robloxpy.get_session()
        async with session.get(self.url) as resp:
            return await resp.read()

    async def save(self, fp: Union[BinaryIO, Type[PathLike]]) -> int:
        """
        Saves the image into a file-like object.
        """
        data = self.read()
        if isinstance(fp, IOBase) and fp.writable():
            return fp.write(data)
        else:
            with open(fp, 'wb') as f:
                return f.write(data)

@asyncinit
class MarketAsset():
    __slots__ = ('id', 'name', 'description', 'creator', 'lowest_price', 'price', 'favorites')

    async def __init__(self, id: int) -> None:
        await self._update(id)

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, MarketAsset):
            return self.id == other.id
        return False

    async def _update(self, id: int) -> None:
        if not robloxpy.CurrentCookie:
            raise errors.NoCookie
        try:
            async with robloxpy.CurrentCookie.post('https://catalog.roblox.com/v1/catalog/items/details', json={"items": [{"itemType": "Asset","id": id}]}) as resp:
                data = await resp.json()
            data = data['data'][0]
        except IndexError:
            raise errors.InvalidId
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.creator = await user.User(data['creatorTargetId'])
        try:
            self.lowest_price = data['lowestPrice']
        except:
            self.lowest_price = None
        try:
            self.price = data['price']
        except:
            self.price = self.lowest_price or None
        self.favorites = data['favoriteCount']

    async def thumbnail(self) -> Type[ImageAsset]:
        """
        Returns the assets thumbnail as an ImageAsset.
        """
        session = await robloxpy.get_session()
        async with session.get(f"{Utils.ThumnnailAPIV1}assets?assetIds={self.id}&format=Png&isCircular=true&size=700x700") as resp:
            data = await resp.json()
        data = data['data'][0]
        return ImageAsset(data['imageUrl'])

    async def buy(self) -> None:
        """
        purchases the asset.

        untested
        """
        async with robloxpy.CurrentCookie.post(f"https://economy.roblox.com/v1/purchases/products/{self.id}",data={"expectedCurrency":1,"expectedPrice":self.lowest_price,"expectedSellerId":None}) as resp:
            pass