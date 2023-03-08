# -*- coding: utf-8 -*-

# Nicolas, 2021-03-05
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme








# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'mini-quoridorMap'
    game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 100 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nbLignes = game.spriteBuilder.rowsize
    nbCols = game.spriteBuilder.colsize
    assert nbLignes == nbCols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker les murs)
    lMax=nbLignes-2 
    cMin=2
    cMax=nbCols-2
   
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
       
           
    # on localise tous les états initiaux (loc du joueur)
    # positions initiales des joueurs
    initStates = [o.get_rowcol() for o in players]
    ligneObjectif = (initStates[1][0],initStates[0][0]) # chaque joueur cherche a atteindre la ligne ou est place l'autre 
    print(ligneObjectif)
    
    # on localise tous les murs
    # sur le layer ramassable    
    walls = [[],[]]
    walls[0] = [o for o in game.layers['ramassable'] if (o.get_rowcol()[0] == 0 or o.get_rowcol()[0] == 1)]  
    walls[1] = [o for o in game.layers['ramassable'] if (o.get_rowcol()[0] == nbLignes-2 or o.get_rowcol()[0] == nbLignes-1)]  
    allWalls = walls[0]+walls[1]
    nbWalls = len(walls[0])
    assert len(walls[0])==len(walls[1]) # les 2 joueurs doivent avoir le mm nombre de murs
    
    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets murs ou joueurs
    #-------------------------------
    
    def wallStates(walls): 
        # donne la liste des coordonnees dez murs
        return [w.get_rowcol() for w in walls]
    
    def playerStates(players):
        # donne la liste des coordonnees dez joueurs
        return [p.get_rowcol() for p in players]
    
   
    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print("lignes", nbLignes)
    print("colonnes", nbCols)
    print("Trouvé ", nbPlayers, " joueurs avec ", int(nbWalls/2), " murs chacun" )
    print ("Init states:", initStates)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo 
    # 2 joueurs 
    # Joueur 0: place au hasard
    # Joueur 1: A*
    #-------------------------------
    
        
    #-------------------------------
    # On choisit une case objectif au hasard pour chaque joueur
    #-------------------------------
    
    allObjectifs = ([(ligneObjectif[0],i) for i in range(cMin,cMax)],[(ligneObjectif[1],i) for i in range(cMin,cMax)])
    print("Tous les objectifs joueur 0", allObjectifs[0])
    print("Tous les objectifs joueur 1", allObjectifs[1])
    objectifs =  (allObjectifs[0][random.randint(cMin,cMax-3)], allObjectifs[1][random.randint(cMin,cMax-3)])
    print("Objectif joueur 0 choisi au hasard", objectifs[0])
    print("Objectif joueur 1 choisi au hasard", objectifs[1])

    #-------------------------------
    # Fonctions definissant les positions legales et placement de mur aléatoire
    #-------------------------------
    
    def legal_wall_position(pos , player):
        row,col = pos
        # une position legale est dans la carte et pas sur un mur deja pose ni sur un joueur
        # attention: pas de test ici qu'il reste un chemin vers l'objectif
        path = A_star((player + 1) % 2 , True , row , col)
        row1 , col1 = path[-1]
        row2 , col2 = A_star(player , True , row , col)[-1]
        return ((pos not in wallStates(allWalls)) and (pos not in playerStates(players)) and ((row2,col2) == objectifs[player ]) and ((row1,col1) == objectifs[(player + 1) % 2])  and row>lMin and row<lMax-1 and col>=cMin and col<cMax)
        
    def draw_wall_location_strategie_1(player , path_next_player):
        # tire au hasard un couple de position permettant de placer un mur
        i = 0
        while True:
            if (i<len(path_current_player)-1):
                i =+ 1
                loc = path_next_player[i]
            else :
                loc = (random.randint(lMin,lMax),random.randint(cMin,cMax))
            if legal_wall_position(loc , player):  
                inc_pos =[(0,1),(0,-1),(1,0),(-1,0)] 
                random.shuffle(inc_pos)
                for w in inc_pos:
                    loc_bis = (loc[0] + w[0],loc[1]+w[1])
                    if legal_wall_position(loc_bis , player):
                        return(loc,loc_bis)
            
    #-------------------------------
    # Fonctions qui return True si le joueur player lui reste en moins un mur à positionner, False sinon
    #-------------------------------
    def more_walls(player):
        for o in walls[player]:
            if(player == 0 and o.get_rowcol()[0] == 0) or (player == 1 and o.get_rowcol()[0] == nbLignes-2) :
                w1 = o 
                w2 = walls[player][walls[player].index(w1)+ nbCols - 6]
                return w1 , w2
        return None  
   
    
    #-------------------------------
    # Fonction qui applique A*
    #-------------------------------
    def A_star(player , wall = False , col = -1 , row = -1):  
        g =np.ones((nbLignes,nbCols),dtype=bool)  # une matrice remplie par defaut a True  
        for w in wallStates(allWalls):            # on met False quand murs
            g[w]=False
        if wall :
            g[row][col] = True
        for i in range(nbLignes):                 # on exclut aussi les bordures du plateau
            g[0][i]=False
            g[1][i]=False
            g[nbLignes-1][i]=False
            g[nbLignes-2][i]=False
            g[i][0]=False
            g[i][1]=False
            g[i][nbLignes-1]=False
            g[i][nbLignes-2]=False
        p = ProblemeGrid2D(playerStates(players)[player],objectifs[player],g,'manhattan')
        path = probleme.astar(p,verbose=False)
        return path
        
    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
            
    posPlayers = initStates

    END = False
    player = 0
    while(not END):
        print("C'est le tour du joueur ",player)
        w = more_walls(player)
        path_current_player = A_star(player)
        path_next_player = A_star((player+1)%2)
        if( w != None and len(path_current_player) > len(path_next_player) ):
                #placer un mur
                print("création d'un mur")
                ((x1,y1),(x2,y2)) = draw_wall_location_strategie_1(player , path_next_player)
                w[0].set_rowcol(x1,y1)
                w[1].set_rowcol(x2,y2)
                print ("Le joueur ",player," a placé un mur sur les case (",x1,",",y1,") et (",x2,",",y2,") ")
                game.mainiteration()
        else:
            #déplacer le joueur
            # on fait bouger le joueur i jusqu'à son but
            # en suivant le chemin trouve avec A* 
                row,col = A_star(player)[1]
                posPlayers[player]=(row,col)
                players[player].set_rowcol(row,col)
                print ("pos joueur ",player," : ", row,col)
                if (row,col) == objectifs[player]:
                    print("2 le joueur ",player," a atteint son but!")
                    END = True
                    break
                # mise à jour du pleateau de jeu
                game.mainiteration()
        player = (player +1) % 2
            

    pygame.quit()
    
    
    
    
    #-------------------------------
    
        
    
    
   

if __name__ == '__main__':
    main()
    


