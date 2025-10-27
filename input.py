import curses


def prompt_input(stdscr, prompt):
    curses.curs_set(1)
    h, w = stdscr.getmaxyx()
    win = stdscr.derwin(1, w, h - 2, 0)
    win.clear()
    win.addstr(0, 0, prompt[:w - 1])
    win.refresh()
    curses.echo()
    try:
        s = win.getstr(0, len(prompt), 1024)
        s = s.decode('utf-8') if s else None
    except KeyboardInterrupt:
        s = None
    finally:
        curses.noecho()
        curses.curs_set(0)
    return s
