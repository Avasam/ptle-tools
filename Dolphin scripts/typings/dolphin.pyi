"""
Aggregator module of all dolphin-provided modules.
It lets people import the dolphin-provided modules in a more
intuitive way. For example, people can then do this:
    `from dolphin import event, memory`
instead of:
    `import dolphin_event as event`
    `import dolphin_memory as memory`

Valid:
  `import dolphin`
  `from dolphin import *`
  `from dolphin import event`
  `import dolphin_event as event`
Invalid:
  `import dolphin.event`
  `from dolphin.event import ...`
"""
import dolphin_event as event
import dolphin_memory as memory
import dolphin_gui as gui
import dolphin_savestate as savestate
import dolphin_controller as controller
import dolphin_utils as utils

__all__ = [
    "event",
    "memory",
    "gui",
    "savestate",
    "controller",
    "utils",
]
