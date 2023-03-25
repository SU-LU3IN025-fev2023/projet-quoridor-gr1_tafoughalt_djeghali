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
import math
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
# Définir des constantes comme des facteurs pour la fonction d'évaluation
# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ----
A = 0.75
B = 0.15
C = 0.5
D = 0.5





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
    #print ("Iterations: ")
    #print (iterations)

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
        # donne la liste des coordonnees des murs
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
    
    def legal_wall_position(pos , player , pos2 = None):

        # une position legale est dans la carte et pas sur un mur deja pose ni sur un joueur
        # attention: pas de test ici qu'il reste un chemin vers l'objectif
        
        path = A_star((player + 1) % 2 , True , pos , pos2)
        row1 , col1 = path[-1]
        row2 , col2 = A_star(player , True , pos , pos2)[-1]
        if pos2 != None :
            pos = pos2
        row , col = pos
        return ((pos not in wallStates(allWalls)) and (pos not in playerStates(players)) and ((row2,col2) == objectifs[player ]) and ((row1,col1) == objectifs[(player + 1) % 2])  and row>lMin and row<lMax-1 and col>=cMin and col<cMax)
# Poser la question aiu pourquoi mettre row > lMax-1 et non pas >= 
    def draw_random_wall_location(player):
        # tire au hasard un couple de position permettant de placer un mur
        while True:
            random_loc  = (random.randint(lMin,lMax),random.randint(cMin,cMax))
            if legal_wall_position(random_loc , player):  
                inc_pos =[(0,1),(0,-1),(1,0),(-1,0)] 
                random.shuffle(inc_pos)
                for w in inc_pos:
                    random_loc_bis = (random_loc[0] + w[0],random_loc[1]+w[1])
                    if legal_wall_position(random_loc,  player , random_loc_bis ):
                        return(random_loc,random_loc_bis)
                    
                    
    def draw_wall_location_strategie_1(player , path_next_player):
        # tire au hasard un couple de position permettant de placer un mur
        i = 0
        while True:
            if (i<len(path_next_player)-1):
                i += 1
                loc = path_next_player[i]
                print("Loc :",loc,"      i:",i)

            else :
                loc = (random.randint(lMin,lMax),random.randint(cMin,cMax))
            print(loc , " ", legal_wall_position(loc , player))
            if legal_wall_position(loc , player):  
                inc_pos =[(0,1),(0,-1),(1,0),(-1,0)] 
                random.shuffle(inc_pos)
                for w in inc_pos:
                    loc_bis = (loc[0] + w[0],loc[1]+w[1])
                    if legal_wall_position(loc,  player , loc_bis ):
                        return(loc,loc_bis)
     
    def draw_wall_location_strategie_2(player , path_next_player):
        # tire au hasard un couple de position permettant de placer un mur
        i = 1
        while True and i<len(path_next_player):
            loc = path_next_player[i]
            print(loc , " ", legal_wall_position(loc , player))
            if legal_wall_position(loc , player):  
                inc_pos =[(0,1),(0,-1),(1,0),(-1,0)] 
                random.shuffle(inc_pos)
                for w in inc_pos:
                    loc_bis = (loc[0] + w[0],loc[1]+w[1])
                    if legal_wall_position(loc,  player , loc_bis ):
                        return(loc,loc_bis)
            i+=1
        return None
          
    #-------------------------------
    # Fonctions qui return las coordonées d'un mûr si le joueur player lui reste en moins un mur à positionner, None sinon
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
    def A_star(player , wall = False , pos=None , pos2=None):  
        g =np.ones((nbLignes,nbCols),dtype=bool)  # une matrice remplie par defaut a True  
        for w in wallStates(allWalls):            # on met False quand murs
            g[w]=False
        if wall :
            g[pos] = False
            if pos2 != None :
                g[pos2] = False
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
    #------------------------------------------------------------------#
    #                       Fonctions auxiliaires                      #
    #------------------------------------------------------------------#
    def nb_walls(player):
        """
            @param player: l'indice d'un joueur
            @return : le nombre de mûrs qu'ils lui restent
        """
        nb = 0
        for o in walls[player]:
            if(player == 0 and o.get_rowcol()[0] == 0):
                nb += 1
            elif (player == 1 and o.get_rowcol()[0] == nbLignes-2) :
                nb += 1
        return nb

    def near_walls(player):
        nb = 0
        row , col = players[player].get_rowcol()
        walls_pos = wallStates(allWalls)
        if (row-1,col) in walls_pos :
            if (row-1,col-1) in walls_pos:
                nb+=1
            if (row-1,col+1) in walls_pos:
                 nb+=1

        if (row+1,col) in walls_pos :
            if (row+1,col-1) in walls_pos:
                nb+=1
            if (row+1,col+1) in walls_pos:
                 nb+=1
        
        if (row,col-1) in walls_pos :
            if (row-1,col-1) in walls_pos:
                nb+=1
            if (row+1,col-1) in walls_pos:
                 nb+=1
        
        if (row,col+1) in walls_pos :
            if (row-1,col+1) in walls_pos:
                nb+=1
            if (row+1,col+1) in walls_pos:
                 nb+=1
        
        return nb
    
    def possible_moves(player):
        l = []
        row , col = players[player].get_rowcol()
        inc_pos =[(0,-1),(0,1),(-1,0),(1,0)] 
        walls_pos = wallStates(allWalls)
        for w in inc_pos :
            if not ((row + w[0] , col + w[1]) in walls_pos) :
                l.append((row + w[0] , col + w[1]))
        return l
    
    
    def possible_wall_placements(player):
        """
            @param player: l'indice d'un joueur
            @return : une liste de couple , contenant les postions des mur pouvant
            etre placés a proximité du joueur , ainsi qu'une direction ,
            EX : l[0] = ((2,5),(0,1)) un mur pourrait etre place de maniere horizontale
            à partir de la case (2,5) => Ses coordonnées seront donc : (2,5),(2,6) 
        """
        nb = 0
        row , col = players[player].get_rowcol()
        l = []
        inc_pos =[(0,1),(0,-1),(1,0),(-1,0)]
        for pos in inc_pos:
            loc = (pos[0] + row,pos[1]+col)
            if legal_wall_position(loc, player):
                directions =[((0,1),"RIGHT"),((0,-1),"LEFT"),((1,0),"DOWN"),((-1,0),"UP")]
                for dir in directions:
                    loc_bis = (loc[0] + dir[0][0],loc[1]+dir[0][1])
                    if legal_wall_position(loc,  player,loc_bis):
                        l.append((loc,dir[0]))
        return l

    def evaluation_function(player):
        """
            @param player: l'indice du joueur courant
            @return : la valeur de la fonction d'évaluation
        """
        if players[player].get_rowcol() == objectifs[player] :
            #le joueur courant est arrivée à son objectif
            return math.inf
        else:
            if players[(player+1)%2].get_rowcol() == objectifs[(player+1)%2] :
                #le joueur adversaire est arrivée à son objectif
                return -math.inf
            else :
                diff_paths = A_star((player+1)%2) - A_star(player)
                diff_nbWalls = nb_walls(player) - nb_walls((player+1)%2)
                diff_nearWalls = near_walls((player+1)%2) - near_walls(player)
                diff_possibleMoves = len(possible_moves(player)) - len(possible_moves((player+1)%2))
                return A*diff_paths + B*diff_nbWalls + C*diff_nearWalls + D*diff_possibleMoves


    def choose_action(player):
        maxCost = -1
        row,col = -1,-1
        direction = None
        action = ""
        depth = 4
        possibleMoves = possible_moves(player)
        for pos in possibleMoves:
            sauv_pos = players[player].get_rowcol()
            players[player].set_rowcol(pos)
            posPlayers[player]= pos
            cost = MinMax(player,depth)
            players[player].set_rowcol(sauv_pos)
            posPlayers[player]= sauv_pos
            
            if maxCost < cost :
                row , col = pos[0] , pos[1]
                maxCost = cost
                action = "MOVE"
        
        if(nb_walls(player))>0 :
            
            possibleWallsPosition = possible_wall_placements(player)
            for pos,dir in possibleWallsPosition :
                w1 , w2 = more_walls(player)
                sauv_w = w1.get_rowcol() , w2.get_rowcol()
                w1.set_rowcol(pos[0] , pos[1])
                w2.set_rowcol(pos[0]+dir[0] ,pos[1]+dir[1])
                cost = MinMax(player,depth)
                w1.set_rowcol(sauv_w[0])
                w2.set_rowcol(sauv_w[1])
                
                if maxCost < cost :
                    row , col = pos[0] , pos[1]
                    direction = dir
                    maxCost = cost
                    action = "PLACE_WALL"
                    
        return action , row , col , direction

    def MinMax (player, currentPos, posWall, directionWall , depth):
        if depth ==0 : 
            return evaluation_function(player)
        else :
            if (depth % 2 == 0):
                max_ev = -math.inf
                possibleMoves = possible_moves(player)
                for pos in possibleMoves:
                    sauv_pos = players[player].get_rowcol()
                    players[player].set_rowcol(pos)
                    posPlayers[player]= pos
                    eval = MinMax(player,depth-1)
                    players[player].set_rowcol(sauv_pos)
                    posPlayers[player]= sauv_pos
                    max_ev = max(eval, max_ev)

                
                if(nb_walls(player))>0 :
                    possibleWallsPosition = possible_wall_placements(player)
                    for pos,dir in possibleWallsPosition :
                        w1 , w2 = more_walls(player)
                        sauv_w = w1.get_rowcol() , w2.get_rowcol()
                        w1.set_rowcol(pos[0] , pos[1])
                        w2.set_rowcol(pos[0]+dir[0] ,pos[1]+dir[1])
                        eval = MinMax(player,depth-1)
                        w1.set_rowcol(sauv_w[0])
                        w2.set_rowcol(sauv_w[1])
                        max_ev = max(eval, max_ev)             
                return max_ev
            else:
                min_ev = math.inf
                possibleMoves = possible_moves(player)
                for pos in possibleMoves:
                    sauv_pos = players[player].get_rowcol()
                    players[player].set_rowcol(pos)
                    posPlayers[player]= pos
                    eval = MinMax(player, pos)
                    players[player].set_rowcol(sauv_pos)
                    posPlayers[player]= sauv_pos
                    min_ev = min(eval, min_ev)
                
                if(nb_walls(player))>0 :
                    possibleWallsPosition = possible_wall_placements(player)
                    for pos,dir in possibleWallsPosition :
                        w1 , w2 = more_walls(player)
                        sauv_w = w1.get_rowcol() , w2.get_rowcol()
                        w1.set_rowcol(pos[0] , pos[1])
                        w2.set_rowcol(pos[0]+dir[0] ,pos[1]+dir[1])
                        eval = MinMax(player, None,pos, dir,depth-1)
                        w1.set_rowcol(sauv_w[0])
                        w2.set_rowcol(sauv_w[1])
                        min_ev = min(eval, min_ev)                  
                    
                return min_ev



    #-------------------------------
    # Stratégie aléatoire
    #-------------------------------
    def aleatoire ( joueur ) :
        print("C'est le tour du joueur ",player)
        w = more_walls(player)
        if( w != None):
            action = random.randint(0,1)
            if action == 0 :
                #placer un mur
                print("création d'un mur")
                ((x1,y1),(x2,y2)) = draw_random_wall_location(player)
                w[0].set_rowcol(x1,y1)
                w[1].set_rowcol(x2,y2)
                print ("Le joueur ",player," a placé un mur sur les case (",x1,",",y1,") et (",x2,",",y2,") ")
                game.mainiteration()
            else:
                #déplacer le joueur
                #for i in range(iterations):
                
                # on fait bouger le joueur i jusqu'à son but
                # en suivant le chemin trouve avec A* 
                    row,col = A_star(player)[1]
                    posPlayers[player]=(row,col)
                    players[player].set_rowcol(row,col)
                    print ("1 pos joueur ",player," : ", row,col)
                    if (row,col) == objectifs[player]:
                        print("le joueur ",player," a atteint son but!")
                        return True
                    # mise à jour du pleateau de jeu
                    game.mainiteration()

        else:
            #déplacer le joueur
            #for i in range(iterations):
            
            # on fait bouger le joueur i jusqu'à son but
            # en suivant le chemin trouve avec A* 
                row,col = A_star(player)[1]
                posPlayers[player]=(row,col)
                players[player].set_rowcol(row,col)
                print ("pos joueur ",player," : ", row,col)
                if (row,col) == objectifs[player]:
                    print("2 le joueur ",player," a atteint son but!")
                    return True
                # mise à jour du pleateau de jeu
                game.mainiteration() 
        return False
    
    #-------------------------------
    # Stratégie 2
    #-------------------------------
    def strategie_1( player ):
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
                return True
            # mise à jour du pleateau de jeu
            game.mainiteration()
    #-------------------------------
    # Stratégie 2
    #-------------------------------
    def strategie_2( player ):
        print("C'est le tour du joueur ",player)
        w = more_walls(player)
        path_current_player = A_star(player)
        path_next_player = A_star((player+1)%2)
        if( w != None and len(path_current_player) > len(path_next_player) and draw_wall_location_strategie_2(player , path_next_player) != None ):
                #placer un mur
                print("création d'un mur")
                ((x1,y1),(x2,y2)) = draw_wall_location_strategie_2(player , path_next_player)
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
                    print("Le joueur ",player," a atteint son but!")
                    return True
                # mise à jour du pleateau de jeu
                game.mainiteration()
    #-------------------------------
    # Stratégie alpha_beta
    #-------------------------------
    def alpha_beta( player ):
        return 0
    

    
    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
            
    posPlayers = initStates

    END = False
    player = 0
    while(not END):
        if player == 0:
            if (strategie_2(player)):
                break
        else :
            if (strategie_1(player)):
                break
        player = (player +1) % 2
            
    game.mainiteration()
    pygame.quit()
    
    
    
    
    #-------------------------------
    
        
    
    
   

if __name__ == '__main__':
    main()
 