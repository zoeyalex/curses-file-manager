import curses
from curses.textpad import Textbox, rectangle

import os
from os.path import expanduser

# local imports
from panels import BrowserPanel, PreviewPanel
from file import File
from keybinds import *

MIN_WIDTH = 15


def init():
    # disable cursor blink
    curses.curs_set(0)

    # create a color pair FG/BG
    curses.start_color()
    curses.use_default_colors()

    # highlight
    curses.init_pair(1, curses.COLOR_BLACK, 11)

    # directory
    curses.init_pair(2, 5, 0)

    # border
    curses.init_pair(3, 6, 0)


def calculate_dimensions(stdscr):
    height, width = stdscr.getmaxyx()
    return [
        (0, 2 * width // 5, 0, 0),
        (0, 3 * width // 5, 0, 2 * width // 5)
    ]


def application(stdscr):
    init()

    height, width = stdscr.getmaxyx()

    sub, sub2 = [stdscr.subwin(*dim) for dim in calculate_dimensions(stdscr)]

    state = {
        "screen": stdscr,
        "panels": [BrowserPanel(sub, expanduser("~")), PreviewPanel(sub2, None)],
        "active_panel": 0,
    }


    while True:

        stdscr.erase()

        if width >= MIN_WIDTH:
            for panel in state["panels"]:
                panel.render()

        curses.doupdate()

        # get user input (stored as ASCII integer) and refresh screen
        key = stdscr.getch()

        if KEYBINDS.get(key, default)(key, state):
            break

"""
class ApplicationOld:



    def run(self, stdscr):
        self.height, self.width = stdscr.getmaxyx()
        self.files = self.create_files_list(self.path)
        sub1 = sub(stdscr, 0, self.width // 5, 0, 0)
        sub2 = sub(stdscr, 0, 4 * self.width // 5, 0, self.width // 5)

        # disable cursor blink
        curses.curs_set(0)

        # create a color pair FG/BG
        curses.start_color()
        curses.use_default_colors()

        # highlight
        curses.init_pair(1, curses.COLOR_BLACK, 11)

        # directory
        curses.init_pair(2, 5, 0)

        # border
        curses.init_pair(3, 6, 0)

        # create a panel object
        panel_left = BrowserPanel(sub1, self.height, self.width // 5, self.files, self.path)
        panel_right = PreviewPanel(sub2, self.height, 4 * self.width // 5, None)

        # starting panel
        active_panel = panel_left

        while True:
            stdscr.erase()

            if self.width >= MIN_WIDTH:
                panel_left.render()
                panel_right.render()

            # update display
            curses.doupdate()


            # get user input
            key = stdscr.getch()

            # handle user input
            if key is ord("q"):
                break

            if key == ord("o") and active_panel is panel_left:
                selected = self.files[panel_left.file_picker.selected_idx]
                new_path = os.path.join(self.path, selected.name)
                if os.path.isdir(new_path):
                    self.path = new_path
                    self.files = self.create_files_list(self.path)
                    panel_left = BrowserPanel(sub1, self.height, self.width // 5, self.files, self.path)
                # preview a text file
                else:
                    panel_right = PreviewPanel(sub2, self.height, 4 * self.width // 5, new_path)

            # go up a directory
            if key is ord("p") and active_panel is panel_left:
                self.path = os.path.abspath(os.path.join(self.path, os.pardir))
                self.files = self.create_files_list(self.path)
                panel_left = BrowserPanel(sub1, self.height, self.width // 5, self.files, self.path)
                active_panel = panel_left

            # move one panel right
            if key is ord("l"):
                active_panel = panel_right

            # move one panel left
            if key is ord("h"):
                active_panel = panel_left
                panel_right = PreviewPanel(sub2, self.height, 4 * self.width // 5, None)

            if key is ord("j"):
                active_panel.scroll_down()

            if key is ord("k"):
                active_panel.scroll_up()

            if key is ord("/"):
                stdscr.addstr(self.height - 1, 1, "(press Return to send your search query)")

                editwin = curses.newwin(1, self.width // 5 - 4, self.height - 3, 2)
                rectangle(stdscr, self.height - 4, 1, self.height - 2, self.width // 5 - 2)
                stdscr.refresh()
                box = Textbox(editwin)

                # let the user edit until ^G/Return is struck
                box.edit()

                # get resulting contents
                message = str(box.gather()).rstrip()

                # remove all files that do not satisfy the search query
                files = [
                    File(file, False)
                    for file
                    in sorted(os.listdir(self.path))
                    if message in file
                ]
                panel_left = BrowserPanel(sub1, self.height, self.width // 5, files, self.path)

            # handle resize
            if key == curses.KEY_RESIZE:
                self.height, self.width = stdscr.getmaxyx()

                if self.width >= MIN_WIDTH:

                    # set windows' left upper corner y, x
                    try:
                        sub1.mvderwin(0, 0)
                        sub2.mvderwin(0, self.width // 5)
                    except curses.error:
                        pass

                    # set windows' right lower corner y, x
                    sub1.resize(self.height, self.width // 5)
                    sub2.resize(self.height, 4 * self.width // 5)

                panel_left.handle_resize(self.height, self.width // 5)
                panel_right.handle_resize(self.height, 4 * self.width // 5)


def sub(stdscr, nlines, ncols, y, x):
    return stdscr.subwin(nlines, ncols, y, x)
"""
