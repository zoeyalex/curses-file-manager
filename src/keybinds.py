import curses

def clear_screen(stdscr):
    stdscr.clear()


def quit(stdscr):
    return True


def default(stdscr):
    stdscr.addstr(0, 0, "key not defined")


KEYBINDS = {
    ord("c"): clear_screen,
    ord("q"): quit,
}
