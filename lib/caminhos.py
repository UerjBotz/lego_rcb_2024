from lib.polyfill    import Enum, heappop, heappush
from cores           import cor


tipo_celula = Enum("tipo_celula", ["RUA", "EDIFICIO"])

tipo_parede = Enum("tipo_parede", ["PAREDE",
                                   "ENTRADA",
                                   "ENTRADA_COM_CANO"])

posicao_parede = Enum("posicao_parede", ["N", "S", "L", "O"])

class Edificio:
    def __init__(self, nome, cor, paredes):
        self.nome = nome
        self.cor  = cor
        self.tipo = tipo_celula.EDIFICIO
        self.paredes = paredes
        self.ocupada = True

class Rua:
    def __init__(self):
        self.ocupada = False
        self.tipo = tipo_celula.RUA
    
# celula = Edificio | Rua

def imprime_matriz(matriz):
    """Imprime a matriz de forma alinhada."""
    largura_maxima = 12

    for linha in matriz:
        for celula in linha:
            if celula.tipo == tipo_celula.EDIFICIO:
                texto = celula.nome
            else:
                texto = "OBSTACULO" if celula.ocupada else "RUA"
            print(texto.ljust(largura_maxima), end=" ")
        print()

def coloca_obstaculo(x, y):
    if mapa[x][y].tipo == tipo_celula.EDIFICIO: return #! falhar mais alto

    mapa[x][y].ocupada = True

def tira_obstaculo(x, y):
    if mapa[x][y].tipo == tipo_celula.EDIFICIO: return

    mapa[x][y].ocupada = False

def coloca_passageiro(edificio: Edificio, entrada: str): #ver como faz para escolher a entrada para ocupar
    if edificio.tipo == tipo_celula.RUA: return False
    if entrada not in "NSLO":            return False

    idx = posicao_parede[entrada]
    if edificio.paredes[idx] != tipo_parede.ENTRADA: return False

    if all(map(lambda p: p != tipo_parede.ENTRADA, edificio.paredes)):
        return False #! falhar mais alto

    edificio.paredes[idx] = tipo_parede.ENTRADA_COM_CANO
    return True

bakery = Edificio(
    nome = "BAKERY",
    cor = cor.MARROM,
    paredes = [tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.PAREDE, tipo_parede.ENTRADA]
)
school = Edificio(
    nome = "SCHOOL",
    cor = cor.AZUL,
    paredes = [tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.PAREDE, tipo_parede.ENTRADA]
)
drugstore = Edificio(
    nome = "DRUGSTORE",
    cor = cor.VERMELHO,
    paredes = [tipo_parede.PAREDE, tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.ENTRADA]
)
city_hall = Edificio(
    nome = "CITY HALL",
    cor = cor.VERDE,
    paredes = [tipo_parede.ENTRADA, tipo_parede.ENTRADA, tipo_parede.PAREDE, tipo_parede.PAREDE]
)
museum = Edificio(
    nome = "MUSEUM",
    cor = cor.AZUL,
    paredes = [tipo_parede.ENTRADA, tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.PAREDE]
)
library = Edificio(
    nome = "LIBRARY",
    cor = cor.VERMELHO,
    paredes = [tipo_parede.ENTRADA, tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.PAREDE]
)
park_aberto = lambda: Edificio(
    nome = "PARK",
    cor = cor.VERDE,
    paredes = [tipo_parede.PAREDE, tipo_parede.PAREDE, tipo_parede.ENTRADA, tipo_parede.PAREDE]
)
park_fechado = lambda: Edificio(
    nome = "PARK",
    cor = cor.VERDE,
    paredes = [tipo_parede.PAREDE, tipo_parede.PAREDE, tipo_parede.PAREDE, tipo_parede.PAREDE]
)
#! ver se lambdar os outros também

mapa = [
    [park_aberto(),   Rua(),  bakery,     Rua(),  school,     Rua()],
    [park_fechado(),  Rua(),  Rua(),      Rua(),  Rua(),      Rua()],
    [park_aberto(),   Rua(),  drugstore,  Rua(),  city_hall,  Rua()],
    [park_fechado(),  Rua(),  Rua(),      Rua(),  Rua(),      Rua()],
    [park_aberto(),   Rua(),  museum,     Rua(),  library,    Rua()],
]

## implementação do A* (adaptada de <https://www.geeksforgeeks.org/a-search-algorithm-in-python/>)
class Cell():
    def __init__(self, i_pai=0,
                       j_pai=0,
                       f=float('inf'),
                       g=float('inf'),
                       h=0):
        self.i_pai = i_pai # Parent cell's row index
        self.j_pai = j_pai # Parent cell's column index
        self.f     = f # Total cost of the cell (g + h)
        self.g     = g # Cost from start to this cell
        self.h     = h # Heuristic cost from this cell to destination

direcoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Movimentos: direita, baixo, esquerda, cima

def dist_manhatan(posicao_atual, destino):
    atual_x, atual_y = posicao_atual
    dest_x,  dest_y  = destino
    return abs(atual_x - dest_x) + abs(atual_y - dest_y)

def dentro_dos_limites(matriz, cell):
    x, y = cell
    return 0 <= x < len(matriz) and 0 <= y < len(matriz[0])

def celula_livre(grid, cell):
    row, col = cell
    return not grid[row][col].ocupada

def eh_destino(src, dest): #! acho que dá pra mudar isso pra parar em frente à porta
    row, col = src
    return row == dest[0] and col == dest[1]

def heuristica(src, dest):
    return dist_manhatan(src, dest)

# Trace the path from source to destination
def trace_path(info_celulas, dest):
    print("The Path is ")
    path = []
    row, col = dest

    # Trace the path from destination to source using parent cells
    while not (info_celulas[row][col].i_pai == row and info_celulas[row][col].j_pai == col):
        path.append((row, col))
        temp_row = info_celulas[row][col].i_pai
        temp_col = info_celulas[row][col].j_pai
        row = temp_row
        col = temp_col

    # Add the source cell to the path
    path.append((row, col))
    # Reverse the path to get the path from source to destination
    path.reverse()

    # Print the path
    for i in path:
        print("->", i, end=" ")
    print()
    
    return path

# Implement the A* search algorithm
def a_estrela(grid, src, dest):
    # Check if the source and destination are valid
    if not dentro_dos_limites(grid, src) or not dentro_dos_limites(grid, dest):
        print("Source or destination is invalid")
        return

    # Check if the source and destination are unblocked
    if not celula_livre(grid, src) or not celula_livre(grid, dest):
        print("Source or the destination is blocked")
        return

    # Check if we are already at the destination
    if eh_destino(src, dest):
        print("We are already at the destination")
        return

    ROW = len(grid)
    COL = len(grid[0])

    # Initialize the closed list (visited cells)
    closed_list  = [[False for _ in range(COL)]  for _ in range(ROW)]
    # Initialize the details of each cell
    info_celulas = [[Cell() for _ in range(COL)] for _ in range(ROW)]

    # Initialize the start cell details
    i, j = src
    info_celulas[i][j] = Cell(f=0,
                              g=0,
                              h=0,
                              i_pai=i,
                              j_pai=j)

    # Initialize the open list (cells to be visited) with the start cell
    open_list = []
    heappush(open_list, (0.0, i, j))

    # Initialize the flag for whether destination is found
    achou_dest = False

    # Main loop of A* search algorithm
    while len(open_list) > 0:
        # Pop the cell with the smallest f value from the open list
        p = heappop(open_list)

        # Mark the cell as visited
        i = p[1]
        j = p[2]
        closed_list[i][j] = True

        # For each direction, check the successors
        for dir in direcoes:
            new_i = i + dir[0]
            new_j = j + dir[1]
            new = new_i, new_j

            # If the successor is valid, unblocked, and not visited
            if dentro_dos_limites(grid, new) and celula_livre(grid, new) and not closed_list[new_i][new_j]:
                # If the successor is the destination
                if eh_destino(new, dest):
                    # Set the parent of the destination cell
                    info_celulas[new_i][new_j].i_pai = i
                    info_celulas[new_i][new_j].j_pai = j
                    print("The destination cell is found")
                    # Trace and print the path from source to destination
                    return trace_path(info_celulas, dest)
                    # achou_dest = True
                    # return
                else:
                    # Calculate the new f, g, and h values
                    g_new = info_celulas[i][j].g + 1.0
                    h_new = heuristica(new, dest)
                    f_new = g_new + h_new

                    # If the cell is not in the open list or the new f value is smaller
                    if info_celulas[new_i][new_j].f == float('inf') or info_celulas[new_i][new_j].f > f_new:
                        # Add the cell to the open list
                        heappush(open_list, (f_new, new_i, new_j))
                        # Update the cell details
                        info_celulas[new_i][new_j] = Cell(f = f_new,
                                                          g = g_new,
                                                          h = h_new,
                                                          i_pai = i,
                                                          j_pai = j)

    # If the destination is not found after visiting all cells
    if not achou_dest:
        print("Failed to find the destination cell")

#funcao que recebe lista de posicoes na matriz e transforma em lista de direcoes
def caminho_relativo(caminho_absoluto: list[tuple[int, int]]):
    if caminho_absoluto is None: print("Caminho Errado")

    #movimentos
    direita = (0, 1); baixo = (1, 0); esquerda = (0, -1); cima = (-1, 0)
    direcoes = [(0,0)]

    # print(caminho_absoluto)
    for i in range(1, len(caminho_absoluto)):
        dx = caminho_absoluto[i][0] - caminho_absoluto[i - 1][0]
        dy = caminho_absoluto[i][1] - caminho_absoluto[i - 1][1]

        if dx == 0 and dy == 1:
            direcoes.append(direita)
        elif dx == 1 and dy == 0:
            direcoes.append(baixo)
        elif dx == 0 and dy == -1:
            direcoes.append(esquerda)
        elif dx == -1 and dy == 0:
            direcoes.append(cima)

    return direcoes

#orientação = N | S | L | O
tipo_movimento = Enum("tipo_movimento",
                      ["FRENTE", "DIREITA_FRENTE", "ESQUERDA_FRENTE", "TRAS", "DIREITA", "ESQUERDA"])

def movimento_relativo(relativo, orientacao):
    orientacoes = ["N", "L", "S", "O"]
    idx_orientacao = orientacoes.index(orientacao)
    # print(idx_orientacao)
    nova_orientacao = orientacao
    
    caminho_relativo = relativo.copy()
    caminho_relativo.pop(0)
    
    movimentos = []
    for movimento in caminho_relativo:
        if   movimento == (0, 1):  # direita
            nova_orientacao = "L"
        elif movimento == (1, 0):  # baixo
            nova_orientacao = "S"
        elif movimento == (0, -1):  # esquerda
            nova_orientacao = "O"
        elif movimento == (-1, 0):  # cima
            nova_orientacao = "N"

        nova_idx_orientacao = orientacoes.index(nova_orientacao)
        diferenca = (nova_idx_orientacao - idx_orientacao) % 4

        if   diferenca == 0:
            movimentos.append(tipo_movimento.FRENTE)
        elif diferenca == 1:
            movimentos.append(tipo_movimento.DIREITA_FRENTE)
        elif diferenca == 2:
            movimentos.append(tipo_movimento.TRAS)
        elif diferenca == 3:
            movimentos.append(tipo_movimento.ESQUERDA_FRENTE)

        idx_orientacao = nova_idx_orientacao

    return movimentos



def achar_movimentos(pos_ini, pos_fim, orientacao):
    lin, col = pos_fim
    
    indice = next((i for i, valor in enumerate(mapa[lin][col]) if valor == tipo_parede.ENTRADA), None)
    if indice is None:
        print("Não há entradas disponíveis")
        return []
    
    orientacao_final = None
    if posicao_parede(indice) == posicao_parede.NORTE:
        pos_fim = pos_fim[lin+1][col]
        orientacao_final = "S"
    elif posicao_parede(indice) == posicao_parede.SUL:
        pos_fim = pos_fim[lin-1][col]
        orientacao_final = "N"
    elif posicao_parede(indice) == posicao_parede.LESTE:
        pos_fim = pos_fim[lin][col+1]
        orientacao_final = "O"
    elif posicao_parede(indice) == posicao_parede.OESTE:
        pos_fim = pos_fim[lin][col-1]
        orientacao_final = "L"
    
    
    caminho     = a_estrela(mapa, pos_ini, pos_fim)
    caminho_rel = caminho_relativo(caminho)

    return (movimento_relativo(caminho_rel, orientacao), orientacao_final)


# if __name__ == "__main__":
#     pos_inicial = (1, 1)
#     pos_final   = (4, 3)

#     print("Mapa Original:")
#     imprime_matriz(mapa)
#     coloca_obstaculo(2, 3)
#     print("\nMapa com obstáculo:")
#     imprime_matriz(mapa)
    
#     resultado = a_estrela(mapa, pos_inicial, pos_final)
#     print(resultado)
    
#     print("Movimento relativo: "+ movimento_relativo(caminho_relativo(resultado), "N"))
    