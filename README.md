# 🧟‍♂️ Zombie Swarm AI

Juego en **Python + Pygame** donde sobrevives a un enjambre de zombis con **IA de boids** y línea de visión entre obstáculos. Supera niveles llegando al **punto seguro** mientras la dificultad sube.

## ✨ Características
- IA de enjambre (boids) con persecución cooperativa.
- Línea de visión (LOS) bloqueada por coberturas.
- Niveles con **punto seguro** + dificultad progresiva.
- Estética postapocalíptica (campo, senderos, motas…).
- Menú principal y pantalla de controles.

## 🎮 Controles
- **WASD / Flechas** → moverse  
- **Shift** → correr (más visible para los zombis)  
- **+ / -** → añadir / quitar zombis (útil para ajustar dificultad)  
- **H** → mostrar / ocultar ayuda in-game  
- **ESC / Q** → volver al menú  
- **En Game Over**:  
  - **R** → reiniciar **el mismo nivel**  
  - **Enter / Espacio** → volver al **menú**

## 🚀 Arranque rápido

### Windows (CMD/PowerShell)
```bat
git clone https://github.com/RafaAlba909/zombie-swarm-ai.git
cd zombie-swarm-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.launcher
