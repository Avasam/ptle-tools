# https://github.com/Felk/dolphin/tree/scripting-preview2

# pylint: disable=await-outside-async
# pyright: reportUnknownVariableType=false, reportMissingModuleSource=false, reportUnknownMemberType=false
from dolphin import event, gui, memory

current_area_old: int = 0
current_area_new: int = 0
JAGUAR = 0x99885996
CRASH_SITE = 0xEE8F6900
PLANE_COCKPIT = 0x4A3E4058
CHAMELEON_TEMPLE = 0x0081082C
JUNGLE_CANYON = 0xDEDA69BC
MAMA_OULLO_TOWER = 0x07ECCC35

def highjack_transition(from_: int, to: int, redirect: int):
    if from_==current_area_old and to == current_area_new:
        memory.write_u32(0x8041BEB4, redirect)
        return True
    return False

while True:
    current_area_old = current_area_new
    await event.frameadvance()  # pyright: ignore
    current_area_new = memory.read_u32(0x8041BEB4)
    gui.draw_text((272, 24), 0xFF00FFFF, f"Current area ID: {hex(current_area_new)}")
    print(f"Current area ID: {hex(current_area_new)}")

    if highjack_transition(0x0, JAGUAR, CRASH_SITE):
        continue

    if highjack_transition(CRASH_SITE, PLANE_COCKPIT, CHAMELEON_TEMPLE):
        continue

    if highjack_transition(CHAMELEON_TEMPLE, JUNGLE_CANYON, MAMA_OULLO_TOWER):
        continue
