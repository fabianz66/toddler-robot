import pygame
import sys
import time
import math
import random
import os

# --- COMPATIBILIDAD WINDOWS (DPI Awareness) ---
# Esto hace que el juego se vea nítido en monitores con alta resolución en Windows
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except:
            pass

# ==========================================================
# NOTA DE INSTALACIÓN:
# Si no tienes pygame instalado, ejecuta en tu terminal:
# Windows: pip install pygame
# macOS/Linux: pip3 install pygame
# ==========================================================

# Configuración General (Puedes modificar estos valores)
ANCHO_VENTANA = 1200
ALTO_VENTANA = 900
COLUMNAS = 7
FILAS = 4
MARGEN_SUPERIOR = 100
TAMANO_CELDA = 140
VELOCIDAD_MOVIMIENTO = 8 

# Colores estilo "Infantil/Pastel"
COLOR_FONDO = (255, 253, 231) # Crema claro
COLOR_GRILLA = (224, 224, 224)
COLOR_ROBOT = (255, 112, 67)  # Naranja robótico
COLOR_META = (76, 175, 80)    # Verde meta
COLOR_TEXTO = (62, 39, 35)
COLOR_EJECUTAR = (255, 213, 79)

class Particula:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angulo = random.uniform(0, math.pi * 2)
        velocidad = random.uniform(2, 7)
        self.vx = math.cos(angulo) * velocidad
        self.vy = math.sin(angulo) * velocidad
        self.vida = 255
        self.gravedad = 0.15

    def actualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravedad
        self.vida -= 4

    def dibujar(self, pantalla):
        if self.vida > 0:
            pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), random.randint(2, 4))

class FuegosArtificiales:
    def __init__(self, ancho, alto):
        self.x = random.randint(100, ancho - 100)
        self.y = alto
        self.target_y = random.randint(100, alto // 2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.velocidad = random.randint(10, 15)
        self.explotado = False
        self.particulas = []

    def actualizar(self):
        if not self.explotado:
            self.y -= self.velocidad
            if self.y <= self.target_y:
                self.explotado = True
                for _ in range(50):
                    self.particulas.append(Particula(self.x, self.y, self.color))
        else:
            for p in self.particulas:
                p.actualizar()
            self.particulas = [p for p in self.particulas if p.vida > 0]

    def dibujar(self, pantalla):
        if not self.explotado:
            pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), 5)
        else:
            for p in self.particulas:
                p.dibujar(pantalla)

class Robot:
    def __init__(self, x, y, imagen_path="robot.png"):
        self.grid_x = x
        self.grid_y = y
        # Coordenadas en píxeles RELATIVAS al inicio de la grilla (0,0 del tablero)
        self.pix_x = x * TAMANO_CELDA
        self.pix_y = y * TAMANO_CELDA
        self.target_pix_x = self.pix_x
        self.target_pix_y = self.pix_y
        self.moviendose = False
        self.angulo = 0
        self.angulo_objetivo = 0
        self.bob = 0
        self.cambiar_imagen(imagen_path)

    def cambiar_imagen(self, path):
        try:
            self.imagen_original = pygame.image.load(path).convert_alpha()
            self.imagen_original = pygame.transform.smoothscale(self.imagen_original, (TAMANO_CELDA - 15, TAMANO_CELDA - 15))
            self.imagen_dibujar = self.imagen_original
        except Exception as e:
            print(f"Error cargando {path}: {e}")
            self.imagen_original = None
            self.imagen_dibujar = None

    def mover(self, direccion):
        if self.moviendose: return
        
        if direccion == "ARRIBA" and self.grid_y > 0:
            self.grid_y -= 1
        elif direccion == "ABAJO" and self.grid_y < FILAS - 1:
            self.grid_y += 1
        elif direccion == "IZQUIERDA" and self.grid_x > 0:
            self.grid_x -= 1
        elif direccion == "DERECHA" and self.grid_x < COLUMNAS - 1:
            self.grid_x += 1
        
        # Target relativo al inicio de la grilla
        self.target_pix_x = self.grid_x * TAMANO_CELDA
        self.target_pix_y = self.grid_y * TAMANO_CELDA
        self.moviendose = True

    def actualizar(self):
        t = pygame.time.get_ticks()
        
        if self.moviendose:
            # Animación de caminado más visible (más salto y más deformación)
            self.bob = abs(math.sin(t * 0.015)) * 20 # Aumentado de 12 a 20
            scale_y = 1.0 + math.sin(t * 0.015) * 0.15 # Aumentado de 0.1 a 0.15
        else:
            # Respiración suave
            self.bob = math.sin(t * 0.003) * 4
            scale_y = 1.0 + math.sin(t * 0.003) * 0.03

        if self.imagen_original:
            w, h = self.imagen_original.get_size()
            self.imagen_dibujar = pygame.transform.smoothscale(self.imagen_original, (int(w), int(h * scale_y)))

        dx = self.target_pix_x - self.pix_x
        dy = self.target_pix_y - self.pix_y
        
        if abs(dx) < VELOCIDAD_MOVIMIENTO:
            self.pix_x = self.target_pix_x
        else:
            self.pix_x += VELOCIDAD_MOVIMIENTO if dx > 0 else -VELOCIDAD_MOVIMIENTO
            
        if abs(dy) < VELOCIDAD_MOVIMIENTO:
            self.pix_y = self.target_pix_y
        else:
            self.pix_y += VELOCIDAD_MOVIMIENTO if dy > 0 else -VELOCIDAD_MOVIMIENTO
            
        if self.pix_x == self.target_pix_x and self.pix_y == self.target_pix_y:
            self.moviendose = False

    def dibujar(self, pantalla, offset_x):
        if self.imagen_dibujar:
            # Calcular posición absoluta en pantalla aplicando el offset_x actual
            abs_x = self.pix_x + offset_x
            abs_y = self.pix_y + MARGEN_SUPERIOR
            
            sombra_rect = pygame.Rect(0, 0, TAMANO_CELDA // 2, 10)
            sombra_rect.center = (abs_x + TAMANO_CELDA // 2, abs_y + TAMANO_CELDA - 10)
            pygame.draw.ellipse(pantalla, (220, 220, 220), sombra_rect)
            
            rect = self.imagen_dibujar.get_rect(center=(abs_x + TAMANO_CELDA // 2, abs_y + TAMANO_CELDA // 2 - self.bob))
            pantalla.blit(self.imagen_dibujar, rect)
        else:
            abs_x = self.pix_x + offset_x
            abs_y = self.pix_y + MARGEN_SUPERIOR
            centro = (abs_x + TAMANO_CELDA // 2, abs_y + TAMANO_CELDA // 2)
            pygame.draw.circle(pantalla, COLOR_ROBOT, centro, TAMANO_CELDA // 3)

# Cargar imagen de la meta y iconos globalmente
IMAGEN_META = None
ICONOS_BOTONES = {}
SONIDO_CHEER = None

def cargar_recursos():
    global IMAGEN_META, ICONOS_BOTONES, SONIDO_CHEER
    try:
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("background.mp3")
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.3)
        except: pass

        try:
            SONIDO_CHEER = pygame.mixer.Sound("cheer.mp3")
        except: pass

        try:
            img = pygame.image.load("cricri.png").convert_alpha()
            IMAGEN_META = pygame.transform.smoothscale(img, (TAMANO_CELDA - 20, TAMANO_CELDA - 20))
        except: pass
        
        mapeo = {"up": "ARRIBA", "down": "ABAJO", "left": "IZQUIERDA", "right": "DERECHA", "play": "PLAY", "restart": "REINICIAR"}
        for file_name, key in mapeo.items():
            try:
                img = pygame.image.load(f"icon_{file_name}.png").convert_alpha()
                ICONOS_BOTONES[key] = pygame.transform.smoothscale(img, (70, 70))
            except: pass
    except Exception as e:
        print(f"Error cargando recursos: {e}")

def dibujar_meta(pantalla, x, y):
    if IMAGEN_META:
        # Dibujar meta estática centrada en la celda
        rect = IMAGEN_META.get_rect(center=(x + TAMANO_CELDA // 2, y + TAMANO_CELDA // 2))
        pantalla.blit(IMAGEN_META, rect)
    else:
        pass

class Boton:
    def __init__(self, x, y, ancho, alto, accion, color):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.accion = accion
        self.color = color
        self.presionado = False
        # Escalar el icono proporcionalmente al tamaño del botón
        self.icono = None
        base_icon = ICONOS_BOTONES.get(accion)
        if base_icon:
            # El icono ocupará el 65% del lado más corto del botón para dejar un margen
            padding = min(ancho, alto) * 0.35
            target_size = int(min(ancho, alto) - padding)
            self.icono = pygame.transform.smoothscale(base_icon, (target_size, target_size))

    def dibujar(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        color_actual = self.color
        if self.rect.collidepoint(mouse_pos):
            color_actual = tuple(min(c + 20, 255) for c in self.color)
        
        # Efecto de presión
        offset = 4 if self.presionado else 0
        rect_dibujo = self.rect.move(offset, offset)
        
        # Sombra (solo si no está presionado)
        if not self.presionado:
            pygame.draw.rect(pantalla, (150, 150, 150), (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), border_radius=15)
        
        # Botón
        pygame.draw.rect(pantalla, color_actual, rect_dibujo, border_radius=15)
        pygame.draw.rect(pantalla, COLOR_TEXTO, rect_dibujo, 3, border_radius=15)
        
        if self.icono:
            rect_icon = self.icono.get_rect(center=rect_dibujo.center)
            pantalla.blit(self.icono, rect_icon)
        else:
            try:
                # Mapeo de texto para botones sin icono
                textos = {
                    "ROBOT_SEL": "Robot",
                    "TEACHER_SEL": "Profe"
                }
                txt_mostrar = textos.get(self.accion, self.accion)
                
                f = pygame.font.SysFont("Arial", 24, bold=True)
                img = f.render(txt_mostrar, True, COLOR_TEXTO)
                pantalla.blit(img, img.get_rect(center=rect_dibujo.center))
            except: pass

    def clic(self, pos):
        return self.rect.collidepoint(pos)

def main():
    pygame.init()
    pantalla_actual_w, pantalla_actual_h = ANCHO_VENTANA, ALTO_VENTANA
    pantalla = pygame.display.set_mode((pantalla_actual_w, pantalla_actual_h), pygame.RESIZABLE)
    cargar_recursos()
    pygame.display.set_caption("🤖 Mi Amigo Robot")
    
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
    fuente_pequena = pygame.font.SysFont("Comic Sans MS", 24)
    
    personaje_actual = "robot.png"
    robot = Robot(0, 0, personaje_actual)
    meta_pos_lista = [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)]
    lista_fuegos = []

    while True:
        tiempo_actual = pygame.time.get_ticks()
        pantalla_actual_w, pantalla_actual_h = pantalla.get_size()
        offset_x_global = (pantalla_actual_w - COLUMNAS * TAMANO_CELDA) // 2
        
        # --- DISEÑO DE BOTONES (Sin Play, movimiento directo) ---
        ancho_btn, alto_btn, espacio = 160, 100, 15
        ancho_cluster = (ancho_btn * 3) + (espacio * 2)
        
        x_base_central = (pantalla_actual_w - ancho_cluster) // 2
        y_base = pantalla_actual_h - 130
        
        # Botón de reinicio en la esquina
        ancho_reset, alto_reset = 120, 80
        x_reset = pantalla_actual_w - ancho_reset - 20
        y_reset = pantalla_actual_h - alto_reset - 20
        
        # Botones de Selección de Personaje (Top Derecha)
        btn_robot = Boton(pantalla_actual_w - 280, 20, 120, 60, "ROBOT_SEL", (200, 200, 200))
        btn_profe = Boton(pantalla_actual_w - 140, 20, 120, 60, "TEACHER_SEL", (200, 200, 200))
        
        botones = [
            # Fila Inferior (Flechas)
            Boton(x_base_central, y_base, ancho_btn, alto_btn, "IZQUIERDA", (255, 245, 157)),
            Boton(x_base_central + (ancho_btn + espacio), y_base, ancho_btn, alto_btn, "ABAJO", (244, 143, 177)),
            Boton(x_base_central + (ancho_btn + espacio) * 2, y_base, ancho_btn, alto_btn, "DERECHA", (165, 214, 167)),
            
            # Fila Superior (Arriba)
            Boton(x_base_central + (ancho_btn + espacio), y_base - alto_btn - 8, ancho_btn, alto_btn, "ARRIBA", (129, 212, 250)),
            
            # Botón REINICIAR
            Boton(x_reset, y_reset, ancho_reset, alto_reset, "REINICIAR", (255, 204, 128)),
            
            # Selección de personaje
            btn_robot, btn_profe
        ]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                clic_procesado = False
                for btn in botones:
                    if btn.clic(evento.pos):
                        btn.presionado = True
                        clic_procesado = True
                        if btn.accion == "REINICIAR":
                            robot = Robot(0, 0, personaje_actual)
                            meta_pos_lista = [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)]
                            lista_fuegos = []
                        elif btn.accion == "ROBOT_SEL":
                            personaje_actual = "robot.png"
                            robot.cambiar_imagen(personaje_actual)
                        elif btn.accion == "TEACHER_SEL":
                            personaje_actual = "fer.png"
                            robot.cambiar_imagen(personaje_actual)
                        elif btn.accion in ["ARRIBA", "ABAJO", "IZQUIERDA", "DERECHA"]:
                            # MOVIMIENTO INMEDIATO
                            robot.mover(btn.accion)
                
                # 2. Revisar Clic en Grilla (Solo si no fue un botón de UI y el robot está quieto)
                if not clic_procesado and not robot.moviendose:
                    adyacentes = [
                        ("ARRIBA", robot.grid_x, robot.grid_y - 1),
                        ("ABAJO", robot.grid_x, robot.grid_y + 1),
                        ("IZQUIERDA", robot.grid_x - 1, robot.grid_y),
                        ("DERECHA", robot.grid_x + 1, robot.grid_y)
                    ]
                    for accion, col, fila in adyacentes:
                        if 0 <= col < COLUMNAS and 0 <= fila < FILAS:
                            rect_celda = pygame.Rect(offset_x_global + col * TAMANO_CELDA, MARGEN_SUPERIOR + fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                            if rect_celda.collidepoint(evento.pos):
                                robot.mover(accion)
                                break
            
            if evento.type == pygame.MOUSEBUTTONUP:
                for btn in botones:
                    btn.presionado = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_q:
                    pygame.quit(); sys.exit()
                if evento.key == pygame.K_f:
                    pygame.display.toggle_fullscreen()
                if evento.key == pygame.K_r:
                    robot = Robot(0, 0, personaje_actual)
                    meta_pos_lista = [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)]
                    lista_fuegos = []

        pantalla.fill(COLOR_FONDO)
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                rect = pygame.Rect(offset_x_global + col * TAMANO_CELDA, MARGEN_SUPERIOR + fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                pygame.draw.rect(pantalla, COLOR_GRILLA, rect, 0)
                pygame.draw.rect(pantalla, (255, 255, 255), rect, 2)

        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if (col, fila) in meta_pos_lista:
                    dibujar_meta(pantalla, offset_x_global + col * TAMANO_CELDA, MARGEN_SUPERIOR + fila * TAMANO_CELDA)

        # --- DIBUJAR ICONOS DE AYUDA EN CELDAS ADYACENTES ---
        if not robot.moviendose and meta_pos_lista:
            adyacentes = [
                ("ARRIBA", robot.grid_x, robot.grid_y - 1),
                ("ABAJO", robot.grid_x, robot.grid_y + 1),
                ("IZQUIERDA", robot.grid_x - 1, robot.grid_y),
                ("DERECHA", robot.grid_x + 1, robot.grid_y)
            ]
            for accion, col, fila in adyacentes:
                if 0 <= col < COLUMNAS and 0 <= fila < FILAS:
                    icon = ICONOS_BOTONES.get(accion)
                    if icon:
                        # Dibujar icono tenue como guía
                        rect_celda = pygame.Rect(offset_x_global + col * TAMANO_CELDA, MARGEN_SUPERIOR + fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                        # Redimensionar icono para la celda
                        tam = int(TAMANO_CELDA * 0.4)
                        icon_guia = pygame.transform.smoothscale(icon, (tam, tam))
                        # Hacerlo traslúcido
                        icon_guia.set_alpha(120)
                        pantalla.blit(icon_guia, icon_guia.get_rect(center=rect_celda.center))

        robot.actualizar()
        robot.dibujar(pantalla, offset_x_global)
        
        pos_robot = (robot.grid_x, robot.grid_y)
        if pos_robot in meta_pos_lista and not robot.moviendose:
            meta_pos_lista.remove(pos_robot)
            if SONIDO_CHEER: SONIDO_CHEER.play()

        for btn in botones: btn.dibujar(pantalla)
            
        # UI Info (Ayuda en la parte superior)
        texto_inst = "Presiona 'F' Pantalla Completa | 'R' Reiniciar | 'Q' Salir"
        img_inst = fuente_pequena.render(texto_inst, True, (150, 150, 150))
        pantalla.blit(img_inst, (20, 10))

        if not meta_pos_lista and not robot.moviendose:
            msg = fuente.render("¡FIN!", True, (255, 152, 0))
            pantalla.blit(msg, msg.get_rect(center=(pantalla_actual_w // 2, MARGEN_SUPERIOR // 2 + 10)))
            if random.random() < 0.08: lista_fuegos.append(FuegosArtificiales(pantalla_actual_w, pantalla_actual_h))

        for f in lista_fuegos[:]:
            f.actualizar(); f.dibujar(pantalla)
            if f.explotado and not f.particulas: lista_fuegos.remove(f)

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()
