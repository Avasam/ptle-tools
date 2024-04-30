
from __future__ import annotations

import random
from enum import IntEnum
from typing import Literal

import CONFIGS
from lib.constants import *  # noqa: F403

MAX_IDOLS = 138
DEFAULT_SHOP_PRICES = [2, 4, 8, 16, 32, 1, 2, 3, 4, 5, 10, 10, 10, 9, 7, 7, 8, 0]
MAPLESS_SHOP_PRICES = [0x04, 8, 16, 32, 0x00003, 4, 5, 10, 10, 10, 9, 7, 7, 8]
"""Same as `DEFAULT_SHOP_PRICES` but with 4 lowest prices removed."""


class ShopPriceOffset(IntEnum):
    ExtraHealth1 = 4
    ExtraHealth2 = 8
    ExtraHealth3 = 12
    ExtraHealth4 = 16
    ExtraHealth5 = 20
    Canteen1 = 92
    Canteen2 = 96
    Canteen3 = 100
    Canteen4 = 104
    Canteen5 = 108
    SmashStrike = 36
    SuperSling = 44
    Breakdance = 28
    JungleNotes = 60
    NativeNotes = 52
    CavernNotes = 68
    MountainNotes = 76
    MysteryItem = 84


class ShopCountOffset(IntEnum):
    ExtraHealth = ShopPriceOffset.ExtraHealth1 - 4
    Canteen = ShopPriceOffset.Canteen1 - 4
    SmashStrike = ShopPriceOffset.SmashStrike - 4
    SuperSling = ShopPriceOffset.SuperSling - 4
    Breakdance = ShopPriceOffset.Breakdance - 4
    JungleNotes = ShopPriceOffset.JungleNotes - 4
    NativeNotes = ShopPriceOffset.NativeNotes - 4
    CavernNotes = ShopPriceOffset.CavernNotes - 4
    MountainNotes = ShopPriceOffset.MountainNotes - 4
    MysteryItem = ShopPriceOffset.MysteryItem - 4


_shaman_shop_prices = DEFAULT_SHOP_PRICES
_shaman_shop_prices_string = ""


def randint_with_bias(
    a: int,
    b: int,
    bias: int = 1,
    direction: Literal["start", "middle"] = "middle",
):
    """
    Run randint multiple times then averaged and rounded to create a bell-curve bias.

    The bias strength is the number of iteration. So 1 is no bias.
    """
    if bias < 1:
        raise ValueError(f"{bias=} is smaller than 1.")

    total = 0

    if direction == "start":
        for _ in range(bias):
            total += random.random()
        total /= bias

        # Bias towards the start by spreading the range over [-1, 1) then abs.
        total = abs((total * 2) - 1)
        # Spread the range from [0, 1) to [0, b-a+1)
        total *= b - a + 1
        # Raise the range from [0, b-a) to [a, b+1)
        total += a
        return int(total)

    if direction == "middle":
        for _ in range(bias):
            total += random.randint(a, b)

        return round(total / bias)

    raise ValueError(f"Invalid {direction=}.")


def randomize_shaman_shop():
    global _shaman_shop_prices
    global _shaman_shop_prices_string
    if ADDRESSES.shaman_shop_struct == TODO:
        return

    _shaman_shop_prices = MAPLESS_SHOP_PRICES[:] \
        if CONFIGS.DISABLE_MAPS_IN_SHOP \
        else DEFAULT_SHOP_PRICES[:]

    if CONFIGS.SHOP_PRICES_RANGE:
        shop_size = len(_shaman_shop_prices)
        idols_left = MAX_IDOLS
        equal_price_per_item = idols_left // shop_size
        minimum_max_price = equal_price_per_item + 1
        max_price = max(minimum_max_price, CONFIGS.SHOP_PRICES_RANGE[1])
        min_price = min(max_price, equal_price_per_item, CONFIGS.SHOP_PRICES_RANGE[0])
        _shaman_shop_prices: list[int] = []
        for items_left in range(shop_size, 0, -1):
            # Ensure we don't bust the total of idols
            max_price = min(idols_left, max_price)

            equal_price_per_item_left = idols_left // items_left
            maximum_min_price = min(max_price, equal_price_per_item_left)
            min_price = min(min_price, maximum_min_price)

            # Ensure a full fill when possible
            if max_price * (items_left - 1) <= idols_left:
                # Last few items in the shop, and it's currently possible for
                # low rolls to not total 138, use as many idols as as needed
                min_price = maximum_min_price
            # Ramp up min_price to avoid having to deal with a bunch of forced 0 price near the end
            # note we already know that `max_price <= idols_left` so no need to check
            elif max_price <= items_left:
                min_price = maximum_min_price

            # Strongly bias the distribution towards the middle
            price = randint_with_bias(min_price, max_price, 3, "start")
            print(f"\n{idols_left=}, {price=}, {min_price=}, {max_price=}, {maximum_min_price=}, {items_left=}\n")  # noqa: E501

            idols_left -= price
            if idols_left < 0:
                raise RuntimeError(f"Oops, somehow we used too many idols! {idols_left=}, {price=}, {min_price=}, {max_price=}")  # noqa: E501
            _shaman_shop_prices.append(price)

            # Try to avoid repeated low prices
            if price == min_price < maximum_min_price:
                min_price += 1

            # Try to avoid repeated high prices
            if price == max_price > max(minimum_max_price, min_price):
                max_price -= 1

        if sum(_shaman_shop_prices) != MAX_IDOLS:
            raise RuntimeError(f"{_shaman_shop_prices=} totals {sum(_shaman_shop_prices)}, which isn't {MAX_IDOLS}.")  # noqa: E501

    random.shuffle(_shaman_shop_prices)
    if CONFIGS.DISABLE_MAPS_IN_SHOP:
        _shaman_shop_prices.insert(13, -1)
        _shaman_shop_prices.insert(14, -1)
        _shaman_shop_prices.insert(15, -1)
        _shaman_shop_prices.insert(16, -1)

    array_repr = str(_shaman_shop_prices).replace(" ", "").replace("-1", "Ø")
    array_sum = sum(_shaman_shop_prices) + (4 if CONFIGS.DISABLE_MAPS_IN_SHOP else 0)
    _shaman_shop_prices_string = f"Shaman Shop: {array_repr} total {array_sum}"
    print(_shaman_shop_prices_string)

    max_health = sorted(_shaman_shop_prices[:5])
    _shaman_shop_prices[:5] = max_health

    max_canteen = _shaman_shop_prices[5:10]
    max_canteen.sort()
    _shaman_shop_prices[5:10] = max_canteen


def patch_shaman_shop():
    if CONFIGS.DISABLE_MAPS_IN_SHOP:
        for offset in (
                ShopCountOffset.JungleNotes,
                ShopCountOffset.NativeNotes,
                ShopCountOffset.CavernNotes,
                ShopCountOffset.MountainNotes,
        ):
            memory.write_u32(ADDRESSES.shaman_shop_struct + offset, 0)

    for index, offset in enumerate(ShopPriceOffset):
        memory.write_u32(ADDRESSES.shaman_shop_struct + offset, _shaman_shop_prices[index])

    return _shaman_shop_prices_string
