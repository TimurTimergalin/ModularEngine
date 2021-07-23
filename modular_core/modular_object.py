from abc import ABC, abstractmethod
from modular_core.module import FunctionalModule, CosmeticModule
from modular_core.additional_types import BinarySearchList, TreeError
from typing import Union, Optional
from pygame import Surface


class TreeObject(ABC):
    def __init__(self):
        self._parent: Optional[TreeObject] = None
        self._children: list[ModularObject] = BinarySearchList(lambda x: x.z if hasattr(x, 'z') else float('inf'))

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

        super(ModularObject, self).__init__()

        self._functional_modules: list[FunctionalModule] = []

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

    def relative_coordinates(self) -> tuple[Union[int, float], Union[int, float]]:
        return self.x, self.y

    def global_coordinates(self) -> tuple[Union[int, float], Union[int, float]]:
        x, y = self.x, self.y
        parent = self.parent
        while parent is not None:  # if parent is not None, TreeObject is always ModularObject, ignore the warning
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

    @staticmethod
    def is_visual():
        return False

    @staticmethod
    def is_special():
        return False


class SpecialObject(ModularObject):
    @staticmethod
    def is_special():
        return True


class VisualObject(ModularObject):
    def __init__(self):
        super(VisualObject, self).__init__()

        self._z: Union[int, float] = 0

        self._cosmetic_modules: list[CosmeticModule] = []

        self._surface = Surface((0, 0))
        self._camera_shift = 1

    def get_z(self):
        return self._z

    def set_z(self, val):
        if not isinstance(val, (int, float)):
            raise TypeError("coordinates should be real numbers, int or float")
        self._z = val

    z = property(get_z, set_z)

    def render(self) -> Surface:
        res = self.surface
        for child in self.children:
            if not child.is_visual():
                continue
            coords = child.relative_coordinates()
            res.blit(child.render(), coords)  # Render visual objects only, ignore the warning

        for module in self._cosmetic_modules:
            module.run(res)

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

    @staticmethod
    def is_visual():
        return True


class Camera(SpecialObject):
    def __init__(self, name):
        super(Camera, self).__init__()
        self._camera_surface = Surface((0, 0))
        self._camera_cosmetic_modules: list[CosmeticModule] = []

        self._name = name

    @property
    def name(self):
        return self._name

    def relative_center(self):
        x, y = self.relative_coordinates()
        x += self._camera_surface.get_width()
        y += self._camera_surface.get_height()
        return x, y

    def global_center(self):
        x, y = self.global_coordinates()
        x += self._camera_surface.get_width()
        y += self._camera_surface.get_height()
        return x, y

    def _camera_shift_coords(self, child):
        x, y = child.x, child.y
        dx, dy = -self.x * child.camera_shift, -self.y * child.camera_shift
        return x + dx, y + dy

    def crop(self):
        res = self._camera_surface.copy()
        for child in self.root.children:
            if not child.is_visual():
                continue

            surf = child.render()
            res.blit(surf, self._camera_shift_coords(child))  # Render visual objects only, ignore the warning
        for module in self._camera_cosmetic_modules:
            res = module.run(res)

        return res

    @property
    def camera_cosmetic_modules(self) -> list[CosmeticModule]:
        return self._camera_cosmetic_modules.copy()

    def camera_add_cosmetic_module(self, module):
        if not isinstance(module, CosmeticModule):
            raise TypeError("wrong type of added module")

        self._camera_cosmetic_modules.append(module)

    def camera_remove_cosmetic_module(self, module):
        self._camera_cosmetic_modules.remove(module)

    def camera_have_cosmetic_module(self, module) -> bool:
        return module in self._camera_cosmetic_modules

    @staticmethod
    def is_visual():
        return False


class Root(TreeObject):
    @property
    def parent(self):
        return None

    @property
    def root(self):
        return self

    def update(self, events):
        for child in self._children:
            child.update(events)


class Scene(Root):
    def __init__(self):
        super(Scene, self).__init__()

        self._cameras = {}
        self._current_camera: Optional[Camera] = None

    def add_child(self, child):
        super(Scene, self).add_child(child)
        if isinstance(child, Camera):
            if self._cameras.get(child.name) is not None:
                raise TreeError("trying to add existing object to a tree")
            self._cameras[child.name] = child

    def remove_child(self, child):
        super(Scene, self).remove_child(child)
        if isinstance(child, Camera):
            del self._cameras[child.name]

    def render(self):
        return self._current_camera.crop()


class HUD(Root):
    def add_child(self, child):
        if not child.is_visible():
            raise TypeError("HUD can only contain visual objects")
        super(HUD, self).add_child(child)

    def render(self, surf):
        for child in self._children:
            surf.blit(child.render(), child.relative_coordinates())
        return surf


class ControlRoom(Root):
    def add_child(self, child):
        if child.is_visible() or child.is_special():
            raise TypeError("ControlRoom can only contain non-visual not-special objects")
        super(ControlRoom, self).add_child(child)
