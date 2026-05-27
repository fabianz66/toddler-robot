import pygame
import sys
import time
import math

# ==========================================================
# NOTA DE INSTALACIÓN:
# Si no tienes pygame instalado, ejecuta en tu terminal:
# pip install pygame
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

class Robot:
    def __init__(self, x, y):
        self.grid_x = x
        self.grid_y = y
        self.pix_x = x * TAMANO_CELDA
        self.pix_y = y * TAMANO_CELDA
        self.target_pix_x = self.pix_x
        self.target_pix_y = self.pix_y
        self.moviendose = False
        self.angulo = 0
        self.angulo_objetivo = 0
        
        # --- CARGAR SPRITE SHEET DE CAMINADO ---
        try:
            sheet = pygame.image.load("character_walking.png").convert_alpha()
            sheet_w, sheet_h = sheet.get_size()
            frame_w = sheet_w // 4
            self.frames = []
            for i in range(4):
                frame = sheet.subsurface((i * frame_w, 0, frame_w, sheet_h))
                # Escalar a tamaño de celda
                self.frames.append(pygame.transform.smoothscale(frame, (TAMANO_CELDA - 10, TAMANO_CELDA - 10)))
            self.frame_actual = 0
            self.imagen = self.frames[0]
        except Exception as e:
            print(f"Error cargando character_walking.png: {e}")
            self.frames = []
            self.imagen = None

    def mover(self, direccion, offset_x):
        if self.moviendose: return
        
        if direccion == "ARRIBA" and self.grid_y > 0:
            self.grid_y -= 1
            self.angulo_objetivo = 0
        elif direccion == "ABAJO" and self.grid_y < FILAS - 1:
            self.grid_y += 1
            self.angulo_objetivo = 180
        elif direccion == "IZQUIERDA" and self.grid_x > 0:
            self.grid_x -= 1
            self.angulo_objetivo = 90
        elif direccion == "DERECHA" and self.grid_x < COLUMNAS - 1:
            self.grid_x += 1
            self.angulo_objetivo = 270
        
        self.target_pix_x = self.grid_x * TAMANO_CELDA + offset_x
        self.target_pix_y = self.grid_y * TAMANO_CELDA + MARGEN_SUPERIOR
        self.moviendose = True

    def actualizar(self):
        t = pygame.time.get_ticks()
        
        # Ciclo de frames y bobbing
        if self.moviendose:
            # Alternar entre frame neutral (0), squash (1) y stretch (2)
            # Esto crea un efecto de "pasos" sin rotar el cuerpo
            self.frame_actual = (t // 120) % 3
            self.bob = abs(math.sin(t * 0.015)) * 10
        else:
            self.frame_actual = 0
            # Respiración suave
            self.bob = math.sin(t * 0.003) * 3

        # Asignar imagen sin rotación
        if self.frames:
            self.imagen_dibujar = self.frames[self.frame_actual]

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

    def dibujar(self, pantalla):
        if self.imagen_dibujar:
            # Sombra
            sombra_rect = pygame.Rect(0, 0, TAMANO_CELDA // 2, 10)
            sombra_rect.center = (self.pix_x + TAMANO_CELDA // 2, self.pix_y + TAMANO_CELDA - 10)
            pygame.draw.ellipse(pantalla, (220, 220, 220), sombra_rect)
            
            # Dibujar siempre derecho con el bob (salto)
            rect = self.imagen_dibujar.get_rect(center=(self.pix_x + TAMANO_CELDA // 2, self.pix_y + TAMANO_CELDA // 2 - self.bob))
            pantalla.blit(self.imagen_dibujar, rect)
        else:
            x, y = self.pix_x, self.pix_y
            centro = (x + TAMANO_CELDA // 2, y + TAMANO_CELDA // 2)
            pygame.draw.circle(pantalla, COLOR_ROBOT, centro, TAMANO_CELDA // 3)

# Cargar imagen de la meta y iconos globalmente
IMAGEN_META = None
ICONOS_BOTONES = {}
SONIDO_CHEER = None

def cargar_recursos():
    global IMAGEN_META, ICONOS_BOTONES, SONIDO_CHEER
    print("DEBUG: Iniciando cargar_recursos")
    try:
        # Mixer para audio
        pygame.mixer.init()
        
        # Música de fondo
        try:
            pygame.mixer.music.load("background.mp3")
            pygame.mixer.music.play(-1) # Bucle infinito
            pygame.mixer.music.set_volume(0.3)
            print("DEBUG: Música de fondo cargada")
        except Exception as e:
            print(f"No se pudo cargar background.mp3: {e}")

        # Sonido de victoria
        try:
            SONIDO_CHEER = pygame.mixer.Sound("cheer.mp3")
            print("DEBUG: Sonido cheer cargado")
        except Exception as e:
            print(f"No se pudo cargar cheer.mp3: {e}")

        # Meta
        img = pygame.image.load("hat.png").convert_alpha()
        IMAGEN_META = pygame.transform.smoothscale(img, (TAMANO_CELDA - 20, TAMANO_CELDA - 20))
        
        # Iconos de botones (Mapeo explícito)
        mapeo = {
            "up": "ARRIBA",
            "down": "ABAJO",
            "left": "IZQUIERDA",
            "right": "DERECHA",
            "play": "PLAY"
        }
        for file_name, key in mapeo.items():
            try:
                img = pygame.image.load(f"icon_{file_name}.png").convert_alpha()
                ICONOS_BOTONES[key] = pygame.transform.smoothscale(img, (70, 70))
                print(f"DEBUG: Icono cargado exitosamente: {key} (size: {ICONOS_BOTONES[key].get_size()})")
            except Exception as e:
                print(f"DEBUG ERROR: No se pudo cargar icon_{file_name}.png: {e}")
    except Exception as e:
        print(f"DEBUG ERROR: Error general en cargar_recursos: {e}")
    print(f"DEBUG: ICONOS_BOTONES contiene: {list(ICONOS_BOTONES.keys())}")

def dibujar_meta(pantalla, x, y):
    if IMAGEN_META:
        rect = IMAGEN_META.get_rect(center=(x + TAMANO_CELDA // 2, y + TAMANO_CELDA // 2))
        # Animación suave de "meta" (levitar)
        offset_meta = math.sin(pygame.time.get_ticks() * 0.005) * 5
        rect.y += offset_meta
        pantalla.blit(IMAGEN_META, rect)
    else:
        centro = (x + TAMANO_CELDA // 2, y + TAMANO_CELDA // 2)
        # Una estrella o trofeo simple
        puntos = []
        for i in range(10):
            radio = 35 if i % 2 == 0 else 15
            angulo = i * (3.1415 * 2 / 10)
            px = centro[0] + radio * pygame.math.Vector2(1, 0).rotate_rad(angulo).x
            py = centro[1] + radio * pygame.math.Vector2(1, 0).rotate_rad(angulo).y
            puntos.append((px, py))
        pygame.draw.polygon(pantalla, (255, 215, 0), puntos) # Dorado
        pygame.draw.polygon(pantalla, (184, 134, 11), puntos, 3) # Borde

class Boton:
    def __init__(self, x, y, ancho, alto, accion, color):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.accion = accion
        self.color = color
        # Mapear accion a nombre de icono
        key = accion if accion != "EJECUTAR" else "PLAY"
        self.icono = ICONOS_BOTONES.get(key)
        if self.icono is None:
            print(f"DEBUG: Missing icon for {accion} (key: {key})")

    def dibujar(self, pantalla):
        mouse_pos = pygame.mouse.get_pos()
        color_actual = self.color
        if self.rect.collidepoint(mouse_pos):
            color_actual = tuple(min(c + 20, 255) for c in self.color)
        
        # Sombra
        pygame.draw.rect(pantalla, (150, 150, 150), (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), border_radius=15)
        # Botón
        pygame.draw.rect(pantalla, color_actual, self.rect, border_radius=15)
        pygame.draw.rect(pantalla, COLOR_TEXTO, self.rect, 3, border_radius=15)
        
        if self.icono:
            rect_icon = self.icono.get_rect(center=self.rect.center)
            pantalla.blit(self.icono, rect_icon)
        else:
            # Fallback to text if icon is missing
            try:
                f = pygame.font.SysFont("Arial", 24)
                img = f.render(self.accion, True, COLOR_TEXTO)
                pantalla.blit(img, img.get_rect(center=self.rect.center))
            except:
                pass

    def clic(self, pos):
        return self.rect.collidepoint(pos)

def main():
    pygame.init()
    pantalla_actual_w = ANCHO_VENTANA
    pantalla_actual_h = ALTO_VENTANA
    pantalla = pygame.display.set_mode((pantalla_actual_w, pantalla_actual_h), pygame.RESIZABLE)
    cargar_recursos()
    pygame.display.set_caption("🤖 Mi Amigo Robot - Programación para Niños")
    
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("Comic Sans MS", 36, bold=True)
    fuente_pequena = pygame.font.SysFont("Comic Sans MS", 24)
    
    fullscreen = False
    
    robot = Robot(0, 0)
    # Lista de posiciones para múltiples sombreros
    meta_pos_lista = [(COLUMNAS - 1, FILAS - 1), (3, 2), (5, 0), (1, 3)]
    
    cola_instrucciones = []
    ejecutando = False
    instruccion_actual = 0
    
    # Ajustar posición inicial del robot según el centro
    offset_x_global = (pantalla_actual_w - COLUMNAS * TAMANO_CELDA) // 2
    robot.pix_x = robot.grid_x * TAMANO_CELDA + offset_x_global
    robot.pix_y = robot.grid_y * TAMANO_CELDA + MARGEN_SUPERIOR
    robot.target_pix_x, robot.target_pix_y = robot.pix_x, robot.pix_y

    while True:
        tiempo_actual = pygame.time.get_ticks()
        pantalla_actual_w, pantalla_actual_h = pantalla.get_size()
        offset_x_global = (pantalla_actual_w - COLUMNAS * TAMANO_CELDA) // 2
        
        # Reposicionar botones dinámicamente
        ancho_btn = 160
        alto_btn = 100
        espacio = 20
        inicio_x_btns = (pantalla_actual_w - (ancho_btn * 5 + espacio * 4)) // 2
        y_botones = pantalla_actual_h - 140
        
        botones = [
            Boton(inicio_x_btns, y_botones, ancho_btn, alto_btn, "ARRIBA", (129, 212, 250)),
            Boton(inicio_x_btns + (ancho_btn + espacio), y_botones, ancho_btn, alto_btn, "ABAJO", (244, 143, 177)),
            Boton(inicio_x_btns + (ancho_btn + espacio) * 2, y_botones, ancho_btn, alto_btn, "IZQUIERDA", (255, 245, 157)),
            Boton(inicio_x_btns + (ancho_btn + espacio) * 3, y_botones, ancho_btn, alto_btn, "DERECHA", (165, 214, 167)),
            Boton(inicio_x_btns + (ancho_btn + espacio) * 4, y_botones, ancho_btn, alto_btn, "PLAY", COLOR_EJECUTAR)
        ]

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if evento.type == pygame.VIDEORESIZE and not fullscreen:
                pantalla = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
                if not ejecutando and not robot.moviendose:
                    robot.pix_x = robot.grid_x * TAMANO_CELDA + (evento.w - COLUMNAS * TAMANO_CELDA) // 2
                    robot.target_pix_x = robot.pix_x

            if evento.type == pygame.MOUSEBUTTONDOWN and not ejecutando:
                for btn in botones:
                    if btn.clic(evento.pos):
                        if btn.accion == "PLAY":
                            if cola_instrucciones:
                                ejecutando = True
                                instruccion_actual = 0
                                ultimo_movimiento_tiempo = tiempo_actual
                        else:
                            cola_instrucciones.append(btn.accion)
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pantalla = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    else:
                        pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
                if evento.key == pygame.K_r:
                    robot = Robot(0, 0)
                    robot.pix_x = 0 * TAMANO_CELDA + offset_x_global
                    robot.target_pix_x = robot.pix_x
                    cola_instrucciones = []
                    ejecutando = False

        if ejecutando and not robot.moviendose:
            if tiempo_actual - ultimo_movimiento_tiempo > 500:
                if instruccion_actual < len(cola_instrucciones):
                    robot.mover(cola_instrucciones[instruccion_actual], offset_x_global)
                    instruccion_actual += 1
                    ultimo_movimiento_tiempo = tiempo_actual
                else:
                    ejecutando = False
                    cola_instrucciones = []

        pantalla.fill(COLOR_FONDO)
        
        # Dibujar Grilla con bordes suaves
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                rect = pygame.Rect(offset_x_global + col * TAMANO_CELDA, MARGEN_SUPERIOR + fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                pygame.draw.rect(pantalla, COLOR_GRILLA, rect, 0) # Relleno suave
                pygame.draw.rect(pantalla, (255, 255, 255), rect, 2) # Borde blanco
                
                if (col, fila) in meta_pos_lista:
                    dibujar_meta(pantalla, rect.x, rect.y)

        robot.actualizar()
        robot.dibujar(pantalla)

        # Verificar si el robot llegó a un sombrero
        pos_robot = (robot.grid_x, robot.grid_y)
        if pos_robot in meta_pos_lista and not robot.moviendose:
            meta_pos_lista.remove(pos_robot)
            if SONIDO_CHEER:
                SONIDO_CHEER.play()

        for btn in botones:
            btn.dibujar(pantalla)
            
        # UI Info
        texto_inst = "Presiona 'F' para Pantalla Completa | 'R' para Reiniciar"
        img_inst = fuente_pequena.render(texto_inst, True, (150, 150, 150))
        pantalla.blit(img_inst, (20, 10))

        # Pasos del robot (Cola de instrucciones con iconos)
        x_plan = offset_x_global
        y_plan = MARGEN_SUPERIOR - 45
        img_plan_label = fuente_pequena.render("Instrucciones:", True, COLOR_TEXTO)
        pantalla.blit(img_plan_label, (x_plan, y_plan + 10))
        
        x_iconos = x_plan + img_plan_label.get_width() + 15
        for i, instruccion in enumerate(cola_instrucciones):
            icon = ICONOS_BOTONES.get(instruccion)
            if icon:
                # Dibujar una versión más pequeña de los iconos en la cola
                icon_peq = pygame.transform.smoothscale(icon, (35, 35))
                pantalla.blit(icon_peq, (x_iconos, y_plan + 5))
                x_iconos += 40
                
                # Dibujar flecha de unión "->"
                if i < len(cola_instrucciones) - 1:
                    img_flecha = fuente_pequena.render(">", True, (200, 200, 200))
                    pantalla.blit(img_flecha, (x_iconos, y_plan + 8))
                    x_iconos += 20

        if not meta_pos_lista and not robot.moviendose:
            msg = fuente.render("🌟 ¡ERES GENIAL! 🌟", True, (255, 152, 0))
            pantalla.blit(msg, msg.get_rect(center=(pantalla_actual_w // 2, MARGEN_SUPERIOR // 2 + 10)))

        pygame.display.flip()
        reloj.tick(60)

if __name__ == "__main__":
    main()
