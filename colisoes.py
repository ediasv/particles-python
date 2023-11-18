import pygame 
from pygame.locals import *
from sys import exit
import random
import numpy

# Coef. de restituição
CR = 0

N_BOLAS = 23

# =================================================================================                    
# Funções auxiliares

def displace(dist, r1, r2):
    return 0.5 * (dist - r1 - r2)

def dist(pos1, pos2):
    return numpy.linalg.norm(numpy.subtract(pos1, pos2))

def temOverlap(b1, b2):
    if (numpy.abs( (b1.p[0] - b2.p[0])**2 + (b1.p[1] - b2.p[1])**2 )) <= (b1.raio + b2.raio)**2:
        return True

def projecao(vec1, vec2):
    return (numpy.multiply(vec2, numpy.divide(numpy.dot(vec1, vec2), numpy.linalg.norm(vec2)**2 )))
# =================================================================================                    

pygame.init()

largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))

font = pygame.font.Font('freesansbold.ttf', 16)

green = (0, 255, 0)
blue = (0, 0, 128)
black = (0, 0, 0)

# =================================================================================
# Classe Bola

class Bola:

    def __init__(self) -> None:
        self.p = [random.randint(40, largura - 40), random.randint(40, altura - 40)]
        self.v = [random.randint(-5, 5), random.randint(-5, 5)]
        self.raio = random.randint(10, 40)
        self.cor = (255, 255, 255)
        self.massa = self.raio
    
    def draw(self):
        pygame.draw.circle(tela, self.cor, (self.p[0], self.p[1]), self.raio)

# =================================================================================
# Criando as bolas, conferindo se elas não se sobrepõem

bolas = []
for i in range(N_BOLAS):
    bolas.append(Bola())

    valido = True
    for j in range(len(bolas)):
        if i != j:
            if temOverlap(bolas[i], bolas[j]):
                valido = False
    while not valido:
        bolas[i] = Bola()
        valido = True
        for j in range(len(bolas)):
            if i != j:
                if temOverlap(bolas[i], bolas[j]):
                    valido = False
        
# =================================================================================

relogio = pygame.time.Clock()

running = True

while running:

    relogio.tick(30)

    tela.fill((0, 0, 0))

    # =================================================================================                    
    # Cálcula a energia cinética eixo-a-eixo e imprime na tela

    ekx = 0
    eky = 0
    ekt = 0
    for bola in bolas:
        ekx += numpy.divide(numpy.multiply(bola.massa, numpy.multiply(bola.v[0], bola.v[0])), 2)
        eky += numpy.divide(numpy.multiply(bola.massa, numpy.multiply(bola.v[1], bola.v[1])), 2)
        ekt += 0.5 * bola.massa * (numpy.linalg.norm(bola.v) ** 2)


    ekx = round(ekx, 2)
    eky = round(eky, 2)
    ekt = round(ekt, 2)

    text = font.render(f'Ekx = {ekx}', True, green, black)
    textRect1 = text.get_rect()
    textRect1.center = (largura // 2, altura // 2 - 20)

    text2 = font.render(f'Eky = {eky}', True, green, black)
    textRect2 = text2.get_rect()
    textRect2.center = (largura // 2, altura // 2 + 20)

    ekt = sum(0.5 * bola.massa * (numpy.linalg.norm(bola.v) ** 2) for bola in bolas)
    ekt = round(ekt, 2)

    text_ekt = font.render(f'Ekt = {ekt}', True, green, black)
    textRect_ekt = text_ekt.get_rect()
    textRect_ekt.center = (largura // 2, altura // 2 + 60)
    tela.blit(text_ekt, textRect_ekt)

    tela.blit(text, textRect1)
    tela.blit(text2, textRect2)

    # =================================================================================                    

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    # =================================================================================                    
    # Desenha bolas e atualiza as posições de acordo com as velocidades

    for i in range(len(bolas)):
        bolas[i].draw()
        bolas[i].p[0] += bolas[i].v[0]
        bolas[i].p[1] += bolas[i].v[1]
    
    # =================================================================================                    
    # Colisão com as bordas

    for i in range(len(bolas)):
        if (bolas[i].p[0] <= bolas[i].raio):
            bolas[i].p[0] = bolas[i].raio
            bolas[i].v[0] *= -1
        elif (bolas[i].p[0] >= largura - bolas[i].raio):
            bolas[i].p[0] = largura - bolas[i].raio
            bolas[i].v[0] *= -1

        if (bolas[i].p[1] <= bolas[i].raio):
            bolas[i].p[1] = bolas[i].raio
            bolas[i].v[1] *= -1
        elif (bolas[i].p[1] >= altura - bolas[i].raio):
            bolas[i].p[1] = altura - bolas[i].raio
            bolas[i].v[1] *= -1
    # =================================================================================                    

        
        for j in range(i+1, len(bolas)):
            if i != j:
                if temOverlap(bolas[i], bolas[j]):

                    # =================================================================================                    
                    # Movendo as bolas pra posição em que elas apenas se tangenciam

                    distancia = dist(bolas[i].p, bolas[j].p)
                    q_displace = displace(distancia, bolas[i].raio, bolas[j].raio)

                    bolas[i].p[0] -= q_displace * (bolas[i].p[0] - bolas[j].p[0]) / distancia
                    bolas[i].p[1] -= q_displace * (bolas[i].p[1] - bolas[j].p[1]) / distancia

                    bolas[j].p[0] += q_displace * (bolas[i].p[0] - bolas[j].p[0]) / distancia
                    bolas[j].p[1] += q_displace * (bolas[i].p[1] - bolas[j].p[1]) / distancia

                    # =================================================================================
                    # Alterando as velocidades

                    normal = numpy.subtract(bolas[i].p, bolas[j].p)

                    v1 = bolas[i].v
                    v1p = projecao(v1, normal)
                    v1t = numpy.subtract(v1, v1p)
                    m1 = bolas[i].massa

                    v2 = bolas[j].v
                    v2p = projecao(v2, normal)
                    v2t = numpy.subtract(v2, v2p)
                    m2 = bolas[j].massa

                    numerator = numpy.add(numpy.multiply(m1, v1), numpy.multiply(m2, v2))
                    denominator = m1 + m2
                    vcm = numpy.divide(numerator, denominator)
                    vcm = projecao(vcm, normal)

                    v1p = numpy.subtract(numpy.multiply(1+CR, vcm), numpy.multiply(CR, v1p))
                    v2p = numpy.subtract(numpy.multiply(1+CR, vcm), numpy.multiply(CR, v2p))

                    v1 = numpy.add(v1p, v1t)
                    v2 = numpy.add(v2p, v2t)

                    bolas[i].v = v1
                    bolas[j].v = v2   
                    # =================================================================================

    pygame.display.update()   
