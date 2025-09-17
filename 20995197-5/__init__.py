import pyglet
from OpenGL import GL
import click
import numpy as np
import math

class Attractor:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.current_view = 0  # 0: XY, 1: XZ, 2: YZ
        self.view_names = ["XY", "XZ", "YZ"]
        
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
        # Guardar estado anterior para calcular velocidad
        prev_x, prev_y, prev_z = self.x, self.y, self.z
        
        dx = self.sigma * (self.y - self.x)
        dy = self.x * (self.rho - self.z) - self.y
        dz = self.x * self.y - self.beta * self.z
        
        self.x += dx * self.dt
        self.y += dy * self.dt
        self.z += dz * self.dt
        
        # Calcular velocidad para ángulo de trayectoria
        vel_x = self.x - prev_x
        vel_y = self.y - prev_y
        vel_z = self.z - prev_z
        
        # Normalizar coordenadas para cada vista
        if self.current_view == 0:  # XY
            point = [self.x / 25.0, self.y / 25.0]
            angle = math.atan2(vel_y, vel_x)

        elif self.current_view == 1:  # XZ
            point = [self.x / 25.0, (self.z - 25.0) / 25.0]
            angle = math.atan2(vel_z, vel_x)
            
        else:  # YZ
            point = [self.y / 25.0, (self.z - 25.0) / 25.0]
            angle = math.atan2(vel_z, vel_y)
        
        # Agregar punto con su ángulo
        self.points.append([point[0], point[1], angle])
        
        # Mantener solo los últimos puntos
        if len(self.points) > self.max_points:
            self.points.pop(0)
    
    def get_color_hsv(self, index, angle):
        total = len(self.points)
        if total == 0:
            return (1.0, 1.0, 1.0)
        
        # Matiz (H): basado en el ángulo de la trayectoria
        hue = (angle + math.pi) / (2 * math.pi) 
        
        # Saturación (S): basada en densidad normalizada (más reciente = más saturado)
        saturation = min(1.0, index / (total * 0.7))
        
        # Valor/Brillo (V): alto para puntos visitados
        value = 0.8 + 0.2 * (index / total)
        
        return self.hsv_to_rgb(hue * 360.0, saturation, value)
    
    def hsv_to_rgb(self, h, s, v):
        # Convierte HSV a RGB
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
        # Cambia la vista y reinicia los puntos
        self.current_view = (self.current_view + 1) % 3
        self.points.clear()
    
    def reset(self):
        """Reinicia la simulación"""
        self.x, self.y, self.z = 0.1, 0.0, 0.0
        self.points.clear()
    
    def draw(self):
        # Actualizar varios puntos por frame
        for _ in range(3):
            self.update_lorenz()
        
        # Dibujar puntos usando funciones básicas de pyglet
        if len(self.points) > 1:
            # Convertir puntos a coordenadas de pantalla
            points_to_draw = []
            colors_to_draw = []
            
            for i, point_data in enumerate(self.points):
                x, y, angle = point_data
                # Convertir de [-1,1] a coordenadas de pantalla
                screen_x = int((x + 1.0) * 0.5 * self.width)
                screen_y = int((y + 1.0) * 0.5 * self.height)
                
                color = self.get_color_hsv(i, angle)
                points_to_draw.append((screen_x, screen_y))
                colors_to_draw.append(color)
            
            # Dibujar usando pyglet shapes
            for i, (point, color) in enumerate(zip(points_to_draw, colors_to_draw)):
                # Crear un círculo pequeño para cada punto
                circle = pyglet.shapes.Circle(point[0], point[1], 1.5, color=(int(color[0]*255), int(color[1]*255), int(color[2]*255)))
                circle.draw()

@click.command("tarea", short_help='Atractor de Lorenz Simple')
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)

def tarea(width, height):
    win = pyglet.window.Window(width, height, caption="Atractor de Lorenz - ESPACIO: cambiar vista, R: reiniciar")
    attractor = Attractor(width, height)
    label = pyglet.text.Label('', font_name='Arial', font_size=16, color=(255, 255, 255, 255), x=10, y=height - 30)
    
    @win.event
    def on_draw():
        win.clear()
        attractor.draw()
        
        # Actualizar y dibujar label
        label.text = f"Vista {attractor.view_names[attractor.current_view]} - Puntos: {len(attractor.points)}"
        label.draw()
    
    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            attractor.switch_view()

        elif symbol == pyglet.window.key.R:
            attractor.reset()
    
    pyglet.app.run()