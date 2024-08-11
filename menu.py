import nuke
import KnobHijacker
import EventFilters

FILTER = EventFilters.CustomEventFilter()

refresh_command = '''print("Refreshing Hijacker Code and Settings.")\n
import importlib\n
import KnobHijacker\n
importlib.reload(KnobHijacker)\n
import KnobHijacker\n
hijack = KnobHijacker.Hijack()\n
add_hijacker_menus()'''

def add_hijacker_menus():
    slider_menu = nuke.toolbar("Nodes")
    slider_menu.addCommand("Fix Gizmos/Scripts/Hijacker/Hijack Knob", "KnobHijacker.Hijack().run(nuke.selectedNode())", "-")
    slider_menu.addCommand("Fix Gizmos/Scripts/Hijacker/Refresh", refresh_command)

add_hijacker_menus()