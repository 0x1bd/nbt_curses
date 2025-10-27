import curses
from collections import Counter


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)  # Compounds
    curses.init_pair(2, curses.COLOR_MAGENTA, -1)  # Lists
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Numbers
    curses.init_pair(4, curses.COLOR_GREEN, -1)  # Strings
    curses.init_pair(5, curses.COLOR_RED, -1)  # Messages/errors


def show_graph(stdscr, counter: Counter):
    curses.curs_set(0)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, 'NBT Tag Type Counts — press any key to return')
    rows = sorted(counter.items(), key=lambda x: x[1], reverse=True)
    if not rows: stdscr.addstr(2, 0, 'No tags'); stdscr.getch(); return
    maxk = max(len(k) for k, _ in rows)
    maxv = max(v for _, v in rows)
    bar_max = max(10, w - maxk - 12)
    for i, (k, v) in enumerate(rows[:h - 3]):
        bar_len = int((v / maxv) * bar_max) if maxv else 0
        stdscr.addstr(2 + i, 0, f"{k.ljust(maxk)} | {'#' * bar_len} {v}")
    stdscr.refresh();
    stdscr.getch()


def render(stdscr, explorer):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, f"nbt_curses — {explorer.path}"[:w - 1], curses.A_BOLD)
    help_line = "Ctrl+E:Edit  Ctrl+A:Add  Ctrl+D:Delete  Ctrl+G:Graph  Ctrl+X:Quit"
    try:
        stdscr.addstr(h - 1, 0, help_line[:w - 1], curses.A_REVERSE)
    except:
        pass
    try:
        msg = explorer.message or explorer.status
        stdscr.addstr(h - 2, 0, msg[:w - 1], curses.color_pair(5))
    except:
        pass

    explorer.build_visible()
    win_h = h - 4
    for row in range(win_h):
        idx = explorer.offset + row
        if idx >= len(explorer.visible): break
        node, depth = explorer.visible[idx]
        prefix = '  ' * depth
        marker = '+' if (not node.is_primitive() and not node.expanded) else '-' if (
                    not node.is_primitive() and node.expanded) else ' '
        preview = str(node.value)[
            :40] if node.is_primitive() else f"Compound[{len(node.value)}]" if node.is_compound() else f"List[{len(node.value)}]"
        line = f"{prefix}{marker} {node.name}: {preview}"

        color = 0
        if node.is_compound():
            color = curses.color_pair(1)
        elif node.is_list():
            color = curses.color_pair(2)
        elif isinstance(node.value, (int, float)):
            color = curses.color_pair(3)
        elif isinstance(node.value, str):
            color = curses.color_pair(4)

        attr = color | curses.A_REVERSE if idx == explorer.cursor else color
        try:
            stdscr.addstr(2 + row, 0, line[:w - 1], attr)
        except:
            pass
    stdscr.refresh()
