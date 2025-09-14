import pyglet
from OpenGL import GL
import click
import numpy as np
import math

class SimpleAttractor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_view = 0  # 0: XY, 1: XZ, 2: YZ
        
        # Parámetros de Lorenz
        self.dt = 0.01
        self.sigma = 10.0
        self.rho = 28.0
        self.beta = 8.0/3.0
        
        # Estado actual
        self.x, self.y, self.z = 0.1, 0.0, 0.0
        
        # Puntos para dibujar
        self.points = []
        self.max_points = 5000
        
        # Burn-in inicial
        for _ in range(1000):
            self.update_lorenz()
    
    def update_lorenz(self):
        """Actualiza un paso del sistema de Lorenz"""
        dx = self.sigma * (self.y - self.x)
        dy = self.x * (self.rho - self.z) - self.y
        dz = self.x * self.y - self.beta * self.z
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
        # Agregar punto normalizado
        if self.current_view == 0:  # XY
            point = [self.x / 25.0, self.y / 25.0]
        elif self.current_view == 1:  # XZ
            point = [self.x / 25.0, (self.z - 15.0) / 25.0]  # Centrar Z alrededor de 15
        else:  # YZ
            point = [self.y / 25.0, (self.z - 15.0) / 25.0]  # Centrar Z alrededor de 15
        
        self.points.append(point)
        
        # Mantener solo los últimos puntos
        if len(self.points) > self.max_points:
            self.points.pop(0)
    
    def get_color(self, index):
        """Calcula color HSV basado en posición y tiempo"""
        total = len(self.points)
        if total == 0:
            return (1.0, 1.0, 1.0)
        
        # Hue basado en la posición en la trayectoria
        hue = (index / total) * 360.0
        
        # Saturación basada en la densidad (más reciente = más saturado)
        saturation = min(1.0, index / (total * 0.5))
        
        # Valor basado en qué tan reciente es el punto
        value = 0.3 + 0.7 * (index / total)
        
        return self.hsv_to_rgb(hue, saturation, value)
    
    def hsv_to_rgb(self, h, s, v):
        """Convierte HSV a RGB"""
        h = h / 60.0
        c = v * s
        x = c * (1 - abs((h % 2) - 1))
        m = v - c
        
        if h < 1:
            r, g, b = c, x, 0
        elif h < 2:
            r, g, b = x, c, 0
        elif h < 3:
            r, g, b = 0, c, x
        elif h < 4:
            r, g, b = 0, x, c
        elif h < 5:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return (r + m, g + m, b + m)
    
    def switch_view(self):
        """Cambia la vista y reinicia los puntos"""
        self.current_view = (self.current_view + 1) % 3
        self.points.clear()
    
    def reset(self):
        """Reinicia la simulación"""
        self.x, self.y, self.z = 0.1, 0.0, 0.0
        self.points.clear()
    
    def draw(self):
        """Dibuja el atractor usando OpenGL inmediato"""
        # Actualizar varios puntos por frame
        for _ in range(3):
            self.update_lorenz()
        
        # Dibujar líneas conectando los puntos
        if len(self.points) > 1:
            GL.glBegin(GL.GL_LINE_STRIP)
            for i, point in enumerate(self.points):
                color = self.get_color(i)
                GL.glColor3f(*color)
                GL.glVertex2f(point[0], point[1])
            GL.glEnd()

@click.command("tarea", short_help='Atractor de Lorenz Simple')
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)
def tarea(width, height):
    win = pyglet.window.Window(width, height, caption="Atractor de Lorenz - ESPACIO: cambiar vista, R: reiniciar")
    attractor = SimpleAttractor(width, height)
    
    @win.event
    def on_draw():
        win.clear()
        
        # Configurar viewport
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-1.2, 1.2, -1.2, 1.2, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
        # Habilitar líneas suaves
        GL.glEnable(GL.GL_LINE_SMOOTH)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glLineWidth(1.5)
        
        # Dibujar atractor
        attractor.draw()
    
    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            attractor.switch_view()
        elif symbol == pyglet.window.key.R:
            attractor.reset()
    
    pyglet.app.run()
