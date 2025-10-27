from typing import Optional
import nbtlib


class Node:
    def __init__(self, name: str, value, parent: Optional['Node'] = None):
        self.name = name
        self.value = value
        self.parent = parent
        self.children = None
        self.expanded = False

    def is_compound(self):
        return isinstance(self.value, (nbtlib.tag.Compound, dict))

    def is_list(self):
        return isinstance(self.value, (nbtlib.tag.List, list))

    def is_primitive(self):
        return not (self.is_compound() or self.is_list())

    def make_children(self):
        if self.children is not None:
            return
        self.children = []
        v = self.value
        if self.is_compound():
            for k, vv in v.items():
                self.children.append(Node(k, vv, parent=self))
        elif self.is_list():
            for i, vv in enumerate(v):
                self.children.append(Node(f"[{i}]", vv, parent=self))
        else:
            self.children = []
