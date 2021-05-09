#!/usr/bin/env python
import curses
import os
from gui import Panel, File
from os.path import expanduser
from curses.textpad import Textbox, rectangle


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
    panel_left = Panel(sub, height, width, files, path)
    panel_right = Panel(sub2, height, width, [], "preview:")

    # starting panel
    current_panel = 1

    while True:
        stdscr.erase()

        panel_left.render_filesystem()
        panel_right.render_file()

        # update display
        curses.doupdate()

        # get user input
        key = stdscr.getch()

        # handle user input
        if key == ord("q"):
            break

        # go inside a directory
        if key == ord("o") and current_panel == 1:
            selected = files[panel_left.file_picker.selected_idx]
            new_path = os.path.join(path, selected.name)
            if os.path.isdir(new_path):
                path = new_path
                files = create_files_list(path)
                panel_left = Panel(sub, height, width, files, path)
            # preview a text file
            else:
                try:
                    with open(new_path, "r") as f:
                        f = [File(name.rstrip(), False) for name in f]
                        panel_right = Panel(sub2, height, width, f, os.path.basename(os.path.normpath(new_path)))
                except UnicodeDecodeError:
                    panel_right = Panel(sub2, height, width, [], "selected file is not a text file")

        # go up a directory
        if key == ord("p") and current_panel == 1:
            path = os.path.abspath(os.path.join(path, os.pardir))
            files = create_files_list(path)
            panel_left = Panel(sub, height, width, files, path)

        # move one panel right
        if key == ord("l") and current_panel != 2:
            current_panel = 2

        # move one panel left
        if key == ord("h") and current_panel != 1:
            current_panel = 1
            panel_right = Panel(sub2, height, width, [], "")

        if key == ord("j") and current_panel == 1:
            panel_left.scroll_down()
        elif key == ord("j") and current_panel == 2:
            panel_right.scroll_file_down()

        if key == ord("k") and current_panel == 1:
            panel_left.scroll_up()
        elif key == ord("k") and current_panel == 2:
            panel_right.scroll_file_up()

        if key == ord("/"):
            stdscr.addstr(height-1, 1, "(press Return to send your search query)")

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
            panel_left = Panel(sub, height, width, files, path)

        # handle resize
        if key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()

            # set windows' left upper corner y, x
            sub.mvderwin(0, 0)
            sub2.mvderwin(0, width // 5)

            # set windows' right lower corner y, x
            sub.resize(height, width // 5)
            sub2.resize(height, 4 * width // 5)

            panel_left.handle_resize(height, width)
            panel_right.handle_resize_file(height, width)


if __name__ == "__main__":
    # handle window
    curses.wrapper(main)
