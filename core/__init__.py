if __name__ == "__main__":
    red = Red(30, 30, 3)
    red.insertar_vortice(15, 15, N=1)
    print(red)
    red.evolucionar(10)
    print(f"Energía tras evolución: {red.energia():.3f}")
