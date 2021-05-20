#!/usr/bin/env python
import curses

# local import
from app import application


if __name__ == "__main__":
    # handle window
    curses.wrapper(application)
