"""
Добавляем обработку клавиш и вращение камеры

Задание: поменять тип вращения камеры (при перемещении мыши [без нажатий] плавно перемещать камеру с инерцией)
Задание: по клавишам переключаться между текстурой и цветом, менять фильтры текстуры и прочее
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

try:
    import PIL.Image as Image
except ImportError as err:
    import Image

import numpy
import math


class CameraOrbit(object):
    """Камера для вращения по сфере вокруг центра модели|сцены"""

    def __init__(self, w, h, radius_min=4, radius_max=20, move_button=1, speed=0.01):
        self.w = w
        self.h = h
        self.radius_min = radius_min
        self.radius_max = radius_max
        self.move_button = move_button  # по умолчанию используем правую клавишу мыши
        self.speed = speed  # фактор скорости изменения
        self.mouse_states = {self.move_button: 0}  # состояние нажатия клавиши
        self.mouse_coords = {self.move_button: (0, 0)}  # координаты нажатия клавиши мыши
        self.data = {}

    def init(self, pos=(0, 0, -5), target=(0, 0, 0), fov=45, near=0.1, far=50.0, forwards=(0, 0, 1), up=(0, 1, 0)):
        """Задаем все необходимые начальные параметры камеры"""
        self.data['pos'] = list(pos)
        self.data['forwards'] = forwards
        self.data['target'] = target
        self.data['up'] = up
        self.data['fov'] = fov
        self.data['start'] = near
        self.data['end'] = far
        self.data['r'] = math.sqrt(numpy.dot(pos, pos))
        self.data['theta'] = math.acos(pos[2] / self.data['r'])
        if pos[0] != 0:
            self.data['phi'] = math.atan(pos[1] / pos[0])
        else:
            self.data['phi'] = 0

    def update(self):
        """Обновляем положение камеры"""
        self.data['pos'][0] = self.data['r'] * math.sin(self.data['theta']) * math.cos(self.data['phi'])
        self.data['pos'][1] = self.data['r'] * math.sin(self.data['theta']) * math.sin(self.data['phi'])
        self.data['pos'][2] = self.data['r'] * math.cos(self.data['theta'])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.data['fov'], self.w / self.h, self.data['start'], self.data['end'])
        gluLookAt(self.data['pos'][0], self.data['pos'][1], self.data['pos'][2], 0, 0, 0, 0, 0, 1)

    def event(self, e):
        """Обрабатываем нажатия клавиш мыши"""
        if (e.type == MOUSEBUTTONDOWN and e.button == 1):
            # если нажали на левую клавишу мыши, то запоминаем координаты и состояние нажатия
            self.mouse_coords[e.button] = e.pos
            self.mouse_states[e.button] = 1
        elif (e.type == MOUSEBUTTONUP and e.button == 1):
            # если отпустили левую клавишу мыши, то сбрасываем координаты и состояние
            self.mouse_coords[e.button] = (0, 0)
            self.mouse_states[e.button] = 0
        elif (e.type == MOUSEMOTION and self.mouse_states[1]):
            # при движение мыши и при зажатой левой кнопке мыши вращаем камеру
            self.mouse_move(*e.pos)

    def mouse_move(self, x, y):
        """Меняем параметры камеры в зависимости от положения мыши"""
        # считываем модификаторы, например ctrl
        mod = pygame.key.get_mods()
        # вычисляем сдвих между текущими координатми и теми что были при нажатии
        dx = self.mouse_coords[self.move_button][0] - x
        dy = self.mouse_coords[self.move_button][1] - y
        # обновляем координаты
        self.mouse_coords[self.move_button] = (x, y)
        # если зажат CRTL, то меняем радиус (приближаем/удаляем)
        if mod & KMOD_LCTRL:
            self.data['r'] += self.speed * dy
            if self.data['r'] < self.radius_min:
                self.data['r'] = self.radius_min
            if self.data['r'] > self.radius_max:
                self.data['r'] = self.radius_max
        else:
            # иначе меняем углы
            self.data['phi'] += self.speed * dx
            self.data['theta'] += self.speed * dy
            if self.data['theta'] > math.pi:
                self.data['theta'] = math.pi
            if self.data['theta'] <= 0:
                self.data['theta'] = 1e-5


class Camera(object):
    """Класс для управления камерой

    Пока просто выставляется перспектива.
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def init(self, pos=(0.0, 0.0, -5), fov=45, near=0.1, far=50.0):
        """Выставляет перспективу и положение камеры в соответствии с параметрами"""
        gluPerspective(fov, (self.w / self.h), near, far)
        glTranslatef(*pos)


class TextureHelper(object):

    @staticmethod
    def load(filename):
        """Загрузка текстуры для использщвания в OpenGL"""

        # открываем файл и преобразуем в массив байт
        img = Image.open(filename)
        img_data = numpy.array(list(img.getdata()), numpy.uint8)

        # создаем текстуру (id)
        texture_id = glGenTextures(1)
        # выравниваем, как считывать данные текстуры, в нашем случае побайтово
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        # устанавливаем текущую текстуру
        glBindTexture(GL_TEXTURE_2D, texture_id)

        # Устанавливаем параметры текстуры (можно поэкспериментировать)

        # Как тестура будет повторятся (см доку)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        # Устанавливаем фильтры для текстуры
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        # записываем данные текстуры в OpenGL память (GPU)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        # сбрасываем текстуру
        glBindTexture(GL_TEXTURE_2D, 0)
        return texture_id

    @staticmethod
    def render(texture_id):
        """Устанавливает текстуру для отображения"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)


class Cube(object):
    """Класс для создание и отрисовки куба"""
    def __init__(self):
        """Заполняем массивы вершин и полигонов"""
        self.verticies = (
            (1, -1, -1),   # 0
            (1, 1, -1),    # 1
            (-1, 1, -1),   # 2
            (-1, -1, -1),  # 3
            (1, -1, 1),    # 4
            (1, 1, 1),     # 5
            (-1, -1, 1),   # 6
            (-1, 1, 1)     # 7
        )
        self.faces = (
            (1, 2, 7, 5),
            (4, 6, 3, 0),
            (5, 7, 6, 4),
            (0, 3, 2, 1),
            (7, 2, 3, 6),
            (1, 5, 4, 0)
        )
        self.colors = (
            (0.0, 1.0, 0.0),
            (1.0, 0.5, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 0.0, 1.0),
        )
        # добавляем текстурные координаты
        self.uvs = (
            ((0, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1), (0, 1)),
            ((0, 0), (1, 0), (1, 1), (0, 1))
        )
        self.texture_id = TextureHelper.load('wall.jpg')
        self.enable_rotation = True

    def render(self):
        """Рисуем куб в виде полигонов, добавляем текстуру"""
        TextureHelper.render(self.texture_id)
        glMatrixMode(GL_MODELVIEW)
        if self.enable_rotation:
            glRotatef(1, 3, 1, 1)
        glBegin(GL_QUADS)
        for fi, faces in enumerate(self.faces):
            # убираем цвет, можно включить, тогда будет наложение
            # glColor3fv(self.colors[fi])
            for vi, vertex in enumerate(faces):
                glTexCoord2fv(self.uvs[fi][vi])
                glVertex3fv(self.verticies[vertex])
        glEnd()

    def event(self, e):
        # добавляем обработку клавиши пробел
        if (e.type == KEYUP and e.key == 32):  # Space
            self.enable_rotation = not self.enable_rotation


class Controller(object):
    """Основной класс для создания окна и запуска цикла рендеринга"""

    def __init__(self, w=800, h=600, name="Lab", frame_rate=60):
        """Конструктор нашего класса

        Принимает параметры размера окна, название окна и ограничение количества кадров в секунду
        """
        self.w = w
        self.h = h
        self.name = name
        self.frame_rate = frame_rate
        self.screen = None  # ссылка на созданное окно
        self.clock = None  # вспомогательный объект для контроля FPS
        self.cube = None
        self.camera = CameraOrbit(w, h)

    def init(self):
        """Создание окна, инициализация"""
        self.screen = pygame.display.set_mode((self.w, self.h), HWSURFACE | OPENGL | DOUBLEBUF | RESIZABLE)
        pygame.display.set_caption(self.name)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        self.clock = pygame.time.Clock()
        self.cube = Cube()
        self.camera.init()

    def loop_step(self):
        """Обработка цикла рендеринга pygame"""
        # задаем максимальное количество кадров в секунду
        self.clock.tick(self.frame_rate)
        # считываем все произошедшие событие
        for event in pygame.event.get():
            # обробатываем выход из приложения
            if event.type == QUIT:
                self.quit()
                return
            if event.type == KEYUP and event.key == K_ESCAPE:
                self.quit()
                return
            # обрабатываем изменение размера окна
            if event.type == VIDEORESIZE:
                self.reshape(*event.size)
            # обработка события
            self.event(event)
        # обновляем камеру
        self.camera.update()
        # что-то рисуем
        self.render()
        # показываем в заголовке окна FPS
        self.fps()
        # смена кадров, т.к. мы используем DOUBLEBUF режим
        pygame.display.flip()

    def quit(self):
        """Выход из приложения, закрытие окна"""
        pygame.quit()
        quit()

    def loop(self):
        """Запускает бесконечный цикл рендеринга"""
        while True:
            self.loop_step()

    def reshape(self, width, height):
        """Обрабатываем изменение размера окна"""
        self.w = self.camera.w = width
        self.h = self.camera.h = height

    def event(self, e):
        """Обрабатываем события"""
        self.camera.event(e)
        self.cube.event(e)

    def fps(self):
        """Рисуем текущий FPS"""
        pygame.display.set_caption("%s FPS: %s" % (self.name, self.clock.get_fps()))

    def run(self):
        """Запуск приложения"""
        self.init()
        #  выставляем начальное положение камеры
        self.camera.update()
        self.loop()

    def render(self):
        """Рисуем"""
        # Очищаем экран
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # Включаем сглаживание
        glEnable(GL_POLYGON_SMOOTH)
        # Рисуем куб
        self.cube.render()


if __name__ == '__main__':
    main = Controller()
    main.run()
