from modular_engine.core.modular_object import ModularObject
from modular_engine.core.module import CosmeticModule


class Scene:
    @property
    def parent(self):
        return None

    @property
    def scene(self):
        return self

    @property
    def children(self):
        return self._children.copy()

    def add_child(self, child):
        if not isinstance(child, ModularObject):
            raise TypeError("wrong type of child")
        self._children.append(child)
        child.parent = self

    def remove_child(self, child):
        if not isinstance(child, ModularObject):
            raise TypeError("wrong type of child")
        self._children.remove(child)
        child.parent = None

    def add_cosmetic_module(self, module):
        if not isinstance(module, CosmeticModule):
            raise TypeError("wrong type of added module")

        self._cosmetic_modules.append(module)

    def remove_cosmetic_module(self, module):
        self._cosmetic_modules.remove(module)

    @property
    def cosmetic_modules(self) -> list[CosmeticModule]:
        return self._cosmetic_modules.copy()

    def have_cosmetic_module(self, module) -> bool:
        return module in self._cosmetic_modules
