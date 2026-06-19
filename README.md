# 🤖 Mi Amigo Robot

Un juego educativo para niños pequeños que enseña conceptos básicos de programación de forma visual e interactiva.

## ¿De qué trata el juego?

El robot aparece en una cuadrícula y debe llegar a todas las casillas marcadas con una meta. El jugador mueve al robot haciendo clic en las casillas adyacentes. Una mano animada aparece para sugerir el siguiente movimiento, ayudando a los más pequeños a entender cómo funciona un algoritmo paso a paso.

Cuando el robot recoge todas las metas, ¡aparecen fuegos artificiales y se celebra el logro!

## Requisitos

- Python 3.x
- pygame

```bash
# Windows
pip install pygame

# macOS / Linux
pip3 install pygame
```

## Cómo ejecutar

```bash
python juego_robot.py
```

o en macOS/Linux:

```bash
python3 juego_robot.py
```

## Controles

| Acción | Descripción |
|---|---|
| Clic en casilla adyacente | Mueve el robot un paso |
| Clic sobre el robot | Sigue la sugerencia del dedo |
| `R` | Reiniciar el juego |
| `F` | Activar / desactivar pantalla completa |
| `Q` | Salir |

Los botones **Robot** y **Profe** en la esquina superior izquierda permiten cambiar el personaje que controla el jugador.

## Archivos necesarios

| Archivo | Descripción |
|---|---|
| `juego_robot.py` | Código principal del juego |
| `robot.png` | Imagen del personaje robot |
| `fer.png` | Imagen del personaje "Profe" |
| `cricri.png` | Imagen de la casilla meta |
| `hand.png` | Icono del dedo guía |
| `background.mp3` | Música de fondo |
| `cheer.mp3` | Sonido de celebración |
| `icon_up/down/left/right/play/restart.png` | Íconos de los botones |

## Conceptos que enseña

- **Secuencias de instrucciones**: cada clic es un paso que el robot ejecuta en orden.
- **Algoritmos**: el dedo guía muestra la ruta óptima hacia la meta más cercana.
- **Pensamiento lógico**: el niño aprende a planificar movimientos para alcanzar un objetivo.

## Hecho con

- [Python](https://www.python.org/)
- [pygame](https://www.pygame.org/)
