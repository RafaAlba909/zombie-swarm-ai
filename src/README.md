# Zombie Swarm AI 🧟‍♂️

Juego experimental en **Python + Pygame** con un enjambre de zombis controlados por 
inteligencia artificial tipo *boids*.  
El objetivo es **sobrevivir** y llegar al punto seguro mientras los zombis 
cooperan para cazarte.

## 🎮 Controles
- **WASD / Flechas** → mover
- **Shift** → correr (más visible para zombis)
- **H** → mostrar/ocultar ayuda
- **R** → reiniciar nivel si mueres
- **Enter/Espacio** → volver al menú
- **ESC/Q** → salir

## 🚀 Cómo ejecutar
```bash
git clone https://github.com/TU-USUARIO/zombie-swarm-ai.git
cd zombie-swarm-ai
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.launcher
