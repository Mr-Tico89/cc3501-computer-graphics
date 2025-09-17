import pyglet
from OpenGL import GL
import click
import numpy as np
import math
import os

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
        
        # Shaders y OpenGL
        self.shader_program = None
        self.vao = None
        self.vbo = None
        
        # Burn-in inicial
        for _ in range(1000):
            self.update_lorenz()
            
        # Inicializar OpenGL después del burn-in
        self.init_opengl()
    
    def load_shader(self, shader_type, source_or_file):
        #Carga y compila un shader
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(script_dir, source_or_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()

        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        return shader
    
    def init_opengl(self):
        # Cargar shaders
        vertex_shader = self.load_shader(GL.GL_VERTEX_SHADER, "vertex_shader.glsl")
        fragment_shader = self.load_shader(GL.GL_FRAGMENT_SHADER, "fragment_shader.glsl")

        # Crear programa de shader
        self.shader_program = GL.glCreateProgram()
        GL.glAttachShader(self.shader_program, vertex_shader)
        GL.glAttachShader(self.shader_program, fragment_shader)
        GL.glLinkProgram(self.shader_program)
        
        # Crear VAO y VBO para datos reales
        self.vao = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.vao)
        
        self.vbo = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        
        # Configurar atributos de vértice
        GL.glUseProgram(self.shader_program)
        
        # Posición (x, y) - 2 floats
        pos_attrib = GL.glGetAttribLocation(self.shader_program, "position")
        if pos_attrib >= 0:
            GL.glEnableVertexAttribArray(pos_attrib)
            GL.glVertexAttribPointer(pos_attrib, 2, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, GL.GLvoidp(0))
        
        # Ángulo - 1 float
        angle_attrib = GL.glGetAttribLocation(self.shader_program, "angle")
        if angle_attrib >= 0:
            GL.glEnableVertexAttribArray(angle_attrib)
            GL.glVertexAttribPointer(angle_attrib, 1, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, GL.GLvoidp(2 * 4))
        
        # Densidad - 1 float
        density_attrib = GL.glGetAttribLocation(self.shader_program, "density")
        if density_attrib >= 0:
            GL.glEnableVertexAttribArray(density_attrib)
            GL.glVertexAttribPointer(density_attrib, 1, GL.GL_FLOAT, GL.GL_FALSE, 4 * 4, GL.GLvoidp(3 * 4))
        
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
    
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
    
    def switch_view(self):
        # Cambia la vista y reinicia los puntos
        self.current_view = (self.current_view + 1) % 3
        self.points.clear()
        for _ in range(100):
            self.update_lorenz()

    def draw(self):
        # Actualizar varios puntos por frame
        for _ in range(3):
            self.update_lorenz()
        
        self.draw_with_shaders()

    
    def draw_with_shaders(self):
        # Dibuja usando shaders en la GPU
        vertex_data = []
        total_points = len(self.points)
        
        for i, point_data in enumerate(self.points):
            x, y, angle = point_data
            # Calcular densidad normalizada basada en posición en la lista
            density = i / max(1, total_points - 1)  # Evitar división por 0
            vertex_data.extend([x, y, angle, density])
            
        # Convertir a array numpy
        vertex_array = np.array(vertex_data, dtype=np.float32)
        
        # Enviar datos a la GPU
        GL.glBindVertexArray(self.vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertex_array.nbytes, vertex_array, GL.GL_DYNAMIC_DRAW)
        
        # Usar programa de shader
        GL.glUseProgram(self.shader_program)
        
        # Configurar el tamaño de los puntos
        GL.glPointSize(3.0)
        
        # Dibujar los puntos usando la GPU
        GL.glDrawArrays(GL.GL_POINTS, 0, total_points)
        
        # Limpiar estado
        GL.glUseProgram(0)
        GL.glBindVertexArray(0)
    
@click.command("tarea", short_help='Atractor de lorenz')
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)

def tarea(width=800, height=600):
    win = pyglet.window.Window(width, height, caption="Atractor de Lorenz - ESPACIO: cambiar vista")
    attractor = Attractor(width, height)
    label = pyglet.text.Label('', font_name='Arial', font_size=16, color=(255, 255, 255, 255), x=10, y=height - 30)
    
    @win.event
    def on_draw():
        win.clear()
        
        # Habilitar blending
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        attractor.draw()

        # Actualizar y dibujar label
        label.text = f"Vista {attractor.view_names[attractor.current_view]}"
        label.draw()
    
    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            attractor.switch_view()
    pyglet.app.run()