#!/usr/bin/env python
import curses
import os
from gui import BrowserPanel, PreviewPanel, File
from os.path import expanduser
from curses.textpad import Textbox, rectangle


MIN_WIDTH = 15


def create_files_list(path):
    return [
        File(name, is_dir=os.path.isdir(os.path.join(path, name)))
        for name
        in sorted(os.listdir(path))
    ]


def main(stdscr):
    # set starting path and create a list of sorted File objects containing current directory's filenames
    path = expanduser("~")
    files = create_files_list(path)

    # get terminal size
    height, width = stdscr.getmaxyx()

    # create subwindows nlines, ncols, begin_y, begin_x
    sub = stdscr.subwin(0, width // 5, 0, 0)
    sub2 = stdscr.subwin(0, 4 * width // 5, 0, width // 5)

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
    panel_left = BrowserPanel(sub, height, width // 5, files, path)
    panel_right = PreviewPanel(sub2, height, 4 * width // 5, None)

    # starting panel
    active_panel = panel_left

    while True:
        stdscr.erase()

        if width >= MIN_WIDTH:
            panel_left.render()
            panel_right.render()

        # update display
        curses.doupdate()

        # get user input
        key = stdscr.getch()

        # handle user input
        if key == ord("q"):
            break

        # go inside a directory
        if key == ord("o") and active_panel is panel_left:
            selected = files[panel_left.file_picker.selected_idx]
            new_path = os.path.join(path, selected.name)
            if os.path.isdir(new_path):
                path = new_path
                files = create_files_list(path)
                panel_left = BrowserPanel(sub, height, width // 5, files, path)
            # preview a text file
            else:
                panel_right = PreviewPanel(sub2, height, 4 * width // 5, new_path)

        # go up a directory
        if key == ord("p") and active_panel is panel_left:
            path = os.path.abspath(os.path.join(path, os.pardir))
            files = create_files_list(path)
            panel_left = BrowserPanel(sub, height, width // 5, files, path)

        # move one panel right
        if key == ord("l"):
            active_panel = panel_right

        # move one panel left
        if key == ord("h"):
            active_panel = panel_left
            panel_right = PreviewPanel(sub2, height, 4 * width // 5, None)

        if key == ord("j"):
            active_panel.scroll_down()

        if key == ord("k"):
            active_panel.scroll_up()

        if key == ord("/"):
            stdscr.addstr(height - 1, 1, "(press Return to send your search query)")

            editwin = curses.newwin(1, width // 5 - 4, height - 3, 2)
            rectangle(stdscr, height - 4, 1, height - 2, width // 5 - 2)
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
                in sorted(os.listdir(path))
                if message in file
            ]
            panel_left = BrowserPanel(sub, height, width // 5, files, path)

        # handle resize
        if key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()

            if width >= MIN_WIDTH:

                # set windows' left upper corner y, x
                try:
                    sub.mvderwin(0, 0)
                    sub2.mvderwin(0, width // 5)
                except curses.error:
                    pass

                # set windows' right lower corner y, x
                sub.resize(height, width // 5)
                sub2.resize(height, 4 * width // 5)

            panel_left.handle_resize(height, width // 5)
            panel_right.handle_resize(height, 4 * width // 5)


if __name__ == "__main__":
    # handle window
    curses.wrapper(main)
