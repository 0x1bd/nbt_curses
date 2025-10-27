import curses
from collections import Counter
from node import Node
from nbt_utils import save_nbt_file, coerce_to_tag, build_tag_from_inputs
from input import prompt_input
from render import show_graph


class Explorer:
    def __init__(self, root: Node, nbt_file, path: str):
        self.root = root
        self.nbt_file = nbt_file
        self.path = path
        self.visible = []
        self.cursor = 0
        self.offset = 0
        self.message = ''
        self.status = ''
        self.build_visible()

    def build_visible(self):
        self.visible = []

        def walk(node, depth=0):
            self.visible.append((node, depth))
            if node.expanded:
                node.make_children()
                for c in node.children:
                    walk(c, depth + 1)

        walk(self.root, 0)
        self.cursor = max(0, min(self.cursor, len(self.visible) - 1))

    def current(self):
        if not self.visible: return None
        return self.visible[self.cursor][0]

    def move(self, delta: int, page=False):
        h, w = curses.initscr().getmaxyx()
        win_h = max(3, h - 4)
        if page: delta *= win_h
        self.cursor = max(0, min(self.cursor + delta, len(self.visible) - 1))
        half = win_h // 2
        self.offset = max(0, self.cursor - half)
        if self.offset + win_h > len(self.visible):
            self.offset = max(0, len(self.visible) - win_h)

    def toggle(self):
        node = self.current()
        if not node or node.is_primitive(): return
        node.expanded = not node.expanded
        if node.expanded: node.make_children()
        self.build_visible()

    def go_parent(self):
        node = self.current()
        if node and node.parent:
            parent = node.parent
            for i, (n, d) in enumerate(self.visible):
                if n is parent: self.cursor = i; break
            self.build_visible()

    def set_message(self, msg: str):
        self.message = msg

    def edit_current(self, stdscr):
        node = self.current()
        if not node or not node.is_primitive(): self.set_message('Not a primitive'); return
        new = prompt_input(stdscr, f"Edit {node.name} (current={repr(node.value)}): ")
        if new is None: self.set_message('Edit canceled'); return
        parent = node.parent
        try:
            new_tag = coerce_to_tag(node.value, new)
            if parent is None:
                node.value = new_tag
            else:
                if parent.is_compound():
                    parent.value[node.name] = new_tag
                else:
                    parent.value[int(node.name.strip('[]'))] = new_tag
            save_nbt_file(self.nbt_file, self.path)
            if parent: parent.children = None
            node.children = None
            self.build_visible()
            self.set_message('Edited and autosaved')
        except Exception as e:
            self.set_message(f'Edit failed: {e}')

    def add_tag(self, stdscr):
        node = self.current()
        if not node or not (node.is_compound() or node.is_list()): self.set_message(
            'Add only allowed in Compound/List'); return
        name = prompt_input(stdscr, 'New tag name: ') if node.is_compound() else ''
        typ = prompt_input(stdscr,
                           'Type (byte/short/int/long/float/double/string/compound/list/bytearray/intarray/longarray): ')
        if not typ: self.set_message('Add canceled'); return
        val = None
        if typ.lower() in ('byte', 'short', 'int', 'long', 'float', 'double', 'string', 'bytearray', 'intarray',
                           'longarray'):
            val = prompt_input(stdscr, 'Value: ')
        try:
            newtag = build_tag_from_inputs(typ.lower(), val)
            if node.is_compound():
                node.value[name] = newtag
            else:
                node.value.append(newtag)
            node.children = None
            save_nbt_file(self.nbt_file, self.path)
            self.build_visible()
            self.set_message('Added and autosaved')
        except Exception as e:
            self.set_message(f'Add failed: {e}')

    def delete_current(self):
        node = self.current()
        if not node or not node.parent: self.set_message('Cannot delete root'); return
        parent = node.parent
        try:
            if parent.is_compound():
                del parent.value[node.name]
            else:
                parent.value.pop(int(node.name.strip('[]')))
            parent.children = None
            save_nbt_file(self.nbt_file, self.path)
            self.build_visible()
            self.set_message('Deleted and autosaved')
        except Exception as e:
            self.set_message(f'Delete failed: {e}')

    def graph_view(self, stdscr):
        counter = Counter()

        def walk(n):
            counter[type(n.value).__name__] += 1
            if not n.is_primitive(): n.make_children(); [walk(c) for c in n.children]

        walk(self.root)
        show_graph(stdscr, counter)
