import pygame
import sys
import time
import math
import random
import os

# --- COMPATIBILIDAD WINDOWS (DPI Awareness) ---
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
# Windows: pip install pygame
# macOS/Linux: pip3 install pygame
# ==========================================================

# Configuración General
ANCHO_VENTANA = 1400
ALTO_VENTANA = 950
COLUMNAS = 7
FILAS = 4
MARGEN_SUPERIOR = 120 # Espacio para cabecera
TAMANO_CELDA = 180
VELOCIDAD_MOVIMIENTO = 10 

COLOR_FONDO = (255, 253, 231)
COLOR_GRILLA = (224, 224, 224)
COLOR_ROBOT = (255, 112, 67)
COLOR_META = (76, 175, 80)
COLOR_TEXTO = (62, 39, 35)
COLOR_EJECUTAR = (255, 213, 79)

class Particula:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.color = color
        angulo = random.uniform(0, math.pi * 2)
        velocidad = random.uniform(2, 7)
        self.vx, self.vy = math.cos(angulo) * velocidad, math.sin(angulo) * velocidad
        self.vida, self.gravedad = 255, 0.15

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
        self.x, self.y = random.randint(100, ancho - 100), alto
        self.target_y = random.randint(100, alto // 2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.velocidad, self.explotado, self.particulas = random.randint(10, 15), False, []

    def actualizar(self):
        if not self.explotado:
            self.y -= self.velocidad
            if self.y <= self.target_y:
                self.explotado = True
                for _ in range(50): self.particulas.append(Particula(self.x, self.y, self.color))
        else:
            for p in self.particulas: p.actualizar()
            self.particulas = [p for p in self.particulas if p.vida > 0]

    def dibujar(self, pantalla):
        if not self.explotado: pygame.draw.circle(pantalla, self.color, (int(self.x), int(self.y)), 5)
        else:
            for p in self.particulas: p.dibujar(pantalla)

class Robot:
    def __init__(self, x, y, imagen_path="robot.png"):
        self.grid_x, self.grid_y = x, y
        self.pix_x, self.pix_y = x * TAMANO_CELDA, y * TAMANO_CELDA
        self.target_pix_x, self.target_pix_y = self.pix_x, self.pix_y
        self.moviendose, self.bob = False, 0
        self.cambiar_imagen(imagen_path)

    def cambiar_imagen(self, path):
        try:
            self.imagen_original = pygame.image.load(path).convert_alpha()
            self.imagen_original = pygame.transform.smoothscale(self.imagen_original, (TAMANO_CELDA - 15, TAMANO_CELDA - 15))
            self.imagen_dibujar = self.imagen_original
        except:
            self.imagen_original = self.imagen_dibujar = None

    def mover(self, direccion):
        if self.moviendose: return
        if direccion == "ARRIBA" and self.grid_y > 0: self.grid_y -= 1
        elif direccion == "ABAJO" and self.grid_y < FILAS - 1: self.grid_y += 1
        elif direccion == "IZQUIERDA" and self.grid_x > 0: self.grid_x -= 1
        elif direccion == "DERECHA" and self.grid_x < COLUMNAS - 1: self.grid_x += 1
        self.target_pix_x, self.target_pix_y = self.grid_x * TAMANO_CELDA, self.grid_y * TAMANO_CELDA
        self.moviendose = True

    def actualizar(self):
        t = pygame.time.get_ticks()
        if self.moviendose:
            self.bob = abs(math.sin(t * 0.015)) * 20
            scale_y = 1.0 + math.sin(t * 0.015) * 0.15
        else:
            self.bob = math.sin(t * 0.003) * 4
            scale_y = 1.0 + math.sin(t * 0.003) * 0.03

        if self.imagen_original:
            w, h = self.imagen_original.get_size()
            self.imagen_dibujar = pygame.transform.smoothscale(self.imagen_original, (int(w), int(h * scale_y)))

        dx, dy = self.target_pix_x - self.pix_x, self.target_pix_y - self.pix_y
        if abs(dx) < VELOCIDAD_MOVIMIENTO: self.pix_x = self.target_pix_x
        else: self.pix_x += VELOCIDAD_MOVIMIENTO if dx > 0 else -VELOCIDAD_MOVIMIENTO
        if abs(dy) < VELOCIDAD_MOVIMIENTO: self.pix_y = self.target_pix_y
        else: self.pix_y += VELOCIDAD_MOVIMIENTO if dy > 0 else -VELOCIDAD_MOVIMIENTO
        if self.pix_x == self.target_pix_x and self.pix_y == self.target_pix_y: self.moviendose = False

    def dibujar(self, pantalla, offset_x):
        if self.imagen_dibujar:
            abs_x, abs_y = self.pix_x + offset_x, self.pix_y + MARGEN_SUPERIOR
            sombra_rect = pygame.Rect(0, 0, TAMANO_CELDA // 2, 10)
            sombra_rect.center = (abs_x + TAMANO_CELDA // 2, abs_y + TAMANO_CELDA - 10)
            pygame.draw.ellipse(pantalla, (220, 220, 220), sombra_rect)
            rect = self.imagen_dibujar.get_rect(center=(abs_x + TAMANO_CELDA // 2, abs_y + TAMANO_CELDA // 2 - self.bob))
            pantalla.blit(self.imagen_dibujar, rect)

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
        try: SONIDO_CHEER = pygame.mixer.Sound("cheer.mp3")
        except: pass
        try:
            img = pygame.image.load("cricri.png").convert_alpha()
            IMAGEN_META = pygame.transform.smoothscale(img, (TAMANO_CELDA - 20, TAMANO_CELDA - 20))
        except: pass
        mapeo = {"up": "ARRIBA", "down": "ABAJO", "left": "IZQUIERDA", "right": "DERECHA", "play": "PLAY", "restart": "REINICIAR"}
        for f_name, key in mapeo.items():
            try:
                img = pygame.image.load(f"icon_{f_name}.png").convert_alpha()
                ICONOS_BOTONES[key] = pygame.transform.smoothscale(img, (70, 70))
            except: pass
        try: ICONOS_BOTONES["FINGER"] = pygame.image.load("hand.png").convert_alpha()
        except: pass
    except Exception as e: print(f"Error recursos: {e}")

def dibujar_meta(pantalla, x, y):
    if IMAGEN_META:
        rect = IMAGEN_META.get_rect(center=(x + TAMANO_CELDA // 2, y + TAMANO_CELDA // 2))
        pantalla.blit(IMAGEN_META, rect)

class Boton:
    def __init__(self, x, y, ancho, alto, accion, color):
        self.rect, self.accion, self.color, self.presionado = pygame.Rect(x, y, ancho, alto), accion, color, False
        base_icon = ICONOS_BOTONES.get(accion)
        if base_icon:
            padding = min(ancho, alto) * 0.35
            target_size = int(min(ancho, alto) - padding)
            self.icono = pygame.transform.smoothscale(base_icon, (target_size, target_size))
        else: self.icono = None

    def dibujar(self, pantalla):
        color_act = tuple(min(c + 20, 255) for c in self.color) if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        offset = 4 if self.presionado else 0
        rect_d = self.rect.move(offset, offset)
        if not self.presionado: pygame.draw.rect(pantalla, (150, 150, 150), (self.rect.x + 4, self.rect.y + 4, self.rect.width, self.rect.height), border_radius=15)
        pygame.draw.rect(pantalla, color_act, rect_d, border_radius=15)
        pygame.draw.rect(pantalla, COLOR_TEXTO, rect_d, 3, border_radius=15)
        if self.icono: pantalla.blit(self.icono, self.icono.get_rect(center=rect_d.center))
        else:
            try:
                txt = {"ROBOT_SEL": "Robot", "TEACHER_SEL": "Profe"}.get(self.accion, self.accion)
                f = pygame.font.SysFont("Arial", 24, bold=True)
                img = f.render(txt, True, COLOR_TEXTO)
                pantalla.blit(img, img.get_rect(center=rect_d.center))
            except: pass

    def clic(self, pos): return self.rect.collidepoint(pos)

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.RESIZABLE)
    cargar_recursos()
    pygame.display.set_caption("🤖 Mi Amigo Robot")
    reloj, fuente, fuente_pequena = pygame.time.Clock(), pygame.font.SysFont("Comic Sans MS", 36, bold=True), pygame.font.SysFont("Comic Sans MS", 24)
    personaje_actual, robot, meta_pos_lista = "robot.png", Robot(0, 0, "robot.png"), [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)]
    lista_fuegos, fullscreen = [], False

    while True:
        pantalla_w, pantalla_h = pantalla.get_size()
        offset_x = (pantalla_w - COLUMNAS * TAMANO_CELDA) // 2
        
        # --- PATHFINDING (Dedo) ---
        accion_sug, dx_sug, dy_sug, ang_sug = None, 0, 0, 0
        if not robot.moviendose and meta_pos_lista:
            meta_c = sorted(meta_pos_lista, key=lambda m: abs(m[0]-robot.grid_x)+abs(m[1]-robot.grid_y))[0]
            gx, gy = meta_c
            if abs(gx - robot.grid_x) >= abs(gy - robot.grid_y) and gx != robot.grid_x:
                if gx > robot.grid_x: accion_sug, dx_sug, ang_sug = "DERECHA", 1, 270
                else: accion_sug, dx_sug, ang_sug = "IZQUIERDA", -1, 90
            elif gy != robot.grid_y:
                if gy > robot.grid_y: accion_sug, dy_sug, ang_sug = "ABAJO", 1, 180
                else: accion_sug, dy_sug, ang_sug = "ARRIBA", -1, 0

        # --- UI BOTONES (Fuera de la grilla) ---
        an_s, al_s = 130, 60
        btn_rob = Boton(20, 30, an_s, al_s, "ROBOT_SEL", (200, 200, 200))
        btn_pro = Boton(20 + an_s + 15, 30, an_s, al_s, "TEACHER_SEL", (200, 200, 200))
        btn_res = Boton(pantalla_w - an_s - 20, 30, an_s, al_s, "REINICIAR", (255, 204, 128))
        botones = [btn_rob, btn_pro, btn_res]

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                clic_p = False
                for b in botones:
                    if b.clic(ev.pos):
                        b.presionado = clic_p = True
                        if b.accion == "REINICIAR":
                            robot, meta_pos_lista, lista_fuegos = Robot(0, 0, personaje_actual), [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)], []
                        elif b.accion == "ROBOT_SEL": personaje_actual = "robot.png"; robot.cambiar_imagen(personaje_actual)
                        elif b.accion == "TEACHER_SEL": personaje_actual = "fer.png"; robot.cambiar_imagen(personaje_actual)
                if not clic_p and not robot.moviendose:
                    r_rob = pygame.Rect(offset_x + robot.grid_x * TAMANO_CELDA, MARGEN_SUPERIOR + robot.grid_y * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                    if r_rob.collidepoint(ev.pos) and accion_sug: robot.mover(accion_sug)
                    else:
                        for a, c, f in [("ARRIBA",robot.grid_x,robot.grid_y-1),("ABAJO",robot.grid_x,robot.grid_y+1),("IZQUIERDA",robot.grid_x-1,robot.grid_y),("DERECHA",robot.grid_x+1,robot.grid_y)]:
                            if 0<=c<COLUMNAS and 0<=f<FILAS and pygame.Rect(offset_x+c*TAMANO_CELDA, MARGEN_SUPERIOR+f*TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA).collidepoint(ev.pos):
                                robot.mover(a); break
            if ev.type == pygame.MOUSEBUTTONUP:
                for b in botones: b.presionado = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_q: pygame.quit(); sys.exit()
                if ev.key == pygame.K_f:
                    fullscreen = not fullscreen
                    res = pygame.display.Info()
                    pantalla = pygame.display.set_mode((res.current_w, res.current_h), pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE)
                if ev.key == pygame.K_r: robot, meta_pos_lista, lista_fuegos = Robot(0, 0, personaje_actual), [(6, 3), (3, 2), (5, 0), (1, 3), (2, 0), (0, 2), (4, 1), (6, 0)], []

        pantalla.fill(COLOR_FONDO)
        for f in range(FILAS):
            for c in range(COLUMNAS):
                r = pygame.Rect(offset_x + c * TAMANO_CELDA, MARGEN_SUPERIOR + f * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                pygame.draw.rect(pantalla, COLOR_GRILLA, r, 0); pygame.draw.rect(pantalla, (255, 255, 255), r, 2)
                if (c, f) in meta_pos_lista: dibujar_meta(pantalla, r.x, r.y)

        if accion_sug:
            h = ICONOS_BOTONES.get("FINGER")
            if h:
                p = math.sin(pygame.time.get_ticks() * 0.015) * 15
                t_c, t_f = robot.grid_x + dx_sug, robot.grid_y + dy_sug
                r_c = pygame.Rect(offset_x + t_c * TAMANO_CELDA, MARGEN_SUPERIOR + t_f * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
                i_r = pygame.transform.smoothscale(pygame.transform.rotate(h, ang_sug), (int(TAMANO_CELDA*0.6), int(TAMANO_CELDA*0.6)))
                pantalla.blit(i_r, i_r.get_rect(center=(r_c.centerx + dx_sug*p, r_c.centery + dy_sug*p)))

        robot.actualizar(); robot.dibujar(pantalla, offset_x)
        p_r = (robot.grid_x, robot.grid_y)
        if p_r in meta_pos_lista and not robot.moviendose:
            meta_pos_lista.remove(p_r)
            if SONIDO_CHEER: SONIDO_CHEER.play()
        
        for b in botones: b.dibujar(pantalla)
        
        fin_grilla_y = MARGEN_SUPERIOR + FILAS * TAMANO_CELDA
        y_ayuda = fin_grilla_y + (pantalla_h - fin_grilla_y) // 2
        p_inst = fuente_pequena.render("F: Pantalla Completa | R: Reiniciar | Q: Salir", True, (150, 150, 150))
        pantalla.blit(p_inst, p_inst.get_rect(center=(pantalla_w // 2, y_ayuda)))

        if not meta_pos_lista and not robot.moviendose:
            msg = fuente.render("¡FIN!", True, (255, 152, 0))
            pantalla.blit(msg, msg.get_rect(center=(pantalla_w // 2, MARGEN_SUPERIOR // 2 + 10)))
            if random.random() < 0.08: lista_fuegos.append(FuegosArtificiales(pantalla_w, pantalla_h))
        for f in lista_fuegos[:]:
            f.actualizar(); f.dibujar(pantalla)
            if f.explotado and not f.particulas: lista_fuegos.remove(f)
        pygame.display.flip(); reloj.tick(60)

if __name__ == "__main__": main()
