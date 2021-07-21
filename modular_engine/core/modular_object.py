from abc import ABC, abstractmethod
from modular_engine.core.module import FunctionalModule, CosmeticModule
from modular_engine.core.additional_types import BinarySearchList
from typing import Union, Optional
from pygame import Surface


class TreeObject(ABC):
    def __init__(self):
        self._parent: Optional[TreeObject] = None
        self._children: list[ModularObject] = []

    @property
    @abstractmethod
    def parent(self):
        pass

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

    @property
    @abstractmethod
    def root(self):
        pass


class ModularObject(TreeObject):
    def __init__(self):
        self._x: Union[int, float] = 0
        self._y: Union[int, float] = 0
        self._z: Union[int, float] = 0

        super(ModularObject, self).__init__()

        self._functional_modules: list[FunctionalModule] = BinarySearchList(lambda x: x)

    def get_x(self):
        return self._x

    def set_x(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("coordinates should be real numbers, int or float")
        self._x = val

    x = property(get_x, set_x)

    def get_y(self):
        return self._x

    def set_y(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("coordinates should be real numbers, int or float")
        self._x = val

    y = property(get_x, set_x)

    def get_z(self):
        return self._z

    def set_z(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("coordinates should be real numbers, int or float")
        self._z = val

    z = property(get_z, set_z)

    def relative_coordinates(self) -> tuple[Union[int, float], Union[int, float]]:
        return self.x, self.y

    def global_coordinates(self) -> tuple[Union[int, float], Union[int, float]]:
        x, y = self.x, self.y
        parent = self.parent
        while parent is not None:  # if parent is not None, TreeObject is always ModularObject
            x += self.parent.x
            y += self.parent.y
            parent = parent.parent

        return x, y

    def get_parent(self):
        return self._parent

    def set_parent(self, val):
        if val is not None and not isinstance(val, TreeObject):
            raise TypeError("wrong type of parent")

        self._parent = val

    parent = property(get_parent, set_parent)

    @property
    def root(self):
        parent = self.parent
        while True:
            if parent.parent is None:
                return parent
            parent = parent.parent

    def add_functional_module(self, module):
        if not isinstance(module, FunctionalModule):
            raise TypeError("wrong type of added module")
        self._functional_modules.append(module)
        module.start(self)

    def remove_functional_module(self, module):
        self._functional_modules.remove(module)

    @property
    def functional_modules(self) -> list[FunctionalModule]:
        return self._functional_modules.copy()

    def have_functional_module(self, module) -> bool:
        return module in self._functional_modules

    def update(self, events):
        for child in self._children:
            child.update(events)

        for module in self._functional_modules:
            module.run(self, events)

    def render(self, events) -> Surface:
        return Surface((0, 0))


class Root(TreeObject):
    @property
    def parent(self):
        return None

    @property
    def root(self):
        return self


class Scene(Root):
    pass


class HUD(Root):
    pass


class VisualObject(ModularObject):
    def __init__(self):
        super(VisualObject, self).__init__()
        self._cosmetic_modules: list[CosmeticModule] = BinarySearchList(lambda x: x)

        self._surface = Surface((0, 0))
        self._camera_shift = 1

    def render(self, events) -> Surface:
        res = self.surface
        for child in self.children:
            coords = child.relative_coordinates()
            res.blit(child.render(events), coords)

        for module in self._cosmetic_modules:
            module.run(res, events)

        return res

    @property
    def cosmetic_modules(self) -> list[CosmeticModule]:
        return self._cosmetic_modules.copy()

    def add_cosmetic_module(self, module):
        if not isinstance(module, CosmeticModule):
            raise TypeError("wrong type of added module")

        self._cosmetic_modules.append(module)

    def remove_cosmetic_module(self, module):
        self._cosmetic_modules.remove(module)

    def have_cosmetic_module(self, module) -> bool:
        return module in self._cosmetic_modules

    def get_c(self):
        return self._camera_shift

    def set_c(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("coordinates should be real numbers, int or float")
        if val <= 0:
            raise ValueError("camera shift coefficient must be greater than zero")
        self._camera_shift = val

    camera_shift = property(get_c, set_c)

    def get_surface(self):
        return self._surface.copy()

    def set_surface(self, val):
        if not isinstance(val, Surface):
            raise TypeError("Wrong type, should be pygame.Surface")
        self._surface = val

    surface = property(get_surface, set_surface)

    def rect(self):
        return self._surface.get_rect()


class Camera(ModularObject):
    pass
