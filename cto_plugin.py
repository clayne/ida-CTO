import ida_idaapi
import ida_kernwin
import ida_funcs

import os
import sys
import codecs

ida_idaapi.require("cto")
ida_idaapi.require("cto.cto_base")
ida_idaapi.require("cto.cto")
ida_idaapi.require("cto.icon")
ida_idaapi.require("cto.syncdata")
ida_idaapi.require("cto.qtutils")
ida_idaapi.require("cto.get_func_relation")


# for IDA 7.4 or earlier
try:
    g_flags = ida_idaapi.PLUGIN_MULTI
except AttributeError:
    g_flags = ida_idaapi.PLUGIN_DRAW

# for IDA 7.4 or earlier
try:
    g_obj = ida_idaapi.plugmod_t
except AttributeError:
    g_obj = object

g_plugmod_flag = False
if g_flags != ida_idaapi.PLUGIN_DRAW and g_obj != object:
    g_plugmod_flag = True


class cto_plugin_t(ida_idaapi.plugin_t):
    flags = g_flags
    comment = "Call Tree Overviewer"
    toolbar_displayed_name = cto.cto_base.cto_base.orig_title
    toolbar_name = toolbar_displayed_name + 'Toolbar'
    wanted_name = cto.cto.CallTreeOverviewer.orig_title
    wanted_hotkey = "Alt-Shift-C"
    help = "Press '" + wanted_hotkey + "' to display the " + wanted_name + " widget. Then press 'H' to see the help after setting focus to the widget."
    
    action_name = "cto:execute"
    menu_path = "Edit/Plugins/"
    icon = cto.icon.icon_handler(cto.icon.g_icon_data_ascii, True)
    icon_data = icon.icon_data
    icon_data_dark = icon.icon_bg_change(icon_data, True, True)
    if icon_data_dark is None:
        icon_data_dark = icon_data
    act_icon = ida_kernwin.load_custom_icon(data=icon_data, format="png")
    act_icon_dark = ida_kernwin.load_custom_icon(data=icon_data_dark, format="png")
    
    class exec_from_toolbar(ida_kernwin.action_handler_t):
        def __init__(self, plugin):
            ida_kernwin.action_handler_t.__init__(self)
            import weakref
            self.v = weakref.ref(plugin)
        
        def activate(self, ctx):
            self.v().plugin_mod.run(None)
            
        def update(self, ctx):
            return ida_kernwin.AST_ENABLE_ALWAYS
    
    def init(self):
        ida_kernwin.msg("############### %s (%s) ###############%s" % (self.wanted_name, self.comment, os.linesep))
        ida_kernwin.msg("%s%s" % (self.help, os.linesep))

        # attach to menu
        ida_kernwin.attach_action_to_menu(
            self.menu_path,
            self.action_name,
            ida_kernwin.SETMENU_APP)

        # attach to toolbar
        ida_kernwin.register_action(
            ida_kernwin.action_desc_t(
            self.action_name,
            self.comment,
            self.exec_from_toolbar(self),
            None,
            self.wanted_name,
            self.act_icon))
        
        # Insert the action in a toolbar
        ida_kernwin.create_toolbar(self.toolbar_name, self.toolbar_displayed_name)
        ida_kernwin.attach_action_to_toolbar(self.toolbar_name, self.action_name)
        
        # install ui hook to enable toolbar later
        self.ph = cto.qtutils.enable_toolbar_t(self.toolbar_name)
        
        # Check if IDA is darkmode or not.
        # It might fail if the mode is darcula or similar themes
        # because the window color is the same as the default theme color.
        # However, it can still distinguish the default and the dark mode.
        if cto.cto_base.cto_base.is_dark_mode_with_main():
            ida_kernwin.update_action_icon(self.action_name, self.act_icon_dark)
            ida_kernwin.update_action_icon(self.menu_path + self.wanted_name, self.act_icon_dark)

        r = self.flags
        self.plugin_mod = cto_plugmod_t()
        if g_plugmod_flag:
            r = self.plugin_mod
        return r

    # for old IDA til 7.6
    def run(self, arg):
        self.plugin_mod.run(arg)
        
    # for old IDA til 7.6
    def term(self):
        self.plugin_mod.term()
        
    @staticmethod
    class register_icon(ida_kernwin.UI_Hooks):
        def updated_actions(self):
            if ida_kernwin.update_action_icon(cto_plugin_t.menu_path + cto_plugin_t.wanted_name, cto_plugin_t.act_icon_dark):
                # unhook this if it's successful
                self.unhook()


class cto_plugmod_t(g_obj):
    toolbar_name = cto_plugin_t.toolbar_name
    menu_path = cto_plugin_t.menu_path
    action_name = cto_plugin_t.action_name
    act_icon = cto_plugin_t.act_icon
    wanted_name = cto_plugin_t.wanted_name
    comment = cto_plugin_t.comment
    help = cto_plugin_t.help
    
    def __init__(self):
        g_obj.__init__(self)
        self.g = None
        
    def __del__(self):
        self.term()
        
    def run(self, arg):
        self.exec_cto()
        
    def term(self):
        if self.g:
            self.g.close()
        if hasattr(self.g, "sd"):
            self.g.sd.close()
            
        ida_kernwin.free_custom_icon(self.act_icon)
        ida_kernwin.detach_action_from_menu(self.menu_path, self.action_name)
        
        ida_kernwin.detach_action_from_toolbar(self.toolbar_name, self.action_name)
        ida_kernwin.delete_toolbar(self.toolbar_name)
        
        ida_kernwin.unregister_action(self.action_name)

        if hasattr(sys.modules["__main__"], "g_cto"):
            delattr(sys.modules["__main__"], "g_cto")
        if "g_cto" in globals():
            global g_cto
            del g_cto
        self.g = None

    def exec_cto(self):
        global g_cto

        # for degub mode handling
        debug = False
        if "g_debug" in globals() and g_debug:
            debug = True
        elif hasattr(sys.modules["__main__"], "g_debug") and sys.modules["__main__"].g_debug:
            debug = True
            
        curr_view = None
        max_depth = 1
        # for the first message when this plugin is launched by a user by pressing shortcut key or going to menu.
        if 'g_cto' not in globals():
            ida_kernwin.msg("Launching %s (%s) ...%s" % (self.wanted_name, self.comment, os.linesep))
            ida_kernwin.msg("For the first execution, %s will analyze all functions to build the call tree. Please wait for a while.%s" % (self.wanted_name, os.linesep))
        else:
            ida_kernwin.msg("Reloading %s.%s" % (self.wanted_name, os.linesep))
            curr_view = g_cto.curr_view
            if g_cto.max_depth > 1:
                max_depth = g_cto.max_depth
            
        if self.g:
            ea = ida_kernwin.get_screen_ea()
            f = ida_funcs.get_func(ea)
            if f:
                ea = f.start_ea
                
            # convert start address if it is a vfunc
            if ea in self.g.vtbl_refs:
                ea = self.g.vtbl_refs[ea]
            
            drefs = list(cto.get_func_relation.get_drefs_to(ea))
            if not ea in self.g.func_relations and len(drefs) == 0 and ea not in self.g.vtbl_refs:
                ida_kernwin.msg("Current ea is not a function or an address in a function.%s" % (os.linesep))
                ida_kernwin.msg("Not reloaded.%s" % (os.linesep))
                return 0
            
            # save several important data with pickle and closing hooks...
            self.g.close()
        
        # reload the main modules
        ida_idaapi.require("cto.cto")

        # get sync data on a global variable
        sd = cto.syncdata.sync_data()
        sync_data = sd.get()
        # execute the main function
        self.g = cto.cto.exec_cto(cto_data=sync_data, curr_view=curr_view, max_depth=max_depth, debug=debug)
        self.g.exec_ui_action("EmptyStack")
        self.g.__dict__["sd"] = sd
        if sync_data is None:
            self.g.sd.set(self.g.cto_data)
            
        # show the messages after launching
        if 'g_cto' not in globals():
            ida_kernwin.msg("Launched %s.%s" % (self.wanted_name, os.linesep))
            ida_kernwin.msg("%s%s" % (self.help.split(". ")[1], os.linesep))
        else:
            ida_kernwin.msg("Reloaded %s.%s" % (self.wanted_name, os.linesep))

        # put the instance in the global variables
        g_cto = self.g
        if not hasattr(sys.modules["__main__"], "g_cto"):
            setattr(sys.modules["__main__"], "g_cto", self.g)
        else:
            sys.modules["__main__"].g_cto = self.g


def PLUGIN_ENTRY():
    return cto_plugin_t()

"""
def main():
    global g_cto
    g_cto = cto.exec_cto()


if __name__ == '__main__':
    main()
"""

ri = cto_plugin_t.register_icon()
ri.hook()
