import curses
import os


class Panel:
    def __init__(self, subwindow, height, width, items, name):
        self.subwindow = subwindow
        self.height = height
        self.width = width
        self.items = items
        self.name = name
        self.item_picker = ItemPicker(len(items), height - 2)

    def render(self):
        self.subwindow.box()
        self.subwindow.addstr(0, 2, self.name)
        selected_line = self.item_picker.selected_idx - self.item_picker.current_top
        for idx, item in enumerate(self.items[self.item_picker.current_top:], 0):
            if idx >= self.height - 2:
                break
            if os.path.isdir(os.path.join(self.name, self.items[idx])):
                self.subwindow.attron(curses.color_pair(2))
                self.subwindow.addstr(idx+1, 1, item)
                self.subwindow.attroff(curses.color_pair(2))
            else:
                self.subwindow.addstr(idx+1, 1, item)
            if idx == selected_line:
                self.subwindow.attron(curses.color_pair(1))
                self.subwindow.addstr(idx+1, 1, item)
                self.subwindow.attroff(curses.color_pair(1))

    def handle_resize(self, height, width):
        self.item_picker.handle_resize(height - 2)
        self.height = height
        self.width = width

    def scroll_up(self):
        self.item_picker.scroll_up()

    def scroll_down(self):
        self.item_picker.scroll_down()


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
