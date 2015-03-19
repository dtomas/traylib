import os

import gtk
import rox

import traylib
from traylib import LEFT, RIGHT
import traylib.pixmaps as pixmaps
from traylib.config import Config
from traylib.icon import Icon
from traylib.tray_config import TrayConfig
from traylib.menu_icon import MenuIcon


class Tray(object):

    def __init__(self, icon_config, tray_config, menu_icon_class=MenuIcon,
                 *menu_icon_args):
        """
        Creates a new C{Tray}.
        
        @param icon_config: The L{IconConfig} of the C{Tray}.
        @param tray_config: The L{TrayConfig} of the C{Tray}.
        """

        self.__icon_config = icon_config
        self.__tray_config = tray_config
        tray_config.add_configurable(self)

        self.__container = None

        self.__icons = {}
        self.__boxes = {}
        self.__box_separators = {}

        if self.__icon_config.vertical:
            self.__separator_left = gtk.HSeparator()
            self.__separator_right = gtk.HSeparator()
        else:
            self.__separator_left = gtk.VSeparator()
            self.__separator_right = gtk.VSeparator()
        self.__menuicon = menu_icon_class(self, icon_config, tray_config,
                                          *menu_icon_args)

        if self.__icon_config.vertical:
            self.__main_box = gtk.VBox()
            self.__box_left = gtk.VBox()
            self.__box = gtk.VBox()
            self.__box_right = gtk.VBox()
        else:
            self.__main_box = gtk.HBox()
            self.__box_left = gtk.HBox()
            self.__box = gtk.HBox()
            self.__box_right = gtk.HBox()

        self.__main_box.pack_start(self.__box_left)
        self.__main_box.pack_start(self.__box)
        self.__main_box.pack_start(self.__box_right)

        self.__main_box.show()
        self.__box_left.show()
        self.__box.show()
        self.__box_right.show()

        self.update_option_separators()
        self.update_option_menus()

        self.__main_box.connect("destroy", self.__main_box_destroyed)

    def add_box(self, box_id, separator=False, side=LEFT):
        """
        Adds a box to the C{Tray} to which icons can be added via the 
        L{add_icon()} method.
        
        @param box_id: An identifier for the box.
        @param separator: Whether to put a separator before/after the box.
        @param side: Where to add the box (C{LEFT}, C{RIGHT}).
        """
        assert box_id not in self.__boxes

        if self.__icon_config.vertical:
            box = gtk.VBox()
        else:
            box = gtk.HBox()
        box.show()
        
        if separator:
            if self.__icon_config.vertical:
                separator = gtk.HSeparator()
            else:
                separator = gtk.VSeparator()
            separator.show()
            if side == LEFT:
                self.__box.pack_start(separator)
            else:
                self.__box.pack_end(separator)
            self.__box_separators[box_id] = separator

        if side == LEFT:
            self.__box.pack_start(box)
        else:
            self.__box.pack_end(box)

        self.__boxes[box_id] = box
        self.__icons[box_id] = {}

    def remove_box(self, box_id):
        """
        Removes the box with the given ID.

        @param box_id: The identifier of the box.
        """
        self.__boxes[box_id].destroy()
        del self.__icons[box_id]
        del self.__boxes[box_id]
        try:
            del self.__box_separators[box_id]
        except KeyError:
            pass

    def has_box(self, box_id):
        """
        Returns C{True} if the tray has a box with the given ID.

        @param box_id: The identifier of the box.

        @return: C{True} if the tray has a box with the given ID.
        """
        return box_id in self.__boxes

    def clear_box(self, box_id):
        """
        Removes all icons in a box.

        @param box_id: The box to be cleared.
        """
        for icon_id in list(self.__icons[box_id]):
            self.remove_icon(icon_id)
        
    def add_icon(self, box_id, icon_id, icon):
        """
        Adds an C{Icon} to the C{Tray}.
        
        @param box_id: The identifier of the box the icon should be added to.
        @param icon_id: The identifier of the icon.
        @param icon: The C{Icon} to be added.
        """
        self.__boxes[box_id].pack_start(icon)
        self.__icons[box_id][icon_id] = icon

    def remove_icon(self, icon_id):
        """
        Removes an icon from the C{Tray}.
        
        @param icon_id: The identifier of the icon.
        """
        for icons in self.__icons.itervalues():
            try:
                icon = icons[icon_id]
            except KeyError:
                pass
            else:
                icon.destroy()
                del icons[icon_id]
        
    def destroy(self):
        """
        Destroys the C{Tray} and the container containing it.
        """
        if self.__container:
            self.__container.destroy()
        else:
            self.__main_box.destroy()

    def forget_menus(self):
        """
        Makes the C{Tray} forget its main menu. Call this if something affecting
        the main menu has changed.
        """
        if self.__menuicon_left:
            self.__menuicon_left.forget_menu()
        if self.__menuicon_right:
            self.__menuicon_right.forget_menu()

    def get_icon(self, id):
        """
        Returns the C{Icon} with the identifier C{id}
        
        @param id: The identifier of the C{Icon}
        @return: The C{Icon} with the identifier C{id}. Returns C{None} if the 
            C{Tray} has no C{Icon} with the identifier C{id}. 
        """
        for icons in self.__icons.itervalues():
            icon = icons.get(id)
            if icon is not None:
                return icon

    def set_container(self, container):
        """
        Adds the C{Tray} to the C{gtk.Container} C{container} after removing it
        from its current container.

        @param container: The C{gtk.Container} the C{Tray} will be added to
            (may be C{None}).
        """
        if self.__container == container:
            return
        if self.__container:
            self.__container.remove(self.__main_box)
        self.__container = container
        if self.__container:
            self.__container.add(self.__main_box)


    # Signal callbacks        

    def __main_box_destroyed(self, main_box):
        assert main_box == self.__main_box
        self.__tray_config.remove_configurable(self)
        self.quit()


    # Methods called when config options of the associated TrayConfig changed

    def update_option_separators(self):
        separators = self.__tray_config.separators
        vertical = self.__icon_config.vertical
        if separators & LEFT:
            if self.__separator_left not in self.__box_left.get_children():
                self.__box_left.pack_start(self.__separator_left)
                self.__separator_left.show()
        else:
            if self.__separator_left in self.__box_left.get_children():
                self.__box_left.remove(self.__separator_left)

        if separators & RIGHT:
            if self.__separator_right not in self.__box_right.get_children():
                self.__box_right.pack_end(self.__separator_right)
                self.__separator_right.show()
        else:
            if self.__separator_right in self.__box_right.get_children():
                self.__box_right.remove(self.__separator_right)

    def update_option_menus(self):
        menus = self.__tray_config.menus
        menuicon = self.__menuicon
        old_box, new_box = (menus == LEFT and (self.__box_right, self.__box_left) 
                            or (self.__box_left, self.__box_right))

        if menuicon in old_box.get_children():
            old_box.remove(menuicon)
        if menuicon not in new_box.get_children():
            new_box.pack_end(menuicon)
            menuicon.update_visibility()
            menuicon.update_icon()
            menuicon.update_tooltip()
            menuicon.update_is_drop_target()
            menuicon.show_all()


   # Methods to be implemented by subclasses

    def quit(self):
        """
        Override this to clean up when the container containing the tray is 
        destroyed.
        """
        pass

    @property
    def icon_ids(self):
        for icons in self.__icons.itervalues():
            for icon_id in icons.iterkeys():
                yield icon_id

    @property
    def icons(self):
        for icons in self.__icons.itervalues():
            for icon in icons.itervalues():
                yield icon

    icon_config = property(lambda self : self.__icon_config)
    tray_config = property(lambda self : self.__tray_config)
    menu_icon = property(lambda self : self.__menu_icon)
