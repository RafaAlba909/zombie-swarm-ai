import sys
import pygame as pg
from .menu import main_menu, show_controls
from . import main as game  # tu juego actual

def run():
    while True:
        choice = main_menu()   # "jugar" | "controles" | "salir"
        if choice == "jugar":
            game.main()        # entra a tu loop de juego tal cual
        elif choice == "controles":
            show_controls()    # pantalla de controles y vuelve
        else:  # "salir"
            pg.quit()
            sys.exit()

if __name__ == "__main__":
    run()
