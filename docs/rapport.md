# Rapport de projet

## Groupe
* Anyes TAFOUGHALT
* Racha Nadine DJEGHALI

# projet-quoridor
    Projet IA et Jeux 2022-2023, L3 Sorbonne Université

# Sujet (Poroposé) :

Il nous est demandé dans ce projet d'implémenter différentes stratégies se basant sur differents algorithmes notamment  **MinMax** et **AlphaBeta** en plus des éventuelles stratégies auxquelles on aurait déja pensé.

## Principe du jeu :
Chaque joueur chercheà être le premier à traverser le terrain. Chaque joueur jour à tour de rôle. Les coups possibles sont:

* Le déplacement de son joueur,
* le dépôt d'un mur de 2 cases sur le plateau.

Les règles de déplacement sont les suivantes:

* Il est possible de se déplacer de une case, dans toutes les directions sauf les diagonales. On suppose ici que les joueurs ne se bloquent pas entre eux, et qu'ils peuvent éventuellement être sur la même case à un moment donné.

Les règles de placement sont les suivantes:
* Les murs sont constitués de 2 "briques" (2 cases) qui doivent posés côte-à-côte horizontalement ou verticalement
* les murs sont ici posés sur les cases (et non entre elles comme c'est le cas dans le jeu de Quridor classique),
* Il est interdit de poser des murs sur les lignes où sont placés initialement les joueurs
* Il est interdit de déposer un mur à un endroit qui fermerait tout chemin d'un des autres joueurs vers ses objectifs.

## Description des choix importants d'implémentation: 

Pour ce faire :     
    Nous avons commencé par implementer des stratégies plutôt naives (hormis l'Aleatoire) qu'on a par la suite developpées.
    On a decider d'utilisé la meme strategie tout au long d'un partie pour chaque joueur
1.  Nous avons pensé dans un premier lieu à une stratégie qui aiderai le joueur a choisir entre se déplacer et placer un mur en se basant uniquement sur les distances qui separent les joueurs de leurs objectifs.(**strategie 1**)

2.  On s'est ensuite intéressé au reel intêret de placer un mur. En effet, on s'est demandé si le fait de se reposer uniquement sur la distance des joueurs par rapport à leurs objectifs était suffisante. Afin d'ameliorer cela nous verifions d'abord si le depot du mur bloquait reelement notre adversaire.(**strategie 2**)

3. Deux  de nos autres stratégies se sont également basées sur des algorithmes trés connus qui nous ont été présentés en cours :
    * MinMax (**strategie3**)
    * Alpha Beta(**strategie4**)
    
*  => Nous avons fait le choix de les utiliser afin de bien évaluer les consequence ou encore le gain du joueur  optant pour une action donnée . Ces approches sont considérées comme etant plus performantes que les autres car elles aident le joueur non seulement à choisir quelle action effectuer mais comment bien la realiser (En choisiant une meilleure position de déplacement par exemple ou encore en selectionnant un des endroits les plus favorable au blocage de l'adversaire) .

### Fonctions auxiliaires :
Afin d'implementer nos différentes strategies nous avons utilisées quelques fonctions dont la description est données si dessous :
 * `draw_random_wall_location(joueur)` : 
    * Utilisé par la stratégie **aleatoire** . 
    * prends en parametre de joueur courant .
    * Tire au hasard une position ou le joueur pourrait placer un mur sans probleme (sans bloqué personnes definitivement ).
 * `draw_wall_location_strategie_1(joueur,Chemin_de_ladversaire)` : 
    * Utilisé par la stratégie **stategie1** . 
    * prends en parametre de joueur courant ainsi que le chemin retourné par A* pour l'adverseve qui le menera vers son objectif .
    * Essaye de trouver une position sur laquelle poser un mur, d'abord sur le chemin de l'adversaire(Afin de lui couper la route ) ensuite si cela n'est pas possible sur une autre position tirée aleatoirement (Elle retourne donc tout le temps une position possible).
 * `draw_wall_location_strategie_2(joueur,Chemin_de_ladversaire)` : 
    * Utilisé par la stratégie **stategie2** . 
    * prends en parametre de joueur courant ainsi que le chemin retourné par A* pour l'adverseve qui le menera vers son objectif .
    * Essaye de trouver une position sur laquelle placer un mur uniquement sur le chemin de l'adversaire pour cette fois-ci(Afin de lui couper la route ) sinon retourne *None*.
 * `choose_action(joueur,minMax,depth)` :
    * Utilisé par les stratégies **stategie2** et **stategie3** . 
    * prends en parametre de joueur, un booleen minMax mis a *True* lorsqu'on souhaite appeller l'algo minMa ou alphaBeta lorque ce dernier est a *False*.
    * Cette fonction nous renvoie la meilleure maniere de proceder :
        * "MOVE" accompagné des coordonnées de la case à laquelle le joueur va se deplacer .
        * "PLACE_WALL" accompagné des coordonnées des coordonnées des 2 cases ou il faut placer le mur.
    * Cette fonction appelle les algorithme minMax ou alphaBeta selon la valeur du boolean et essaye a chaque fois de maximiser le cout retourner par ces 2 algorithmes (L'heuristique estimée pour une action donnée ).
 * `evaluation_function` :
    * C'est l'une des fonctions les plus **importantes**, celle ci renvoie une valeur representation le score ou le gain que peut rapporter une suite d'actions, Cette methode est appellée par les algorithmes alphaBeta et minMax pour evaluer le gain(dans un situation precise) du joueur a une profondeur donnée aprés avoir efféctué quelques actions données (Ou encore pour estimer a quel point un coup pourrait faire gagner le joueur)
    * Pour ce score on a choisi de maximiser selon des facteur qu'on pourrait ajuster :
        * La difference de taille entre le chemin de l'adversaire vers son objectis et le notre : dans le bus de tout le ton essayer de le garder plus loin que son objectifs , en nous rapprochons du notre.
        * Le nombre de mur qu'on possede par rapport a l'autre joueur, afin de pouvoir surtout les utiliser unpeu au milieu du jeu, et e passer les deposer dés le depart (idée que nous avons estimée plus intelligente).
        * Le nombre de nos deplacements possibles en minimisant ceux du joueur adverse : dans le but d'essayer de le bloquer le maximum possible tout en evitant de se retrouver entouré de plusieurs obstacles aussi.
    * Si le joueur arrive a son objectif on retourne un score (le plus elevé)
    * Si le joueur adverse arrive a son objectif on retourne le pire score(le plus faible)
 * `minMax` :
    * Cette implementation se base sur la vraie version du minMax algoroithm ,L'algo prend en parametre une profondeur qu'on initialise a  1 :
        * Si on atteint la profoneur specifiée on retourne un score en appellant `evaluation_function`.

        * Si celle ci n'est pas mutliple de 2 on pocede pour le joueur MIN (adversaire donc):
            * suppose dans un premier lieu que le joueur adverse se deplace a la premiere case retournée par A* et evoque ensuite un appel recursif MinMax sur une profondeur incrementé.
            Et on prend le min entre notre score initiale et le score retourné par l'appel recursif , le joueur min ici essaye et fait de son mieux pour minimiser le gain.
            * Ensuite elle verifie s'il reste au joueur adverse des murs a placer :
                * Si c'est le cas, elle appelle `draw_wall_location_strategie_2` pour lui retourner une postion sur le chemin de du joueur courant et le place , et fait ensuite appelle recurssif a minMax sur une profondeur incrementée: 
                    * Si le score est plus petit que celui qu'on a precedemment enregistré on sauvegarde l'action (postions du mur dans ce cas)
            * On retourne la valeur minimale enregistrée.
        * Sinon :
            * suppose dans un premier lieu que le joueur courant se deplace a la premiere case retournée par A* et evoque ensuite un appel recursif MinMax sur une profondeur incrementée.
            Et on prend le max entre notre score initiale et le score retourné par l'appel recursif , le joueur max ici essaye de maximiser son propre gain.
            * Ensuite elle verifie s'il reste au joueur courent des murs a placer :
                * Si c'est le cas, elle appelle `draw_wall_location_strategie_2` pour lui retourner une postion sur le chemin de du joueur adverse et le place , et fait ensuite appel recursif a minMax sur une profondeur incrementée: 
                    * Si le score est plus grand que celui qu'on a precedemment enregistré on sauvegarde l'action (postions du mur dans ce cas)
                * On retourne la valeur maximale enregistrée.
* `alpha_beta`:
    * Cette implementation se base sur la vraie version de AlphaBeta algoroithm ,L'algo prend en parametre une profondeur qu'on initialise a  1 , ainsi que 2 valeurs alpha et beta :
        * Si on atteint la profoneur specifiée on retourne un score en appellant `evaluation_function`.

        * Si celle ci n'est pas mutliple de 2 on pocede pour le joueur MIN (adversaire donc):
            * suppose dans un premier lieu que le joueur adverse se deplace a la premiere case retournée par A* et evoque ensuite un appel recursif MinMax sur une profondeur incrementé.
                * Si la valeur retourner par l'appel recursif est plus petite ou egale a alpha on l'a renvoie .
                * Sinon on sauvegarde dans beta le min entre beta et le score retourné par l'appel recursif , le joueur min ici essaye et fait de son mieux pour minimiser le gain.
            * Ensuite elle verifie s'il reste au joueur adverse des murs a placer :
                * Si c'est le cas, elle appelle `draw_wall_location_strategie_2` pour lui retourner une postion sur le chemin de du joueur courant et le place , et fait ensuite appelle recurssif a minMax sur une profondeur incrementée: 
                    * Si la valeur retourner par l'appel recursif est plus petite ou egale a alpha on l'a renvoie .
                    *  Sinon on sauvegarde dans beta le min entre beta et le score retourné par l'appel recursif , le joueur min ici essaye et fait de son mieux pour minimiser le gain.
        * Sinon :
            * suppose dans un premier lieu que le joueur courant se deplace a la premiere case retournée par A* et evoque ensuite un appel recursif MinMax sur une profondeur incrementée.
                * Si la valeur retourner par l'appel recursif est plus grande ou egale a beta on l'a renvoie .
                * Sinon on sauvegarde dans alpha le max entre alpha et le score retourné par l'appel recursif , le joueur max ici essaye de maximiser son propre gain.
            * Ensuite elle verifie s'il reste au joueur courent des murs a placer :
                * Si c'est le cas, elle appelle `draw_wall_location_strategie_2` pour lui retourner une postion sur le chemin de du joueur adverse et le place , et fait ensuite appel recursif a minMax sur une profondeur incrementée: 
                    * Si la valeur retourner par l'appel recursif est plus grande ou egale a beta on l'a renvoie .
                    * Sinon on sauvegarde dans alpha le max entre  alpha et le score retourné par l'appel recursif , le joueur max ici essaye de maximiser son propre gain.
                * On retourne la valeur maximale enregistrée.
## Description des stratégies proposées: 

* 1. Aléatoire :
     * Dans cette stratégie chacun des deux joueur verifie s'il poscede encore des mur a placer , il tire une valeur aleatoire selon laquelle il decide soit de placer un mur ou plutot de se deplacer :
        * Pour placer un obstacle  = > il le fait de maniere totalemnt aleatoire.
    Sinon  il se deplace a la premiére case du chemin retourné par A*.
* 2. Stratégie_1 :
     * Ici , pour choisir entre se deplacer ou poser un mur , le joueur compare la longeur de son chemin vers son objectif(retourné par A*) a celui de son adversaire :
        * S'il est plus loin :
            * Il **decide** de placer un mur a tout prix, en appellant `draw_wall_location_strategie_1` qui lui retournera une position soit sur le chemin de son adversaire ou dans un endroit quelconque sur le plateau .
        * Sinon il se deplace à la premiere case du chemin vert sa victoire retourné par A*.
* 3. Stratégie_2 :
     * Cette stratégie est une amélioration de la precedente, le joueur compare la longeur de son chemin vers son objectif(retourné par A*) a celui de son adversaire :
        * S'il est plus loin :
            * Il **essaye** de placer un mur sur le chemin de son adversaire en evoquant `draw_wall_location_strategie_2` qui lui retournera une position sur le chemin de son adversaire ou None.
        * Sinon s'il est plus loin mais qu'il n'arrive pas a placer de mur pour couper la route à l'autre joueur il se deplace toujurs à la premiere case du chemin vert sa victoire retourné par A*.
* 4. Stratégie_3 et Stratégie_3  :
     * Dans ces 2 strategie o, utilise le minMax ou alphaBeta(Selon le boolean minMax). En effet , pour savoir quelle option choisir le joueur appelle choose_action avec le boolean mis a True pour minMax, et a False pour alphaBeta .
     * La fonction choose_action :
        * suppose dans un premier lieu que le joueur se deplace a la premiere case retournée par A* et evoque ensuite MinMax/AlphaBeta sur cette situation du plateau, et celui -ci va lui retourner un score.
        
        * Ensuite elle verifie s'il reste au joueur des murs a placer :
            * Si c'est le cas, elle appelle `draw_wall_location_strategie_2` pour lui retourner une postion sur le chemin de l'adversaire et le place , et fait ensuite appelle a minMax/AlphaBeta sur cette autre configuration du plateau possible : 
                * Si le score est plus grand que celui retourner apres deplacement du joueur on opte pour cette 2 éme demarche sinon on reste sur la premiere (deplacemment du joueur).
     * Selon donc ce qui a été retourné par choose_action on deplace le joueur vers la case retournée , ou on construit un mur sur les cases choisies.
## Description des résultats
Comparaison entre les stratégies. Bien indiquer les cartes utilisées.

Blablabla
