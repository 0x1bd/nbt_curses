import sys, os, curses
from node import Node
from nbt_utils import load_nbt
from explorer import Explorer
from render import init_colors, render

CTRL_E, CTRL_A, CTRL_D, CTRL_G, CTRL_X = 5, 1, 4, 7, 24


def main_curses(stdscr, explorer):
    curses.curs_set(0)
    stdscr.keypad(True)
    init_colors()
    while True:
        try:
            render(stdscr, explorer)
            c = stdscr.getch()
            explorer.message = explorer.status = ''
            if c in (CTRL_X, ord('q')):
                break
            elif c in (curses.KEY_DOWN, ord('j')):
                explorer.move(1)
            elif c in (curses.KEY_UP, ord('k')):
                explorer.move(-1)
            elif c in (curses.KEY_NPAGE,):
                explorer.move(1, page=True)
            elif c in (curses.KEY_PPAGE,):
                explorer.move(-1, page=True)
            elif c in (curses.KEY_RIGHT, ord('l'), 10):
                explorer.toggle()
            elif c in (curses.KEY_LEFT, curses.KEY_BACKSPACE, 263, ord('h')):
                explorer.go_parent()
            elif c == CTRL_E:
                explorer.edit_current(stdscr)
            elif c == CTRL_A:
                explorer.add_tag(stdscr)
            elif c == CTRL_D:
                explorer.delete_current()
            elif c == CTRL_G:
                explorer.graph_view(stdscr)
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f'Error: {e}')
            stdscr.addstr(1, 0, 'Press any key to exit')
            stdscr.getch()
            break


def main(argv):
    if len(argv) < 2: print('Usage: python main.py <file.nbt>'); return
    path = argv[1]
    if not os.path.exists(path): print('File not found:', path); return
    try:
        nbt_file, root_name, root = load_nbt(path)
    except Exception as e:
        print('Failed to load NBT:', e); return
    explorer = Explorer(Node(root_name, root), nbt_file, path)
    curses.wrapper(main_curses, explorer)


if __name__ == '__main__':
    main(sys.argv)
