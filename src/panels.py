import curses
import os
from file import File, FilePicker, FileScroller, create_files_list

class BasePanel:
    def __init__(self, subwindow, title):
        self.height, self.width = subwindow.getmaxyx()
        self.subwindow = subwindow
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

    def handle_key(self, key):
        return self.KEYBINDS[key](self)

    KEYBINDS = {}


class BrowserPanel(BasePanel):
    def __init__(self, subwindow, path):
        super().__init__(subwindow, path)
        self.path = None
        self.files = None
        self.file_picker = None
        self.update_path(path)

    def update_path(self, new_path):
        self.path = new_path
        self.files = create_files_list(self.path)
        self.file_picker = FilePicker(len(self.files), self.height - 2)
        self.title = self.path

    def render(self):
        super().render()
        selected_line = self.file_picker.selected_idx - self.file_picker.current_top
        for idx, file in enumerate(self.files[self.file_picker.current_top:]):
            if idx >= self.height - 2:
                break
            file.render(self.subwindow, idx + 1, 1, idx == selected_line, max(0, self.width - 2), idx)

    def handle_resize(self, height, width):
        super().handle_resize(height, width)
        self.file_picker.handle_resize(height - 2)

    def scroll_up(self):
        self.file_picker.scroll_up()

    def scroll_down(self):
        self.file_picker.scroll_down()

    def go_up_dir(self):
        self.update_path(os.path.abspath(os.path.join(self.path, os.pardir)))

    def go_into_dir(self):
        selected = self.files[self.file_picker.selected_idx]
        new_path = os.path.join(self.path, selected.name)
        if selected.is_dir:
            self.update_path(new_path)
        else:
            return "open_preview", new_path

    KEYBINDS = {
        ord("p"): go_up_dir,
        ord("o"): go_into_dir,
    }


class PreviewPanel(BasePanel):
    def __init__(self, subwindow, path):
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

        super().__init__(subwindow, title)

        self.file_scroller = FileScroller(len(self.lines), self.height - 2)

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
