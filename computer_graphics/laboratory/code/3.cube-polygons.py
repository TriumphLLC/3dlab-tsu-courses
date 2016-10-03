"""
Рисуем куб ввиде полигонов, добавляем цвет

Задание: использовать другие примитивы
*Задание: использовать glDrawElements вместо glBegin|glEnd
"""

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *


class Camera(object):
    """Класс для управления камерой

    Пока просто выставляется перспектива.
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h

    def init(self, pos=(0.0, 0.0, -5), fov=45, near=0.1, far=50.0):
        """Выставляет перспективу и положение камеры в соотвествие с параметрами"""
        gluPerspective(fov, (self.w / self.h), near, far)
        glTranslatef(*pos)


class Cube(object):
    """Класс для создание и отрисовки куба"""
    def __init__(self):
        """Заполняем массивы вершин и полигонов"""
        self.verticies = (
            (1, -1, -1),  #0
            (1, 1, -1),   #1
            (-1, 1, -1),  #2
            (-1, -1, -1), #3
            (1, -1, 1),   #4
            (1, 1, 1),    #5
            (-1, -1, 1),  #6
            (-1, 1, 1)    #7
        )
        self.faces = (
            (1, 2, 7, 5),
            (4, 6, 3, 0),
            (5, 7, 6, 4),
            (0, 3, 2, 1),
            (7, 2, 3, 6),
            (1, 5, 4, 0)
        )
        # добавляем цвета для каждого полигона
        self.colors = (
            (0.0, 1.0, 0.0),
            (1.0, 0.5, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 0.0, 1.0),
            (1.0, 0.0, 1.0),
        )

    def render(self):
        """Рисуем куб ввиде полигонов, добавляем цвет"""
        glMatrixMode(GL_MODELVIEW)
        glRotatef(1, 3, 1, 1)
        glBegin(GL_QUADS)
        for fi, faces in enumerate(self.faces):
            glColor3fv(self.colors[fi])
            for vertex in faces:
                glVertex3fv(self.verticies[vertex])
        glEnd()


class Controller(object):
    """Основной класс для создания окна и запуска цикла рендеринга"""

    def __init__(self, w=800, h=600, name="Lab", frame_rate=60):
        """Конструктор нашего класса

        Принимает параметры размера окна, название окна и ограничение количества кадров всекунду
        """
        self.w = w
        self.h = h
        self.name = name
        self.frame_rate = frame_rate
        self.screen = None  # ссылка на созданное коно
        self.clock = None  # вспомогательный объект для контроля FPS
        self.cube = None
        self.camera = Camera(w, h)

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
        """Обратока цикла рендеринга pygame"""
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
        # что-то рисуем
        self.render()
        # показываем в залоговке окна FPS
        self.fps()
        # смена кадров, т.к. мы используем DOUBLEBUF ражим
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
        pass

    def fps(self):
        """Рисуем текущий FPS"""
        pygame.display.set_caption("%s FPS: %s" % (self.name, self.clock.get_fps()))

    def run(self):
        """Запуск приложения"""
        self.init()
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
