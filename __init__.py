#!/usr/bin/env python
import curses
import os
from file_manager import Panel, File


def create_files_list(path):
    return [
        File(name, is_dir=os.path.isdir(os.path.join(path, name)))
        for name
        in sorted(os.listdir(path))
    ]

def main(stdscr):
    path = "/"
    files = create_files_list(path)

    # get terminal size
    height, width = stdscr.getmaxyx()

    # create subwindows nlines, ncols, begin_y, begin_x
    sub = stdscr.subwin(0, width//3, 0, 0)
    sub2 = stdscr.subwin(0, 2*width//3, 0, width//3)

    # disable cursor blink
    curses.curs_set(0)

    # create a color pair FG/BG
    curses.start_color()
    curses.use_default_colors()
    # highlight
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    # dir
    curses.init_pair(2, 3, 0)

    # create a panel object
    panel_left = Panel(sub, height, width, files, path)
    panel_right = Panel(sub2, height, width, [], "preview:")

    while True:

        stdscr.erase()

        panel_left.render()
        panel_right.render()

        # update display
        curses.doupdate()

        # get user input
        key = stdscr.getch()

        # handle user input
        if key == ord("q"):
            break

        if key == ord("o"):
            selected = files[panel_left.item_picker.selected_idx]
            new_path = os.path.join(path, selected.name)
            if os.path.isdir(new_path):
                path = new_path
                files = create_files_list(path)
                panel_left = Panel(sub, height, width, files, path)
            else:
                try:

                    with open(new_path, "r") as f:
                        f = [File(name, False) for name in f]
                        panel_right = Panel(sub2, height, width, f, os.path.basename(os.path.normpath(new_path)))
                except:
                    panel_right = Panel(sub2, height, width, [], "selected file is not a text file")


        if key == ord("p"):
            path = os.path.abspath(os.path.join(path, os.pardir))
            files = create_files_list(path)
            panel_left = Panel(sub, height, width, files, path)

        if key == ord("j"):
            panel_left.scroll_down()

        if key == ord("k"):
            panel_left.scroll_up()

        # handle resize
        if key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()

            # move window inside parent y, x
            sub.mvderwin(0, 0)
            sub2.mvderwin(0, width//3)

            # nlines ncols
            sub.resize(height, width//3)
            sub2.resize(height, 2*width//3)

            panel_left.handle_resize(height, width)
            panel_right.handle_resize(height, width)


if __name__ == "__main__":
    # handle window
    curses.wrapper(main)
