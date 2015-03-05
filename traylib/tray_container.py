from traylib import *
from traylib.tray import Tray, TrayConfig 
from traylib.icon import IconConfig


class TrayContainer(object):
    """
    An object containing a L{Tray}. If you subclass this, you must also subclass
    C{gtk.Container}.
    """
    
    def __init__(self, min_size, max_size, vertical, tray_class, icon_config, 
                tray_config, *tray_args):
        """
        Creates a new C{TrayContainer}.
        
        @param min_size: The minimum size of the icons.
        @param max_size: The maximum size of the icons.
        @param vertical: C{True} if the tray should be vertical.
        @param tray_class: The class of the tray to be created. Must be a 
            subclass of L{Tray}.
        @param icon_config: The L{IconConfig}.
        @param tray_config: The L{TrayConfig}.
        @param *tray_args: Additional arguments passed to the C{tray_class}'s 
            constructor.
        """
        self.__tray = None
        self.__tray_class = tray_class
        self.__tray_args = tray_args
        self.__icon_config = icon_config
        self.__tray_config = tray_config
        self.__size = 0
        self.__max_size = max_size
        self.__min_size = min_size
        self.__vertical = vertical
        self.set_name(tray_config.name)
        self.connect('size-allocate', self.__size_allocate)

    def __size_allocate(self, widget, rectangle):
        if self.__vertical:
            size = rectangle[2]
        else:
            size = rectangle[3]
        if size == self.__size:
            return
        self.__size = size
        self.update_icon_size(self.__min_size, self.__max_size)
        if not self.__tray:
            self.__tray = self.__tray_class(self.__icon_config, 
                                            self.__tray_config,
                                            *self.__tray_args)
            self.__tray.set_container(self)

    def update_icon_size(self, min_size, max_size):
        """
        Updates the size of the tray's icons and sets the maximum icon size.
        
        @param min_size: The minimum icon size.
        @param max_size: The maximum icon size.
        """
        self.__max_size = max_size
        self.__min_size = min_size
        size = self.get_icon_size()
        self.__icon_config.size = max(min_size, min(size, max_size))

    def get_icon_size(self):
        """
        Extend this to determine the maximum icon size.
        
        @return: The maximum icon size.
        """
        return self.__size
    
    icon_config = property(lambda self : self.__icon_config)
    is_vertical = property(lambda self : self.__vertical)
    tray_config = property(lambda self : self.__tray_config)
    tray = property(lambda self : self.__tray)
