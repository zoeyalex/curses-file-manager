import curses
import os


class BasePanel:
    def __init__(self, subwindow, height, width, title):
        self.subwindow = subwindow
        self.height = height
        self.width = width
        self.title = title

    def render(self):
        self.subwindow.attron(curses.color_pair(3))
        self.subwindow.box()
        self.subwindow.attroff(curses.color_pair(3))
        self.subwindow.addnstr(0, 2, self.title, max(0, self.width - 4))

    def handle_resize(self, height, width):
        self.height = height
        self.width = width

    def scroll_up(self):
        pass

    def scroll_down(self):
        pass


class BrowserPanel(BasePanel):
    def __init__(self, subwindow, height, width, files, title):
        super().__init__(subwindow, height, width, title)
        self.files = files
        self.file_picker = FilePicker(len(files), height - 2)

    def render(self):
        super().render()
        selected_line = self.file_picker.selected_idx - self.file_picker.current_top
        for idx, file in enumerate(self.files[self.file_picker.current_top:]):
            if idx >= self.height - 2:
                break
            file.render(self.subwindow, idx + 1, 1, idx == selected_line, max(0, self.width - 2))

    def handle_resize(self, height, width):
        super().handle_resize(height, width)
        self.file_picker.handle_resize(height - 2)

    def scroll_up(self):
        self.file_picker.scroll_up()

    def scroll_down(self):
        self.file_picker.scroll_down()


class PreviewPanel(BasePanel):
    def __init__(self, subwindow, height, width, path):
        if path is None:
            self.lines = []
            title = "preview: "
        else:
            try:
                with open(path, "r") as file:
                    self.lines = [name.rstrip() for name in file]
                    title = os.path.basename(os.path.normpath(path))
            except UnicodeDecodeError:
                self.lines = []
                title = "selected file is not a text file"

        super().__init__(subwindow, height, width, title)

        self.file_scroller = FileScroller(len(self.lines), height - 2)

    def render(self):
        super().render()
        for line_num, line in enumerate(self.lines[self.file_scroller.current_top:]):
            if line_num >= self.height - 2:
                break
            self.subwindow.addnstr(line_num + 1, 1, line, max(0, self.width - 2))

    def handle_resize(self, height, width):
        super().handle_resize(height, width)
        self.file_scroller.handle_resize(height - 2)

    def scroll_up(self):
        self.file_scroller.scroll_up()

    def scroll_down(self):
        self.file_scroller.scroll_down()


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
