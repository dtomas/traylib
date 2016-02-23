import gtk
import gobject

from traylib import ICON_THEME


class Item(gobject.GObject):

    def __init__(self):
        gobject.GObject.__init__(self)
        self.__icon_theme_changed_handler = ICON_THEME.connect(
            "changed", self.__theme_changed
        )

    def destroy(self):
        ICON_THEME.disconnect(self.__icon_theme_changed_handler)
        self.emit("destroyed")

    def __theme_changed(self, icon_theme):
        self.emit("icon-changed")

    def is_visible(self):
        """
        Override this to determine the visibility.
        
        @return: C{True} if the C{Item} should be visible.
        """
        return True

    def is_blinking(self):
        return False

    def get_name(self):
        """
        Override this to determine the name.
        
        @return: The new name.
        """
        return ""

    def get_icon(self, size):
        """
        This determines the C{gtk.gdk.Pixbuf} the C{Item} should have.
        By default, this method tries to load the pixbuf from the path
        returned by L{get_icon_path()}. If this fails, it looks up the icon 
        in the current icon theme from the icon names returned by 
        L{get_icon_names()}. If this also fails, it returns the pixbuf
        returned by L{get_icon_pixbuf()}.
        
        @return: The new pixbuf.
        """
        icon_path = self.get_icon_path()
        if icon_path:
            try:
                return gtk.gdk.pixbuf_new_from_file(icon_path)
            except:
                pass
        for icon_name in self.get_icon_names():
            icon_info = ICON_THEME.lookup_icon(icon_name, size, 0)
            if not icon_info:
                continue
            icon_path = icon_info.get_filename()
            try:
                pixbuf = gtk.gdk.pixbuf_new_from_file(icon_path)
            except:
                continue
            return pixbuf
        return self.get_icon_pixbuf()

    def get_icon_names(self):
        """
        Override this to determine the icon's icon names. These will only be 
        used if L{get_icon_path} doesn't return a path to an icon or the icon
        could not be loaded.

        @return: The icon names.
        """
        return []

    def get_icon_pixbuf(self):
        """
        Override this to determine the pixbuf to be used for the icon. This
        will only be used if no icons could be found for the icon names
        returned by L{get_icon_names()} and L{get_icon_path()} doesn't return
        a path to an icon.
        """
        return None

    def get_icon_path(self):
        """
        Override this to determine the path to a file from which the pixbuf 
        will be loaded.
        """
        return None

    def get_emblem(self):
        """
        Override this to determine the emblem to be shown in the upper left 
        corner.
        
        @return: The new emblem.
        """
        return None

    def get_zoom(self):
        """
        Extend this to determine the zoom factor.
        
        @return: The new zoom factor.
        """
        return 1.0

    def has_arrow(self):
        """
        Override this to determine whether the C{Icon} has an arrow or not.
        
        @return: C{True} if the C{Icon} should have an arrow.
        """
        return False

    def get_menu_left(self):
        """
        Override this to determine the menu that pops up when left-clicking the
        C{Icon}. (In case the C{click()} method returned C{False}.)

        @return: The menu that pops up when left-clicking the C{Icon}.
        """
        return None

    def get_menu_right(self):
        """
        Override this to determine the menu that pops up when right-clicking
        the C{Icon}.

        @return: The menu that pops up when right-clicking the C{Icon}.
        """
        return None

    def mouse_wheel_up(self, time=0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        up.
        
        @param time: The time of the scroll event.
        """
        return False

    def mouse_wheel_down(self, time=0L):
        """
        Override this to determine the action when the mouse wheel is scrolled 
        down.
        
        @param time: The time of the scroll event.
        """
        return False

    def spring_open(self, time=0L):
        """
        Override this to determine the action when the mouse pointer stays on
        an icon some time while dragging.
        
        @return: C{True} if C{spring_open()} should be called again in a
            second. 
        """
        return False

    def click(self, time=0L):
        """
        Override this to determine the action when left-clicking the C{Icon}. 
        If an action was performed, return C{True}, else return C{False}.
        
        @param time: The time of the click event.
        """
        return False

    def uris_dropped(self, uri_list, action):
        """
        Override this to react to URIs being dropped on the C{Icon}.
        
        @param uris: A list of URIs.
        @param action: One of C{gtk.gdk.ACTION_COPY}, C{gtk.gdk.ACTION_MOVE}
            or C{gtk.gdk.ACTION_LINK}.
        """
        pass

    def get_drag_source_targets(self):
        return []

    def get_drag_source_actions(self):
        return 0

    def drag_data_get(self, context, data, info, time):
        pass


gobject.type_register(Item)
gobject.signal_new(
    "is-visible-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "is-blinking-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    ()
)
gobject.signal_new(
    "name-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "icon-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "zoom-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "has-arrow-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "menu-left-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "menu-right-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)
gobject.signal_new(
    "drag-source-changed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
    ()
)
gobject.signal_new(
    "destroyed", Item, gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()
)


class ItemWrapper(Item):

    def __init__(self, item):
        Item.__init__(self)
        self.__item = item

        self.__item_handlers = [
            item.connect("is-visible-changed", self.__is_visible_changed),
            item.connect("is-blinking-changed", self.__is_blinking_changed),
            item.connect("name-changed", self.__name_changed),
            item.connect("icon-changed", self.__icon_changed),
            item.connect("zoom-changed", self.__zoom_changed),
            item.connect("has-arrow-changed", self.__has_arrow_changed),
            item.connect("menu-left-changed", self.__menu_left_changed),
            item.connect("menu-right-changed", self.__menu_right_changed),
            item.connect("drag-source-changed", self.__drag_source_changed),
        ]

    def destroy(self):
        self.__item.destroy()
        Item.destroy(self)

    def __is_visible_changed(self, item):
        self.emit("is-visible-changed")

    def __is_blinking_changed(self, item):
        self.emit("is-blinking-changed")

    def __name_changed(self, item):
        self.emit("name-changed")

    def __icon_changed(self, item):
        self.emit("icon-changed")

    def __zoom_changed(self, item):
        self.emit("zoom-changed")

    def __has_arrow_changed(self, item):
        self.emit("has-arrow-changed")

    def __menu_left_changed(self, item):
        self.emit("menu-left-changed")

    def __menu_right_changed(self, item):
        self.emit("menu-right-changed")

    def __drag_source_changed(self, item):
        self.emit("drag-source-changed")

    def is_visible(self):
        return self.__item.is_visible()

    def is_blinking(self):
        return self.__item.is_blinking()

    def get_name(self):
        return self.__item.get_name()

    def get_icon_names(self):
        return self.__item.get_icon_names()

    def get_icon_pixbuf(self):
        return self.__item.get_icon_pixbuf()

    def get_icon_path(self):
        return self.__item.get_icon_path()

    def get_emblem(self):
        return self.__item.get_emblem()

    def get_zoom(self):
        return self.__item.get_zoom()

    def has_arrow(self):
        return self.__item.has_arrow()

    def get_menu_left(self):
        return self.__item.get_menu_left()

    def get_menu_right(self):
        return self.__item.get_menu_right()

    def mouse_wheel_up(self, time=0L):
        return self.__item.mouse_wheel_up(time)

    def mouse_wheel_down(self, time=0L):
        return self.__item.mouse_wheel_down(time)

    def spring_open(self, time=0L):
        return self.__item.spring_open(time)

    def click(self, time=0L):
        return self.__item.click(time)

    def uris_dropped(self, uri_list, action):
        self.__item.uris_dropped(uri_list, action)

    def get_drag_source_targets(self):
        return self.__item.get_drag_source_targets()

    def get_drag_source_actions(self):
        return self.__item.get_drag_source_actions()

    def drag_data_get(self, context, data, info, time):
        self.__item.drag_data_get(context, data, info, time)

    @property
    def item(self):
        return self.__item