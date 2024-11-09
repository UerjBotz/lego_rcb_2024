from pybricks.hubs import PrimeHub
from polyfill import Enum

TX_CABECA = 1
TX_BRACO = 2

comando_bt = Enum("comando_bt", ["fecha_garra",
                                 "abre_garra", 
                                 "ver_cor_passageiro", 
                                 "ver_distancias",
                                 #! fazer um enum comandos e outro respostas
                                 "fechei",
                                 "abri",       
                                 "cor_passageiro",     
                                 "distancias"])

