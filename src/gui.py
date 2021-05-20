import curses
import os
from file import File, FilePicker, FileScroller

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


class DebugPanel(BasePanel):
    def __init__(self, subwindow):
        width, height = subwindow.getmaxyx()
        super().__init__(subwindow, height, width, "siema")

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
