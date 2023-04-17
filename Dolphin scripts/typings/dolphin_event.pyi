"""
Module for awaiting or registering callbacks on all events emitted by Dolphin.

The odd-looking Protocol classes are just a lot of syntax to essentially describe
the callback's signature. See https://www.python.org/dev/peps/pep-0544/#callback-protocols
"""
from collections.abc import Callable
from typing import Protocol, type_check_only

def on_frameadvance(callback: Callable[[], None] | None) -> None:
    """Registers a callback to be called every time the game has rendered a new frame."""

async def frameadvance() -> None:
    """Awaitable event that completes once the game has rendered a new frame."""

@type_check_only
class _MemorybreakpointCallback(Protocol):
    def __call__(self, is_write: bool, addr: int, value: int) -> None:
        """
        Example callback stub for on_memorybreakpoint.

        :param is_write: true if a value was written, false if it was read
        :param addr: address that was accessed
        :param value: new value at the given address
        """

def on_memorybreakpoint(callback: _MemorybreakpointCallback | None) -> None:
    """
    Registers a callback to be called every time a previously added memory breakpoint is hit.

    :param callback:
    :return:
    """

async def memorybreakpoint() -> tuple[bool, int, int]:
    """Awaitable event that completes once a previously added memory breakpoint is hit."""

@type_check_only
class _SaveStateCallback(Protocol):
    def __call__(self, is_slot: bool, slot: int, /) -> None:
        """
        Example callback stub for on_savestatesave and/or on_savestateload.

        :param is_slot: true if save/load was with a savestate slot, false if save/load was from a file
        :param slot: the slot the save/load occurred to/from. Should be disregarded if is_slot is false
        """

def on_savestatesave(callback: _SaveStateCallback | None) -> None:
    """
    Registers a callback to be called every time a savestate is saved.

    :param callback:
    :return:
    """

async def savestatesave() -> tuple[bool, int]:
    """Awaitable event that completes once a savestate is saved."""

def on_savestateload(callback: _SaveStateCallback | None) -> None:
    """
    Registers a callback to be called every time a savestate is loaded.

    :param callback:
    :return:
    """

async def savestateload() -> tuple[bool, int]:
    """Awaitable event that completes once a savestate is loaded."""

def system_reset() -> None:
    """Resets the emulation."""
