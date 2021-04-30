import curses


class Panel:
    def __init__(self, subwindow, height, width, files, title):
        self.subwindow = subwindow
        self.height = height
        self.width = width
        self.files = files
        self.title = title
        self.item_picker = ItemPicker(len(files), height - 2)

    def render(self):
        self.subwindow.box()
        self.subwindow.addstr(0, 2, self.title)
        selected_line = self.item_picker.selected_idx - self.item_picker.current_top
        for idx, file in enumerate(self.files[self.item_picker.current_top:]):
            if idx >= self.height - 2:
                break
            file.render(self.subwindow, idx + 1, 1, idx == selected_line)

    def handle_resize(self, height, width):
        self.item_picker.handle_resize(height - 2)
        self.height = height
        self.width = width

    def scroll_up(self):
        self.item_picker.scroll_up()

    def scroll_down(self):
        self.item_picker.scroll_down()


class File:
    def __init__(self, name, is_dir):
        self.name = name
        self.is_dir = is_dir

    def render(self, window, y, x, highlight):
        if highlight and self.is_dir:
            window.attron(curses.color_pair(1))
            window.attron(curses.A_BOLD)
            window.addstr(y, x, self.name)
            window.attroff(curses.color_pair(1))
            window.attroff(curses.A_BOLD)
        elif highlight and self.name[0] == ".":
            window.attron(curses.color_pair(1))
            window.attron(curses.A_ITALIC)
            window.addstr(y, x, self.name)
            window.attroff(curses.color_pair(1))
            window.attroff(curses.A_ITALIC)
        elif highlight:
            window.attron(curses.color_pair(1))
            window.addstr(y, x, self.name)
            window.attroff(curses.color_pair(1))
        elif self.name[0] == "." and self.is_dir:
            window.attron(curses.A_DIM)
            window.attron(curses.A_BOLD)
            window.addstr(y, x, self.name)
            window.attroff(curses.A_DIM)
            window.attroff(curses.A_BOLD)
        elif self.name[0] == ".":
            window.attron(curses.A_ITALIC)
            window.attron(curses.A_DIM)
            window.addstr(y, x, self.name)
            window.attroff(curses.A_DIM)
            window.attroff(curses.A_ITALIC)
        elif self.is_dir:
            window.attron(curses.color_pair(2))
            window.attron(curses.A_BOLD)
            window.addstr(y, x, self.name)
            window.attroff(curses.color_pair(2))
            window.attroff(curses.A_BOLD)
        else:
            window.addstr(y, x, self.name)


class ItemPicker:
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
