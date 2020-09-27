#!/usr/bin/env python3

from __future__ import annotations

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from widgets.main_win import MainWindow

if __name__ == "__main__":
	main_win = MainWindow()
	main_win.show_all()
	Gtk.main()