from panels import PreviewPanel

def quit(key, state):
    return True


def scroll_down(key, state):
    state["panels"][state["active_panel"]].scroll_down()


def scroll_up(key, state):
    state["panels"][state["active_panel"]].scroll_up()


def go_panel_left(key, state):
    state["active_panel"] = 0


def go_panel_right(key, state):
    state["active_panel"] = 1


def default(key, state):
    result = state["panels"][state["active_panel"]].handle_key(key)
    if result is not None:
        action, *args = result
        if action == "open_preview":
            path, = args
            subwindow = state["panels"][1].subwindow
            state["panels"][1] = PreviewPanel(subwindow, path)



KEYBINDS = {
    ord("q"): quit,
    ord("j"): scroll_down,
    ord("k"): scroll_up,
    ord("h"): go_panel_left,
    ord("l"): go_panel_right,
}
