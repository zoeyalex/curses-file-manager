import curses
import os


class File:
    def __init__(self, name, is_dir ):
        self.name = name
        self.is_dir = is_dir

    def render(self, window, y, x, highlight, max_width):
        if highlight and self.is_dir:
            window.attron(curses.color_pair(1))
            window.attron(curses.A_BOLD)
            window.addnstr(y, x, self.name, max_width)
            window.attroff(curses.color_pair(1))
            window.attroff(curses.A_BOLD)
        elif highlight:
            window.attron(curses.color_pair(1))
            window.addnstr(y, x, self.name, max_width)
            window.attroff(curses.color_pair(1))
        elif self.is_dir:
            window.attron(curses.color_pair(2))
            window.attron(curses.A_BOLD)
            window.addnstr(y, x, self.name, max_width)
            window.attroff(curses.color_pair(2))
            window.attroff(curses.A_BOLD)
        else:
            window.addnstr(y, x, self.name, max_width)


class FilePicker:
    def __init__(self, count, size):
        self.count = count
        self.selected_idx = 0
        self.current_top = 0
        self.size = size

    def scroll_up(self):
        if self.selected_idx > 0:
            self.selected_idx -= 1
            if self.selected_idx < self.current_top:
                self.current_top = self.selected_idx

    def scroll_down(self):
        if self.selected_idx < self.count - 1:
            self.selected_idx += 1
            if self.selected_idx >= self.size + self.current_top:
                self.current_top = self.selected_idx - self.size + 1

    def handle_resize(self, new_size):
        if self.size == new_size:
            return
        if new_size > self.size:
            if self.current_top != 0:
                self.current_top = max(
                    self.current_top - (new_size - self.size),
                    0
                )
        else:
            if (self.selected_idx - self.current_top) >= new_size:
                self.current_top += self.selected_idx - self.current_top - new_size + 1
        self.size = new_size


class FileScroller:
    def __init__(self, count, size):
        self.count = count
        self.size = size
        self.current_top = 0

    def scroll_up(self):
        if self.current_top > 0:
            self.current_top -= 1

    def scroll_down(self):
        if self.current_top < self.count - self.size:
            self.current_top += 1

    def handle_resize(self, new_size):
        if self.size == new_size:
            return
        if new_size > self.size:
            if self.current_top != 0:
                self.current_top = max(
                    self.current_top - (new_size - self.size),
                    0
                )
        else:
            if (self.count - self.current_top) >= new_size:
                self.current_top += self.count - self.current_top - new_size + 1
        self.size = new_size


def create_files_list( path):
    return [
        File(name, is_dir=os.path.isdir(os.path.join(path, name)))
        for name
        in sorted(os.listdir(path))
    ]
