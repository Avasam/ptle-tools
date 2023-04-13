# Modules hidden behind a private package because `dolphin` itself is not a package
# Valid:
#   import dolphin
#   from dolphin import event
# Invalid:
#  import dolphin.event
#  from dolphin.event import ...
from ._modules import (
    controller as controller,
    event as event,
    gui as gui,
    memory as memory,
    savestate as savestate,
)
