# Importamos módulos requeridos
import os
from random import *
import random
import time
#C:\Users\amaru\proyecto-info073-26s2-g7
import pygame

# Estados del juego
ESTADO_INICIO = "inicio"
ESTADO_INSTRUCCIONES = "instrucciones"
ESTADO_JUGANDO = "jugando"
ESTADO_DERROTA = "derrota"
ESTADO_VICTORIA = "victoria"

# Rutas a la carpeta de imágenes de pantallas
DIR_PANTALLAS = os.path.join(os.path.dirname(__file__), "data", "pantallas")

# Se específica el nombre del archivo para cada imagen de pantalla.
# El formato de imagen utilizado puede ser PNG, JPG/JPEG, BMP, o GIF.
PANTALLA_INICIO = "pantalla_inicio.bmp"
PANTALLA_INSTRUCCIONES = "pantalla_instrucciones.bmp"
PANTALLA_VICTORIA = "pantalla_victoria.bmp"
PANTALLA_DERROTA = "pantalla_derrota.bmp"

# Para evitar que el jugador se mueva demasiado rápido
RETRASO = 200

# Códigos de cada elemento del tablero
VACIO = 0
OBSTACULO = 1
JUGADOR = 2
MANZANA = 3
MANZANAS_PARA_GANAR = 0
opciones=["grey","grey10"]
color=random.choice(opciones)

# Tamaño del tablero
# Si se cambian estas constantes, se debe modificar la definición
# del tablero que se encuentra en función reiniciar().
FILAS = 15
COLUMNAS = 15

ANCHO_VENTANA = 1040
ALTO_VENTANA = 800
LADO_TABLERO = 800
ANCHO_PANEL = ANCHO_VENTANA - LADO_TABLERO

BORDE = (
    [(c,0) for c in range(COLUMNAS)]
    + [(c,FILAS-1)for c in range(COLUMNAS)]
    + [(0,f)for f in range(1, FILAS - 1)]
    +[(COLUMNAS-1,f)for f in range(1, FILAS - 1)]
)

def aparecer_aleatorio(tablero, id_elem, incluir_borde=True):
    """
    Coloca un elemento en una casilla vacía aleatoria del tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - id_elem: El número identificador del elemento que queremos colocar.

    Retorna:
        - (columna, fila): Tupla que indica posición en la que se colocó el elemento.
    """

    # Debemos detectar los espacios vacíos, para ello recorremos
    # el tablero y almacenamos tuplas de (columna, fila) las posiciones
    # en las que un elemento "VACIO" (el número 0 en este caso) se encuentre.
    vacios = []

    # Forma vista en clases de recorrer el arreglo multidimensional.
    # Tanto fila como columna son números.
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            # Obtenemos el elemento que se encuentra en esa fila y columna.
            elem_pos = tablero[fila][columna]

            if elem_pos == VACIO:
                # Al utilizar los paréntesis () dentro de la función, lo estaremos
                # añadiendo como una tupla con la estructura (columna, fila).
                vacios.append((columna, fila))
    if not incluir_borde:
        vacios=[pos for pos in vacios if pos not in BORDE]
    # También se puede utilizar comprensión de listas para rellenar el arreglo
    # a la vez que lo recorremos:
    #
    # vacios = [
    #     (columna, fila)
    #     for fila in range(FILAS)
    #     for columna in range(COLUMNAS)
    #     if tablero[fila][columna] == VACIO
    # ]
    
    # Si no hay casillas vacías, retornamos un valor especial.
    if len(vacios) == 0:
        return -1, -1

    # Usando la función random.choice(lista) podremos obtener una tupla
    # aleatoria desde el arreglo "vacios" que definimos anteriormente.
    columna, fila = random.choice(vacios)

    # Finalmente, colocamos el elemento al poner su número en la casilla
    # del tablero correspondiente.
    tablero[fila][columna] = id_elem
    
    return columna, fila


def poblar_tablero(tablero):
    """
    Coloca un obstáculo y la manzana en el tablero.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
    """
    for i in range ( CANT_OBSTACULOS ) :
        aparecer_aleatorio ( tablero , OBSTACULO , incluir_borde = False )
    aparecer_aleatorio(tablero, MANZANA)

def dibujar_panel(screen, fuente, largo):
    panel = pygame . Rect ( LADO_TABLERO , 0 , ANCHO_PANEL , ALTO_VENTANA )
    pygame . draw . rect ( screen , " gray15 ", panel )
    # Margen izquierdo del texto dentro del panel
    x = LADO_TABLERO + 24
    # Titulo
    titulo = fuente . render (" LILA ", True , " purple ")
    screen . blit ( titulo , (x , 30) )
    # Largo actual de la serpiente
    largo_txt = fuente . render ( f" Largo : { largo }", True , " cyan ")
    screen . blit ( largo_txt , (x , 100) )
    # Meta para ganar ( constante LARGO_VICTORIA )
    meta_txt = fuente . render ( f" Objetivo : { MANZANAS_PARA_GANAR-1 }", True , "purple" )
    screen . blit ( meta_txt , (x , 140) )

def refrescar_tablero(screen, tablero, manzanas_comidas, fuente, cuerpo, cabeza_img, cuerpo_img, cola_img, direccion):
    """
    Dibuja el estado actual del tablero en la pantalla.

    Parámetros:
        - screen: La pantalla sobre la cual estamos dibujando.
        - tablero: El tablero con sus posiciones actuales.
    """
    # Rellena la pantalla con el color gris, básicamente pintando
    # por encima de lo que estaba anteriormente.
    screen.fill("grey30")
    # Podemos calcular el tamaño en pixeles que tendrá cada
    # casilla al dividir tanto la altura de la pantalla (screen.get_height())
    # como el ancho (screen.get_width()) por la cantidad de filas y columnas respectivamente.
    # Por ejemplo en este caso alto_elem sería 800 / 15 = 53.3, lo que nos indica que la
    # altura de cada elemento es de 53.3 píxeles.
    alto_elem = LADO_TABLERO / FILAS
    ancho_elem = LADO_TABLERO / COLUMNAS
    # Como el jugador es un círculo, se necesita el radio.
    radio = ancho_elem / 2
    # Posición en eje "y" en unidad de píxeles.
    pos_y = 0

    for i in range(FILAS):
        # Posición en eje "x" en unidad de píxeles.
        pos_x = 0
        for j in range(COLUMNAS):
            if tablero[i][j] == OBSTACULO:
                # Dibuja un rectángulo en la posición (pos_x, pos_y) y que sea
                # de tamaño (ancho_elem, alto_elem) y color negro.
                pygame.draw.rect(
                    screen,
                    "grey",
                    pygame.Rect((pos_x, pos_y), (ancho_elem, alto_elem)),
                )                    
            if tablero[i][j] == MANZANA:
                if manzanas_comidas == MANZANAS_PARA_GANAR-1:
                    #Si solo queda una manzana, la ultima se genera de un nuevo color y tamaño representando un portal de salida
                    Color="purple"
                    tamx=0
                    tamy=0
                else:
                    Color="cyan"
                    tamx=30
                    tamy=30
                pygame.draw.rect(
                    screen,
                    Color,
                    # Acá reducimos el tamaño del rectángulo
                    # para identificarlo más fácilmente
                    pygame.Rect(
                        (pos_x + 10, pos_y + 10),
                        (ancho_elem - tamx, alto_elem - tamy),   
                    ),
                    )
            # Estamos recorriendo los píxeles de la pantalla, por lo que
            # debemos sumar el ancho y altura en pixeles de cada elemento que
            # ya hayamos recorrido para avanzar al siguiente.
            pos_x += ancho_elem
        pos_y += alto_elem
    cola_dib = cola_img
    
    #Posicionar y rotar imagenes
    if len(cuerpo) >= 2:

        cola_actual = cuerpo[-1]
        anterior = cuerpo[-2]

        dx = anterior[0] - cola_actual[0]
        dy = anterior[1] - cola_actual[1]

        if dy == -1:          # Abajo
            cola_dib = cola_img

        elif dy == 1:       # Arriba
            cola_dib = pygame.transform.rotate(cola_img, 180)

        elif dx == -1:        # Derecha
            cola_dib = pygame.transform.rotate(cola_img, 90)

        elif dx == 1:       # Izquierda
            cola_dib = pygame.transform.rotate(cola_img, -90)
            
    if direccion == (0, -1):      # Arriba
        cabeza_dib = cabeza_img

    elif direccion == (1, 0):     # Derecha
        cabeza_dib = pygame.transform.rotate(cabeza_img, -90)

    elif direccion == (0, 1):     # Abajo
        cabeza_dib = pygame.transform.rotate(cabeza_img, 180)

    elif direccion == (-1, 0):    # Izquierda
        cabeza_dib = pygame.transform.rotate(cabeza_img, 90)
    else:
        cabeza_dib = cabeza_img
    # Refresca el contenido que se ve en pantalla.
    for i, (col, fila) in enumerate(cuerpo):
    #Cada que se coma una manzana la cantidad de circulos generados crece en 1
        x = col * ancho_elem
        y = fila * alto_elem

        if i == 0:
            screen.blit(cabeza_dib, (x, y))

        elif i == len(cuerpo) - 1:
            screen.blit(cola_dib, (x, y))

        else:

            anterior = cuerpo[i - 1]
            siguiente = cuerpo[i + 1]

            dx = abs(anterior[0] - siguiente[0])
            dy = abs(anterior[1] - siguiente[1])

            if dy == 2:
                cuerpo_dib = cuerpo_img

            elif dx == 2:
                cuerpo_dib = pygame.transform.rotate(cuerpo_img, 90)

            else:
                cuerpo_dib = cuerpo_img

            screen.blit(cuerpo_dib, (x, y))
            
    dibujar_panel(screen,fuente,len(cuerpo))
    pygame.display.flip()


def cambiar_direccion(keys, direccion_actual, manzanas_comidas):
    """
    Cambia la dirección del jugador.

    Parámetros:
        - keys: Arreglo de teclas presionadas.
        - direccion_actual: La dirección en la que estaba avanzando justo antes de analizar
            si hubo un cambio de dirección.

    Retorna:
        - direccion_actual: La nueva dirección del jugador.
    """

    # Tecla W
    if keys[pygame.K_w]:
        # La tupla nos indica que horizontalmente (columnas) no hará nada (0) y
        # que verticalmente (filas) disminuirá el índice en el tablero (-1).
        return (0, -1)

    # Tecla S
    if keys[pygame.K_s]:
        # En este caso avanzará a través de las filas del tablero.
        return (0, 1)

    # Tecla A
    if keys[pygame.K_a]:
        # Retrocede por las columnas del tablero.
        return (-1, 0)

    # Tecla D
    if keys[pygame.K_d]:
        # Avanza por las columnas del tablero.
        return (1, 0)

    # Si no se presiona ninguna de las teclas anteriores, la dirección
    # será la misma que la anterior.
    return direccion_actual


def avanzar ( tablero , cuerpo , direccion , manzanas_comidas, screen ) :
    """
    Avanza el jugador un paso en la dirección dada.

    Parámetros:
        - tablero: El tablero con sus posiciones actuales.
        - pos_jugador: Tupla con la posición actual (índice con
            estructura (columna, fila)) del jugador en el tablero.
        - direccion: Tupla con la dirección en la que está avanzando actualmente el jugador.

    Retorna:
        - (resultado, nueva_pos_jugador): Retorna el resultado que se obtiene
            al avanzar (derrota, victoria o "ok" (no cambia de pantalla)) y la nueva posición del jugador.
    """
    # Obtenemos los componentes "x" e "y" de cada tupla recibida
    # con información de la dirección y posición del jugador.
    dir_col, dir_fila = direccion
    ind_actual_col, ind_actual_fila = (
        cuerpo[0]  # Tupla (columna, fila) que representa los índices en el tablero.
    )
    ind_nueva_col = ind_actual_col + dir_col
    ind_nueva_fila = ind_actual_fila + dir_fila
    
    #Si la cabeza choca con parte del cuerpo se considera derrota
    nueva_cabeza = (ind_nueva_col, ind_nueva_fila)
    if nueva_cabeza in cuerpo:
        return "derrota", cuerpo, manzanas_comidas
    # Aplicamos la dirección a la posición del jugador.

    # Verificamos que no haya choque con el borde del tablero.
    if not (0 <= ind_nueva_col < COLUMNAS and 0 <= ind_nueva_fila < FILAS):
        return "derrota", cuerpo , manzanas_comidas

    # Obtenemos el elemento que se encuentre en el tablero en la nueva posición del jugador.
    pos_elem = tablero[ind_nueva_fila][ind_nueva_col]

    if pos_elem == OBSTACULO:
        return "derrota", cuerpo, manzanas_comidas

    if pos_elem == MANZANA :
        manzanas_comidas += 1
        tablero[ind_nueva_fila][ind_nueva_col] = VACIO
        #Mover al jugador a la nueva casilla
        nueva_cabeza = (ind_nueva_col, ind_nueva_fila)
        #Se alarga en 1 al jugador
        cuerpo.insert(0, nueva_cabeza)
        # Si llegamos al objetivo , victoria
        if manzanas_comidas >= MANZANAS_PARA_GANAR:
            return "victoria", cuerpo , manzanas_comidas
        # Si no , generar otra manzana y continuar
        aparecer_aleatorio ( tablero , MANZANA )
        return "ok", cuerpo , manzanas_comidas

    # Movimiento normal, si es que no encontramos manzana ni obstáculo.
    nueva_cabeza = (ind_nueva_col, ind_nueva_fila)
    cuerpo.insert(0, nueva_cabeza)
    cuerpo.pop()
    #Se va creando y eliminando circulos en base al movimiento, borrando la parte mas lejana y creando una nueva al otro extremo
    return "ok", cuerpo , manzanas_comidas


def reiniciar():
    """
    Crea un nuevo tablero y estado para una nueva partida.

    Retorna:
        - (tablero, pos_jugador): Tablero nuevo y la nueva posición aleatoria del jugador.
            pos_jugador corresponda a una tupla (columna, fila) donde columna y fila son índices
            de matriz tablero.
    """

    # Si se modifica constante FILAS o COLUMNAS al inicio, también
    # se debe modificar este arreglo de tablero con los valores correspondientes.
    # Esto puede ser mejorado usando dos bucles "for" anidados o comprensión de listas.
    global MANZANAS_PARA_GANAR
    global CANT_OBSTACULOS
    
    CANT_OBSTACULOS= random.randint(10,30)

    MANZANAS_PARA_GANAR = random.randint(5, 10)
    
    tablero = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    # Usando dos bucles "for" anidados se haría de la siguiente manera:
    # tablero = []
    # for _ in range(FILAS):
    #     fila_tablero = []
    #
    #     for _ in range(COLUMNAS):
    #         fila_tablero.append(VACIO)
    #
    #     tablero.append(fila_tablero)
    # Otra manera usando comprensión de listas:
    # tablero = [[VACIO] * COLUMNAS for _ in range(FILAS)]
    # El _ en el "for" indica que no usamos la variable con la que iteramos.

    poblar_tablero(tablero)

    # Colocamos al jugador en una posición aleatoria.
    pos_jugador = aparecer_aleatorio(tablero, VACIO)
    #Se adapta a la composicion de "cuerpo"
    cuerpo = [pos_jugador]
    
    return tablero, cuerpo


def mostrar_pantalla(screen, nombre_archivo):
    """
    Carga una imagen y la muestra escalada a la ventana.

    Parámetros:
        - screen: La pantalla donde colocaremos la imagen.
        - nombre_archivo: El nombre del archivo de la imagen.
    """

    ruta = os.path.join(DIR_PANTALLAS, nombre_archivo)

    try:
        imagen = pygame.image.load(ruta)
        imagen = pygame.transform.scale(imagen, screen.get_size())

        # Dibujamos la imagen en la pantalla en la coordenada (0, 0).
        screen.blit(imagen, (0, 0))

        # Refrescamos pantalla.
        pygame.display.flip()
    except FileNotFoundError:
        # Fallback de seguridad en caso de que las imágenes no existan aún
        screen.fill("black")
        pygame.display.flip()
        print(f"Advertencia: No se encontró la imagen {ruta}")


def main():
    pygame.init()
    pygame.mixer.init() 
    DIR_SOUNDS = os.path.join(os.path.dirname(__file__), "sounds")

    pygame.mixer.music.load(
        os.path.join(DIR_SOUNDS, "fondo.mp3.mp3")
    ) 
    pygame.mixer.music.play(-1)


    # Establecemos la resolución de la pantalla.
    screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))

    # Establecemos el título de la ventana.
    pygame.display.set_caption("Snake")
    cabeza_img = pygame.image.load("C:/Users/amaru/G7/sprites/cabeza.png").convert_alpha()
    cuerpo_img = pygame.image.load("C:/Users/amaru/G7/sprites/cuerpo.png").convert_alpha()
    cola_img = pygame.image.load("C:/Users/amaru/G7/sprites/cola.png").convert_alpha()
    
    tam = (LADO_TABLERO // COLUMNAS, LADO_TABLERO // FILAS)

    cabeza_img = pygame.transform.scale(cabeza_img, tam)
    cuerpo_img = pygame.transform.scale(cuerpo_img, tam)
    cola_img = pygame.transform.scale(cola_img, tam)
    fuente = pygame.font.Font(None, 36)

    running = True

    estado = ESTADO_INICIO
    tablero = []
    pos_jugador = (0, 0)
    direccion = (0, 0)
    tiempo_ultimo_mov = 0
    manzanas_comidas = 0

    mostrar_pantalla(screen, PANTALLA_INICIO)

    # Este es el bucle principal del juego, todo lo que sucede en el juego
    # está aquí.
    while running:
        # Se analizan los eventos del bucle actual.
        for evento in pygame.event.get():
            # Si es que se quiere cerrar la ventana.
            if evento.type == pygame.QUIT:
                running = False

            # Si es que se presiona alguna tecla.
            if evento.type == pygame.KEYDOWN:
                if estado == ESTADO_INICIO:
                    if evento.key == pygame.K_SPACE:
                        tablero, cuerpo = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        # Obtiene tiempo en milisegundos
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas_comidas, fuente, cuerpo, cabeza_img, cuerpo_img, cola_img, direccion)
                    elif evento.key == pygame.K_i:
                        estado = ESTADO_INSTRUCCIONES
                        mostrar_pantalla(screen, PANTALLA_INSTRUCCIONES)

                elif estado == ESTADO_INSTRUCCIONES:
                    estado = ESTADO_INICIO
                    mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado in (ESTADO_DERROTA, ESTADO_VICTORIA):
                    if evento.key == pygame.K_r:
                        tablero, cuerpo = reiniciar()
                        manzanas_comidas = 0
                        direccion = (0, 0)
                        tiempo_ultimo_mov = pygame.time.get_ticks()
                        estado = ESTADO_JUGANDO
                        refrescar_tablero(screen, tablero, manzanas_comidas, fuente, cuerpo, cabeza_img, cuerpo_img, cola_img, direccion)

                    if evento.key == pygame.K_ESCAPE:
                        estado = ESTADO_INICIO
                        mostrar_pantalla(screen, PANTALLA_INICIO)

                elif estado == ESTADO_JUGANDO:
                    direccion = cambiar_direccion(pygame.key.get_pressed(), direccion, manzanas_comidas)

        if estado == ESTADO_JUGANDO:
            tiempo_actual = pygame.time.get_ticks()  # En milisegundos

            # La variable RETRASO hace que si no han pasado esa cantidad de ticks,
            # entonces no se avanzará en el tablero.
            if direccion != (0, 0) and tiempo_actual - tiempo_ultimo_mov >= RETRASO:
                resultado , cuerpo , manzanas_comidas = avanzar(
                    tablero , cuerpo , direccion , manzanas_comidas, screen
                )
                if resultado == "derrota":
                    estado = ESTADO_DERROTA
                    mostrar_pantalla(screen, PANTALLA_DERROTA)
                elif resultado == "victoria":
                    estado = ESTADO_VICTORIA
                    mostrar_pantalla(screen, PANTALLA_VICTORIA)
                else:
                    tiempo_ultimo_mov = tiempo_actual
                    refrescar_tablero(screen, tablero, manzanas_comidas, fuente, cuerpo, cabeza_img, cuerpo_img, cola_img, direccion)

    pygame.quit()


if __name__ == "__main__":
    main()
