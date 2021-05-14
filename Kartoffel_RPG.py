#!/usr/bin/env python3

#note sur la version : vendeur update <-- plus pratique pour s'y retrouver, non ?
    #ancienne version : color update (couleurs linux)
    # retouche vendeur:
        # travaille maintenant avec la liste Donjon["objets_en_vente"] (+ facile à modifier, modifiable par le programme)
        # un vrai système de dialogue:
            # n'affiche pas "parler au vendeur", garde les action "acheter x" et l'image du vendeur tant que l'on a pas quité le dialogue
            # fait apparaître le nom du vendeur dans le statut
            # fait disparaître la description et les actions de la salle et de son contenu
        # "Vendeur devient "le Vendeur" (car affiché dans le statut)
    # Donjon["Statut_ennemi"] et Donjon["Ancien_statut_ennemi"] deviennent Joueur["Statut_ennemi"] et Joueur["Ancien_statut_ennemi"]
    # procédure pour créer un ennemi : creer_ennemi(nom, statut)
    # placement du FIN en ascii dans un fichier externe
    # les images du coffre, du squelette, de sheppler, le statut du squelette, de sheppler apparaissent au bon moment à la fin. Sheppler disparait dans la map après l'explosion. yeux de Shlepper -> rouges quand il est enragé et image de fin du sceptre = Shlepper enragé (super classe :D ).
    # retouche de quelques images (lapin, gemme, enlèvement des lignes vides/tabulations)
    # quelques autres retouches mineures (procédure presentation(), nom des actions, écran de statut, fonctionnement des couleurs et de cscinder(), cftx())
#bugs restants :
    # la patate fait (100 + un lancé de dés) domages
    # à vous de trouver les autres ;)

#note pour bosser sur google drive : clic droit sur le fichier -> ouvrir avec -> drive notepad ; vous verrez, c'est cool
#pour bosser en même temps, y'a code your cloud (https://codeyourcloud.com/), mais chez moi ça lag trop
#que vous utilisiez l'un ou l'autre (ou rien), téléchargez google drive afin d'avoir les fichiers directement sur votre ordi, c'est plus facile pour les modifier et vous pouvez les lancer avec la console !!

import os #pour pouvoir effacer la console
import time #pour pouvoir attendre
import random #pour les lancés de dés.
if os.name == 'nt':
    from ctypes import windll #pour la couleur sous windows
    couleur = windll.kernel32


############# NOTE : pour comprendre le programme, le plus facile est de partir du bas et de remonter.
############# De plus, il vaut mieux lire le compte rendu avant de regarder les fonctions utilitaires, le pourquoi de tout ce qui commence par 'c' étant détaillé en fin de partie III.


###############################################################
# fonctions utilitaires :
###############################################################


def lignes_fichier(repertoire_et_nom_fichier):
    Lignes = []
    fichier = open(repertoire_et_nom_fichier, "r")
    ligne = fichier.readline()
    while ligne:
        Lignes.append(ligne[:-1])
        ligne = fichier.readline()
    fichier.seek(0) # pour "rembobiner" le fichier
    fichier.close()
    return(Lignes)

def dimensions_fichier(repertoire_et_nom_fichier): # renvoie un couple (le nombre de caractères maximum dans une ligne, le nombre de lignes)
    return(dimensions_texte( lignes_fichier(repertoire_et_nom_fichier) ))

def dimensions_texte(Lignes):
    x = 0
    y = 1
    for ligne in Lignes:
        if clen(ligne) > x: # et > 0 puisque x = 0 au départ
            x = clen(ligne)
        y+=1
    return(x,y)


def clen(Chaine): # clen = color len : sert à compter la longueur d'une chaine de caractère, sans compter ce qui est entre deux caractères spéciaux (ici on a choisi le '&'). On en a besoin pour éviter de compter les codes couleurs lorsque l'on met le texte en forme pour qu'il occupe une place précise de l'écran.
    if type(Chaine) != str:
        return(len(Chaine))
    compter = True
    i = 0
    for c in Chaine:
        if c == Systeme["caractere_special"]:
            compter = not compter
        elif compter:
            i += 1
    return(i)

def cprint(Chaine, end = '\n'): #cprint = color print : sert à afficher une chaine de caractère, sans compter ce qui est entre deux caractères spéciaux (ici on a choisi le '&'). On en a besoin pour éviter que les codes couleurs soient affichés, sous windows par exemple.
    debut_special = Chaine.find(Systeme["caractere_special"])
    fin_special = Chaine.find(Systeme["caractere_special"], debut_special + 1)
    if fin_special == -1:
        if os.name == 'nt':
            print(Chaine, end = end, flush = True)
        else:
            print(Chaine, end = end)
    else:
        if os.name == 'nt':
            print(Chaine[:debut_special], end = "", flush = True) #Habituellement, python stocke tout le texte à afficher tant que l'on ne fait pas de saut de ligne et affiche tout à ce moment là, afin de gagner en performance. En précisant flush = True, on le force a écrire directement (sans mise en cache), car sans cela tout l'écran s'affichera dans la couleur que nous avons demendé en dernier.
        else :
            print(Chaine[:debut_special], end = "")
        commande(Chaine[debut_special + 1 : fin_special])
        cprint(Chaine[fin_special + 1 : ], end = end) #on recommence à partir de la fin de la commande

def cinput(Chaine = ""):
    debut_special = Chaine.find(Systeme["caractere_special"])
    fin_special = Chaine.find(Systeme["caractere_special"], debut_special + 1)
    if fin_special == -1:
        return input(Chaine)
    else:
        if os.name == 'nt':
            print(Chaine[:debut_special], end = "", flush = True)
        else:
            print(Chaine[:debut_special], end = "")
        commande(Chaine[debut_special + 1 : fin_special])
        return cinput(Chaine[fin_special + 1 : ]) #on recommence à partir de la fin de la commande

def commande(Commande):
    modifier_fond = Commande.find("fond")
    if Commande[0:7] == "couleur" and Commande.find("fond") == -1:
        modifier_couleur_consolle(Commande[8:], Systeme["fond_par_defaut"])
    if Commande[0:4] == "fond":
        modifier_couleur_consolle(Systeme["couleur_par_defaut"], Commande[5:])
    if Commande[0:7] == "couleur" and modifier_fond != -1:
        modifier_couleur_consolle(Commande[8 : modifier_fond -1], Commande[modifier_fond +5 : ])

def modifier_couleur_consolle(couleur_police, couleur_fond = 0):
    if couleur_fond == 0:
        couleur_fond = Systeme["fond_par_defaut"]
    windows = os.name == "nt"
    Couleurs = ["noir", "rouge", "bleu", "vert", "cyan", "violet", "jaune", "blanc"]
    Couleurs_linux = ["16", "196", "26", "76", "51", "92", "220", "231"]
    Couleurs_windows = [-8, 4, 1, 2, 3, 5, 6, 7] #explication plus loin pour le -8
    num_couleur = Couleurs.index(couleur_police)
    num_fond = Couleurs.index(couleur_fond)
    if windows:
        couleur.SetConsoleTextAttribute(couleur.GetStdHandle(-11), (Couleurs_windows[num_couleur] +8) + 16*(Couleurs_windows[num_fond] +8))
        # les couleurs étant codées en hexadécimal (base 16), les 8 premières sont les couleurs en foncé et les 8 suivantes sont les mêmes en plus clair. Nous ajoutons donc 8 pour obtenir ces dernières. Comme le noir clair donne du gris, on a codé le noir comme -8 pour arriver à 0.
        # comme le chiffre des "dizaines" représente le fond, il faut multiplier par 16 pour passer à la "dizaine" en base 16. nous rajoutons de même 16*8 pour obtenir le fond en version claire.
        # on ajoute ensuite les nombres des "dizaines" et des unités hexadecimales pour obtenir le nombre hexadecimal.
    else:
        cprint("\x1b[38;5;{};48;5;{}m".format(Couleurs_linux[num_couleur], Couleurs_linux[num_fond]), end = "")

def couleurs_par_defaut():
    return("&couleur {} fond {}&".format(Systeme["couleur_par_defaut"], Systeme["fond_par_defaut"]))

def colorer(chaine, couleur = "", fond = ""):
    if couleur == "":
        couleur = Systeme["couleur_par_defaut"]
    if fond == "":
        fond = Systeme["fond_par_defaut"]
    return("&couleur {} fond {}&".format(couleur, fond) + chaine + couleurs_par_defaut())


def cscinder(chaine, largeur): #renvoie les mots et les commandes qui devraient être coupés à la ligne
# on commance par séparer les commandes
    Chaines1 = isoler_commandes(chaine)
# puis on traite les sauts de ligne manuels afin de ne pas compter la longueur d'une fin de chaine qui devrait être à la ligne.
    Chaines2 = []
    for chaine1 in Chaines1:
        Chaines2 += chaine1.split('\n')
    # attention pour la suite, des chaines vides ont pu être générées.
# enfin on génère des sauts de lignes dès que la chaine dépasse la longueur donnée, tout en vérifiant que l'on ne coupe pas de mot
    Chaines3 = []
    ajouter_a_la_prochaine_ligne = ""
    for chaine2 in Chaines2:
        if len(chaine2) > 0 and chaine2[0] == Systeme["caractere_special"]: #la première condition, qui est testée en premier, s'assure que l'on ne sort pas du tableau pour la deuxième
            ajouter_a_la_prochaine_ligne += chaine2
        else:
            Mots = chaine2.split(" ") #si chaine2 est vide, Mots contient une chaine vide, qui sera correctement traitée par la suite.
            ligne = ""
            for mot in Mots:
                if len(ligne) + len(mot) <= largeur: #il faudrait rajouter 1 pour l'espace mais on l'enlèvera si la condition est vérifiée
                    ligne += mot + " "
                else:
                    Chaines3.append(ajouter_a_la_prochaine_ligne + ligne[:-1]) #on enlève le dernier espace. note : si ligne est vide, ligne[:-1] renvoie une chaine vide.
                    ajouter_a_la_prochaine_ligne = ""
                    while len(mot) > largeur: #peut parraître inutile, mais mots allemand et écrans de petits smartphones ne font pas bon ménage...
                        Chaines3.append(ajouter_a_la_prochaine_ligne + mot[ :largeur -1] + "-")
                        ajouter_a_la_prochaine_ligne = ""
                        mot = mot[largeur -1: ]
                    ligne = mot + " "
            Chaines3.append(ajouter_a_la_prochaine_ligne + ligne[:-1])
            ajouter_a_la_prochaine_ligne = ""
    return(Chaines3)

def isoler_commandes(chaine): #renvoie une liste alternée de phrases/commandes
    R = []
    Chaines1a = chaine.split(Systeme["caractere_special"])
    Chaines1b = []
    special = False #Si chaine commence par une commande, donc par le caractère de séparation, le split() met une chaine vide en première position de la liste Chaines1. Celle-ci ne commence donc jamais par une commande.
    for i in range(len(Chaines1a)):
        if Chaines1a[i] != "": #on verifie qu'il n'y a pas deux commandes de suite (ou une commande vide)
            if special: #si cette ligne est une commande
                Chaines1b.append(Systeme["caractere_special"] + Chaines1a[i] + Systeme["caractere_special"]) #le split ayant enlevé les caractères de séparations, on les remet autours des commandes
            else:
                Chaines1b.append(Chaines1a[i])
        special = not special #le split ayant découpé a chaque début et fin de commande, on a une alternance régulière
    return(Chaines1b)

def ftx(chaine, largeur): # ftx = fixer_taille_X : fixe la taille de la chaine
    difference = largeur - clen(chaine)
    if difference > 0:
        return(chaine + (difference * " "))
    elif difference <= 0:
        return(chaine[:largeur]) #note : peut tronquer une commande !

def cftx(chaine, largeur):
    difference = largeur - clen(chaine)
    if difference > 0:
        return(chaine + (difference * " "))
    elif difference <= 0:
        Chaines = isoler_commandes(chaine)
        for i in range(len(Chaines) -1, -1, -1):
            if difference != 0:
                if len(Chaines[i]) > 0 and Chaines[i][0] != Systeme["caractere_special"]:
                    if len(Chaines[i]) >= difference:
                        Chaines[i] = Chaines[i] [ : difference]
                        difference = 0
                    else:
                        difference = difference - len(Chaines[i])
                        Chaines[i] = ""
        return( "".join(Chaines) ) #assemble les éléments en les séparant par ""
    

def fty(Chaines, largeur, hauteur): # fty = fixer_taille_Y : fixe la taille de liste
    difference = hauteur - clen(Chaines)
    return(Chaines + [largeur * " " for i in range(difference)])

def ftxy(Chaines, largeur, hauteur):
    R = []
    for chaine in Chaines:
        R.append(cftx(chaine, largeur))
    return(fty(R, largeur, hauteur))

def cxy(Chaines, largeur_voulue, hauteur_voulue, largeur, hauteur, fixer_taille_X = True, fixer_taille_Y = True):
# cxy = centrer_X_et_Y : fixe la taille de la liste de chaine
    difference_Y = hauteur_voulue - hauteur
    difference_X = largeur_voulue - largeur
    R = [largeur_voulue * " " for i in range(difference_Y//2)]
    for i in range(hauteur):
        if fixer_taille_X:
            R.append(cftx((difference_X//2)*" " + Chaines[i], largeur_voulue ))
        else:
            R.append( (difference_X // 2) * " " + Chaines[i])
    if fixer_taille_Y:
        for i in range((difference_Y+1)//2):
            R.append(largeur_voulue * " ")
    return(R)

def comparer(chaine1, chaine2): # renvoie un indice de corrélation entre 0 et 1
    if chaine1 == chaine2:
        return(1)
    Mots1 = chaine1.split() #pas de paramètre -> coupe aux " "
    Mots2 = chaine2.split()
    nombre_mots_identiques
    
    Mots1b = Mots1[:] # [:] pour créer une copie de la liste
    Mots2b = Mots2[:]
    for mot1 in Mots1:
        if Mots2b.find(mot1) != -1: #si trouvé (on se fiche de l'indice)
            nombre_mots_identiques += 1
            Mots1b.remove(mot1) #on retire le couple d'éléments de Mots1 x Mots2
            Mots2b.remove(mot1) #pour ne pas le compter plusieurs fois si plusieurs éléments de Mots1 identiques
            # et pour pouvoir refaire la même chose à partir de Mots2b sans le compter plusieurs fois
    for mot2 in Mots2b:
        if Mots1b.find(mot2) != -1:
            nombre_mots_identiques += 1
            Mots1b.remove(mot1) #pour ne pas le compter plusieurs fois si plusieurs éléments de Mots2b identiques
    return(nombre_mots_identiques / ( clen(Mots1) if clen(Mots1) >= clen(Mots2) else clen(Mots2) ))



###############################################################
# fonctions d'affichage :
###############################################################



def effacer_ecran():
    os.system('cls' if os.name == 'nt' else 'clear')


def centrer_et_afficher_ecran_titre(): #ci-après l'évolution de cette fonction
    modifier_couleur_consolle(Systeme["couleur_par_defaut"], Systeme["fond_par_defaut"])
    effacer_ecran()
    
    repertoire_et_nom_fichier = "art/ecran_titre.txt"
    Lignes = lignes_fichier(repertoire_et_nom_fichier)
    # fichier_titre = open(repertoire_et_nom_fichier, "r")
    
    decalage_X = int(Systeme["nombre_de_lettres_X"] / 2 - dimensions_texte(Lignes)[0] / 2)
    if decalage_X < 0:
        decalage_X = 0
    
    for i in range(100):
        Affichage = ""
        x=0
        for ligne in Lignes:
            x+=1
            Affichage += (decalage_X)*" "
            for y in range(clen(ligne)):
                if (0 < -y+x+2*i-Systeme["nombre_de_lettres_Y"] and -y+x+2*i-Systeme["nombre_de_lettres_Y"] < 10):
                    Affichage += str.lower(ligne[y])
                else:
                    Affichage += ligne[y]
            Affichage += "\n"
        
        effacer_ecran()
        cprint(Affichage)
        time.sleep(0.03)
    
    chaine = colorer("Appuyez sur entrée pour entrer dans le donjon...", "jaune")
    decalage_X = int(Systeme["nombre_de_lettres_X"] / 2 - clen(chaine) / 2)
    if decalage_X < 0:
        decalage_X = 0
    entree = cinput((decalage_X * " ") + chaine)
    
    if (not Systeme["fin_partie"]) and entree != "passer" and entree != "p":
        presentation()

def presentation():
    nom = ""
    while nom == "":
        effacer_ecran()
        cprint("\n") #saute deux lignes
        nom = cinput(colorer("Choisissez un pseudonyme : ", "jaune"))
    if nom == "passer" or nom == "p":
        return()
    Phrases = [ " ",
    " ",
    "     Le royaume de Vorstellungskraft est, depuis plusieurs années déjà, sous le joug d'un grand nécromancien.", 3,
    "         Nul ne sait d'où il vient, il se fait appeler Shlepper, et tout le royaume le craint, et le hait.", 3,
    "           Sa puissance est telle qu'il a sû vaincre et soumettre tous les héros ayant osé le défier.", 3,
    "    Il contrôle désormais le royaume. Pille, et taxe les villageois. Et emmagasine son trésor dans son immense","                                                   donjon.", 3,
    " ",
    " ",
    "                       Vous, {}, êtes un mercenaire rêvant de pouvoir et de richesse.".format(colorer(nom, "jaune")), 3,
    "            Vous prévoyez depuis longtemps de défier le nécromancien, afin de vous approprier ses biens.", 3,
    "   Vous voilà maintenant face à son antre. Mais avant de pouvoir combattre le grand Sorcier, vous allez devoir \n                                                  conquerir", 3,
    " ",
    "                                                  Le Donjon",
    " ", 1,
    "                                                 de Kartoffel",
    " ",
    " ", 1 ]
    for i in Phrases:
        if type(i) == str:
            cprint(i)
        else:
            time.sleep(i)
    cinput(colorer(
    "                                      Appuyez sur Entrée pour continuer", "jaune"))


def affichage_scinde(Phrases = False, afficher_actions = True, afficher_description = True): # vaut 0 si rien n'est entré
    dimention_X = Systeme["nombre_de_lettres_X"] - 3 #on garde 3 colones pour les bordures de gauche, de milieu et de droite
    dimention_phrases_X = dimention_X // 2
    dimention_visuel_X = (dimention_X + 1) // 2 # si impaire, c'est le visuel qui a une colone en plus
    dimention_phrases_Y = Systeme["nombre_de_lettres_Y"] - 9 - 3 #on garde 9 lignes pour la map, et 3 pour les bordures du haut, du milieu et du bas
    dimention_X_statut = dimention_phrases_X - 17 - 9 - 2 #15 +2 espaces pour la salle, 5 +4 espaces pour le donjon, 2 pour les bordures supplémentaires (non incluses dans dimention_phrases_X)
    if Phrases == False:
        Phrases_brutes = '\n' + texte_derniere_action(True)
        if afficher_description:
            Phrases_brutes += description()
        Phrases_brutes += texte_derniere_action(False)
        if afficher_actions:
            Phrases_brutes += actions_possibles()
        # variable de transition inutile mais qui clarifie le code
        Phrases = [" {} ".format(p + couleurs_par_defaut()) for p in ftxy(cscinder(Phrases_brutes, dimention_phrases_X - 2), dimention_phrases_X - 2, dimention_phrases_Y)]
        test(Phrases, dimention_phrases_X, dimention_phrases_Y)
        #une liste de chaines !
    if clen(Phrases) > dimention_phrases_Y:
        for i in range (0, clen(Phrases), dimention_phrases_Y):
            affichage_scinde(Phrases[i : dimention_phrases_Y + i])
    Visuel = ftxy(visuel(dimention_visuel_X), dimention_visuel_X, Systeme["nombre_de_lettres_Y"] - 2)
    Statut = ftxy(statut(dimention_X_statut), dimention_X_statut, 9)
    Plan_salle = cxy(plan_salle(), 17, 9, 15, 7)
    Plan_donjon = cxy(plan_donjon(), 9, 9, 5, 4)
    b = " ═║╔╗╚╝╦╠╣╩╬" #b = bodrures : caractère utilisé pour les bordures. Attention le premier est un espace (plus facile pour compter)
    Affichage = b[3] + dimention_phrases_X*b[1] + b[7] + dimention_visuel_X*b[1] + b[4] + '\n'
    for i in range(dimention_phrases_Y):
        Affichage += b[2] + Phrases[i] + b[2] + Visuel[i] + b[2] + '\n'
    Affichage += b[8] + dimention_X_statut* b[1] + b[7] + 17*b[1] + b[7] + 9*b[1] + b[9] + Visuel[dimention_phrases_Y + 1] + b[2] + '\n'
    for i in range(9):
        Affichage += b[2] + Statut[i] + b[2] + Plan_salle[i] + b[2] + Plan_donjon[i] + b[2] + Visuel[dimention_phrases_Y +1 +i] + b[2] + '\n'
    Affichage += b[5] + dimention_X_statut* b[1] + b[10] + 17*b[1] + b[10] + 9*b[1] + b[10] + dimention_visuel_X*b[1] + b[6] + '\n'
    effacer_ecran()
    cprint(Affichage, end='')

def test(Phrases, x, y):
    erreur = ""
    if y != clen(Phrases):
        erreur += "Il manque {} lignes ; ".format(y - clen(Phrases))
    i = 0
    for ligne in Phrases:
        i += 1
        if x != clen(ligne):
            erreur += "Il manque {} caractères à la ligne {} ; ".format(x - clen(ligne), i)
    if erreur != "":
        cprint(colorer(erreur, "rouge"))
        input("afichage du texte : ")
        print(Phrases)
        input("afichage debug : ")
        affichage_debug()
        input("... ")

def affichage_debug(): #pratique pour tester le programme dans un IDE comme Komodo
    print(112*'-')
    print('\n' + texte_derniere_action(True) + description() + texte_derniere_action(False) + actions_possibles())

def afficher_progressivement(Phrases, intervalle_de_temps, afficher_actions_fin = False, image_fin = False):
    if os.name == 'nt':
        for i in range(clen(Phrases)):
            for j in range(i+1):
                ajouter_phrase(Phrases[j])
            if i == clen(Phrases) - 1 and image_fin != False:
                modifier_image(image_fin)
            affichage_scinde(afficher_actions = False, afficher_description = False)
            time.sleep(intervalle_de_temps)
        if not afficher_actions_fin:
            cinput("... ")
        else: #on laisse la fonction affichage scindé reprendre la main, en lui redonnant toutes les phrases auxquelles elle va rajouter les actions possibles :
            for i in range(clen(Phrases)):
                ajouter_phrase(Phrases[i])
    #étrangement, fonctionne seulement sous windows
    else:
        for i in Phrases:
            ajouter_phrase(i)
        if image_fin != False:
            modifier_image(image_fin)
        affichage_scinde(afficher_actions = False, afficher_description = False)
        if not afficher_actions_fin:
            cinput("... ")
        else: #on laisse la fonction affichage scindé reprendre la main, en lui redonnant toutes les phrases auxquelles elle va rajouter les actions possibles :
            for i in range(clen(Phrases)):
                ajouter_phrase(Phrases[i])


def description():
    if not Joueur["creature_combatue"] and (not Joueur["Statut_ennemi"] == "Dialogue"):
        x = Joueur["pos_donjon_Y"]
        y = Joueur["pos_donjon_X"]
        Chaine_initiale = Donjon["piece"] [ Donjon["Donjon1"] [x][y] ] [1] + " Vous voyez"
        Chaine = Chaine_initiale
        for objet in salle_courante()[0]:
            Chaine += " {},".format(objet[0][0])
        for creature in salle_courante()[1]:
            Chaine += " {},".format(creature[0][0])
        if Chaine != Chaine_initiale:
            return(Chaine[:-1] + ".\n\n")
        else:
            return("Vous ne voyez rien.\n\n")
    else:
        return("")


def visuel(dimention_visuel_X):
    if Systeme["nom_image"] == "":
        if not Joueur["creature_combatue"]:
            image = "Salle_vide"
        else:
            image = Joueur["creature_combatue"]
    else:
        image = Systeme["nom_image"]
    
    for c, c_norm in {'é': 'e', 'è': 'e', 'ê': 'e', 'à': 'a', 'É': 'E'}.items():
        image = image.replace(c, c_norm)
    Lignes = lignes_fichier("art/{}.txt".format(image))
    dimensions = dimensions_texte(Lignes) #pour ne pas refaire plusieurs fois le calcul
    
    Lignes = ftxy(Lignes, dimensions[0], dimensions[1]) #homogénéise la longueur des lignes du fichier afin de ne pas regarder dans un index inexistant de la liste
    return(cxy(Lignes, dimention_visuel_X, Systeme["nombre_de_lettres_Y"] - 2, dimensions[0], dimensions[1]))

def modifier_image(image):
    global Systeme
    Systeme["nom_image"] = image


def statut(dimention_X_statut):
    S = [comparer_et_colorer(Joueur["Statut"] [i], Joueur["Ancien_statut"][i]) for i in range(len(Joueur["Statut"]))]
    if Joueur["Statut"] [2] > 1:
        Or = "{} pièce".format(S[2])
    elif Joueur["Statut"] [2] == 1:
        Or = "{} pièces".format(S[2])
    else:
        Or = "pas assez"
    if Joueur["Statut"] [0] >= 0:
        dixieme_de_vie = Joueur["Statut"] [0] *10 // Joueur["Statut"] [1]
    else:
        dixieme_de_vie = 0
    Barre_vie = "[{}]".format(dixieme_de_vie*colorer('-', "vert") + (10 - dixieme_de_vie)*colorer('-', "rouge"))
    
    Statut_monstre = [ "", "", dimention_X_statut*"_", "" ]
    if Joueur["creature_combatue"]: #on ne l'affiche qu'en combat
    # si on est hors combat, Joueur["creature_combatue"] vaut false; sinon, comme elle contient une chaine non vide, le test renvoie True
        Statut_monstre[0] = " {} vous fait face".format(Joueur["creature_combatue"].capitalize()) #peut déborder (tampis)
        if Joueur["Statut_ennemi"] != "Dialogue":
            if Joueur["Statut_ennemi"] [0] > 0:
                S_e = comparer_et_colorer(Joueur["Statut_ennemi"] [0], Joueur["Ancien_statut_ennemi"] [0])
                Statut_monstre[1] = " Il lui reste {} de vie".format(S_e)
            else:
                Statut_monstre[1] = " Celui-ci n'a plus de vie"
    return(Statut_monstre + [ " Vie: {} {}/{}".format(Barre_vie, S[0], S[1]), " Or: {}".format(Or), " Bonus Degats: {}".format(S[3]), " Armure: {}".format(S[4]), " Bonus Soin: {}".format(S[5]) ] )

def comparer_et_colorer(nouveau_statut, ancien_statut):
    if nouveau_statut == ancien_statut:
        return str(nouveau_statut)
    elif nouveau_statut < ancien_statut:
        return colorer(str(nouveau_statut), "rouge")
    elif nouveau_statut > ancien_statut:
        return colorer(str(nouveau_statut), "vert")

def mise_a_jour_statut():
    global Joueur
    Joueur["Ancien_statut"] = Joueur["Statut"][:] #[:] pour créer une nouvelle liste
    Joueur["Ancien_statut_ennemi"] = Joueur["Statut_ennemi"][:]


def plan_salle():
    Salle=[]
    for y in range(-3, 4):
        chaine =""
        for x in range(-7, 8):
            if x == Joueur["pos_piece_X"] and y == Joueur["pos_piece_Y"]:
                chaine = chaine + (Systeme["caractere_joueur"])
            elif objet(x,y) != False:
                chaine = chaine + objet(x, y)
            else:
                if y==-3 or y==3 or x==-7 or x==7:
                    chaine = chaine + Systeme["caractere_mur"]
                else:
                    chaine = chaine + " "
        Salle.append(chaine)
    return(Salle)

def objet(x, y): # retourne le caractère représentatif de la première chose trouvée dans la case (x, y) de la salle
    for creature in salle_courante()[1]:
        if creature[1] == x and creature[2] == y:
            return(creature[0][1])
    for objet in salle_courante()[0]:
        if objet[1] == x and objet[2] == y:
            return(objet[0][1])
    return(False)


def plan_donjon():
    Plan=[]
    for ligne in range(len(Donjon["Donjon1"])):
        chaine = ""
        for colone in range(len(Donjon["Donjon1"] [ligne])):
            if Joueur["pos_donjon_Y"] == ligne and Joueur["pos_donjon_X"] == colone:
                chaine += (Systeme["caractere_donjon_joueur"])
            elif Donjon["Donjon1"] [ligne][colone] != 0:
                chaine += Systeme["caractere_donjon_piece"]
            else:
                chaine += ' '
        Plan.append(chaine)
    return(Plan)


def texte_derniere_action(avant_description):
    if Joueur["derniere_action"][0] != "":
        Chaine = Joueur["derniere_action"][0] + '\n'
        modifier_derniere_action("", 0, False)
        return(Chaine)
    else:
        return("")
# ancienne fonction :
# def afficher_Joueur["derniere_action"](avant_description):
    # if Joueur["derniere_action"][0] == "" or avant_description != Joueur["derniere_action"][2]:
        # if not avant_description:
            # cprint("")
    # else:
        # cprint(Joueur["derniere_action"][0])
        # if Joueur["derniere_action"][1] != 0:
            # for i in range (3):
                # time.sleep(Joueur["derniere_action"][1]/3)
                # cprint(".", end='')
        # cprint('\n') # reviens à la ligne et saute une ligne
        # modifier_derniere_action("", 0, False)

def modifier_derniere_action(action, duree, avant_description):
    if action != "":
        action = action + '\n'
    Joueur["derniere_action"][0] = action
    Joueur["derniere_action"][1] = duree
    Joueur["derniere_action"][2] = avant_description

def ajouter_phrase(phrase, end = '\n'):
    Joueur["derniere_action"][0] += phrase + end



###############################################################
# fonctions des actions possibles :
###############################################################


def action(entree):
    global Joueur
    changer_question(colorer("Que voulez-vous faire ?", "jaune"))
    a = 0
    if not Joueur["creature_combatue"] and (not Joueur["Statut_ennemi"] == "Dialogue"):
        for objet in salle_courante()[0]:
            for action in objet[0][2]: #[0] se réfère à l'objet en lui-même (contrairement à [1] et [2] qui se réfèrent à ses coordonnées)
                if entree == action[0]:
                    a = action[1]
        for creature in salle_courante()[1]:
            for action in creature[0][2]: #même remarque pour [0]
                if entree == action[0]:
                    a = action[1]
    for action in Joueur["actions_supplementaires"]:
        if entree == action[0] or entree == action[2]:
            a = action[1]
    for action in Joueur["actions_persistantes"]:
        if entree == action[0]:
            if not Joueur["Statut_ennemi"] == "Dialogue":
                if not Joueur["creature_combatue"]:
                    if action[2]:
                        a = action[1]
                elif action[3]:
                    a = action[1]
    
    if a == 0:
        if entree != "":
            modifier_derniere_action('Vous ne savez pas faire "{}"...'.format(entree), 0, False)
        else:
            modifier_derniere_action("Vous ne pouvez pas ne rien faire...", 0, False)
    else:
        #on teste ensuite si une créature nous attaque avant l'action
        if not Joueur["creature_combatue"] and (not Joueur["Statut_ennemi"] == "Dialogue"):
            for creature in salle_courante()[1]:
                if creature[0][4] and a != creature[0][2][0][1]: #même remarque pour [0] : avec [0][4] on regarde si la créature est agressive, avec [0][2] on a la liste des actions possibles sur la créature, représenté par un couple ("chaine a proposer", fonction à déclancher) et [0][2][0][1] désigne la fonction à déclancher de la première action possible sur la créature, soit le combat s'il est agressif. On vérifie ici que ce n'est pas déjà ce que voulait faire le joueur. Comment ça, compliqué ?
                    modifier_derniere_action("{} vous agresse avant que vous n'ayez pu '{}' !\n".format(creature[0][3].capitalize(), entree), 0, True)
                    a = lambda: combattre(creature[0][3]) #passer par une fonction anonyme est le seul moyen que j'ai trouvé pour stocker une fonction paramétrée
        
        Joueur["actions_supplementaires"] = [] #réinitialise les actions supplementaires à chaque affichage
        mise_a_jour_statut() #stocke les anciens statuts pour un calcul de différence ultérieur
        modifier_image("")
        a()


def actions_possibles():
    if Systeme["fin_partie"] or Systeme["quitter"]:
        return("")
    
    Chaine_initiale = colorer("Vous pouvez faire les actions suivantes :", "jaune")
    Chaine = Chaine_initiale
    
    if not Joueur["creature_combatue"] and (not Joueur["Statut_ennemi"] == "Dialogue"):
        for objet in salle_courante()[0]:
            for action in objet[0][2]:
                Chaine += " {},".format(action[0])
        for creature in salle_courante()[1]:
            for action in creature[0][2]:
                Chaine += " {},".format(action[0])
    
    for action in Joueur["actions_supplementaires"]:
        Chaine += " {},".format(action[0])
    
    for action in Joueur["actions_persistantes"]:
        if not Joueur["Statut_ennemi"] == "Dialogue":
            if not Joueur["creature_combatue"]:
                if action[2]:
                    Chaine += " {},".format(action[0])
            elif action[3]:
                Chaine += " {},".format(action[0])
    
    if Chaine != Chaine_initiale:
        return(Chaine[:-1] + ".")
    else:
        return("Vous ne pouvez a priori rien faire.")

def ajouter_action(description, fonction, raccourcis = None):
    global Joueur
    if raccourcis == None and description[0] in "0123456789":
        raccourcis = description[0]
    # si la description est de la forme "1. Attaquer", on peut juste entrer 1 ; ne marche que jusqu'à 9
    Joueur["actions_supplementaires"].append([description, fonction, raccourcis])

def ajouter_action_persistante(description, fonction, hors_combat = True, en_combat = True):
    global Joueur
    Joueur["actions_persistantes"].append([description, fonction, hors_combat, en_combat])

def retirer_action_persistante(fonction): #on utilise plutôt la fonction car on change régulièrement sa description
    global Joueur
    for a in Joueur["actions_persistantes"]:
        if a[1] == fonction:
            Joueur["actions_persistantes"].remove(a)



def salle_courante():
    x = Joueur["pos_donjon_X"]
    y = Joueur["pos_donjon_Y"]
    return( Donjon["Pieces"] [ Donjon["Donjon1"] [y][x] ] )

def bouger(x, y):
    global Joueur
    Joueur["pos_piece_X"]  = x
    Joueur["pos_piece_Y"] = y

def deplacer(x, y):
    global Joueur
    Joueur["pos_donjon_X"] += x
    Joueur["pos_donjon_Y"] += y
    bouger( - Joueur["pos_piece_X"], - Joueur["pos_piece_Y"])
    modifier_derniere_action("Vous entrez dans une nouvelle pièce.", 0, True)

def deplacer_haut():
    bouger(0, -2)
    deplacer(0,-1)
def deplacer_droite():
    bouger(6, 0)
    deplacer(1,0)
def deplacer_gauche():
    bouger(-6, 0)
    deplacer(-1,0)
def deplacer_bas():
    bouger(0, 2)
    deplacer(0,1)

def deplacer_salle_coffre():
    modifier_image("Salle_coffre")
    deplacer_bas()

def deplacer_salle_shlepper():
    modifier_image("Salle_coffre")
    deplacer_droite()
    shlepper()


def ouvrir_coffre1(): #obtenir la patate
    obtenir_objet("la patate")
    retirer_objet("un enorme coffre en bois")

def commercer(phrase_initiale = "Bonjour aventurier, je suis un marchand ambulant. Je peux vous vendre des objets qui rendront votre petite expédition dans le donjon plus facile, comme "): #parler au vendeur
    
    creer_ennemi("le Vendeur", "Dialogue") #fait apparître l'image du vendeur (sauf si un objet à été obtenu), fait disparaître la description et les actions de la salle et de son contenu, fait apparaître le vendeur dans le nom du statut
    phrase = phrase_initiale
    for objet in Donjon["objets_en_vente"]:
        num_objet = Joueur["Noms_objet"].index(objet[0])
        if not Joueur["Inventaire"] [num_objet]:
            phrase += objet[2] + " ({} pièces d'or), ".format(objet[1])
            ajouter_action( "acheter " + objet[0], lambda copie_objet = objet : achat_objet(copie_objet) )
            #le moyen le plus simple, mais pas très élégant, de copier cette variable mutable est ici de la passer comme paramètre par défaut de la fonction anonyme
    ajouter_action("s'en aller", fermer_dialogue)
    if phrase == phrase_initiale:
        ajouter_phrase("Bonjour aventurier. Je n'ai plus rien à vous vendre, mais grâce à vous, je suis riiiiiiiche ! Au revoir !")
    else:
        ajouter_phrase(phrase[ :-2] + '.')

def achat_objet(objet):
    if Joueur["Statut"] [2] >= objet[1]:
        ajouter_phrase(objet[3])
        ajouter_phrase("")
        Joueur["Statut"] [2] -= objet[1]
        obtenir_objet(objet[0])
    else:
        ajouter_phrase("Désolé, mais il vous manque {} or... Revenez quand vous serrez plus fortuné !".format(objet[1] - Joueur["Statut"] [2]))
    ajouter_phrase("")
    commercer("Il me reste ")

def fermer_dialogue():
    global Joueur
    ajouter_phrase("Vous terminez la conversation.\n")
    Joueur["creature_combatue"] = False
    Joueur["Statut_ennemi"] = [0,0,0,0]

def enflammer_epee(): #fusion de l'épée et de la gemme pour avoir l'épée enflammée
    global Joueur
    Joueur["Inventaire"]
    Joueur["Inventaire"] [1] = False
    Joueur["Inventaire"] [4] = False
    retirer_action_persistante(enflammer_epee)
    obtenir_objet(Joueur["Noms_objet"][5])

def obtenir_objet(nom_objet): #loot d'objet 
    global Joueur
    objet = Joueur["Noms_objet"].index(nom_objet)
    if objet == 0:
        modifier_derniere_action("Votre premier butin ! Vous trouvez... Une patate ?!", 0, True)
        ajouter_action_persistante("manger la patate", patate, hors_combat = False)
    elif objet == 1:
        augmenter_caracteristique(3, 5)
        if Joueur["Inventaire"] [4]:
            ajouter_action_persistante("enflammer l'épée", enflammer_epee, en_combat = False)
    elif objet == 2:
        augmenter_caracteristique(4, 2)
    elif objet == 3:
        obtenir_or(5)
        augmenter_caracteristique(1, 30)
        augmenter_caracteristique(5, 5)
    elif objet == 4:
        if Joueur["Inventaire"] [1]:
            ajouter_action_persistante("enflammer l'épée", enflammer_epee, en_combat = False)
    elif objet == 5:
        augmenter_caracteristique(3, 7)
    ajouter_phrase("Vous obtenez {} !".format(nom_objet))
    modifier_image(nom_objet)
    Joueur["Inventaire"] [objet] = True

def obtenir_or(montant_or): #augmente l'or
    global Joueur
    ajouter_phrase("Vous obtenez {} pièce{} d'or !".format(montant_or, ("s" if montant_or > 1 else "")))
    Joueur["Statut"] [2] += montant_or

def augmenter_caracteristique(caracteristique, valeur_cible): #augmente les stats avec les objets
    global Joueur
    if Joueur["Statut"] [caracteristique] < valeur_cible:
        if caracteristique == 1: #si on augmante la vie maximum
            Joueur["Statut"] [0] += valeur_cible - Joueur["Statut"] [caracteristique] #on augmente la vie actuelle en conséquence
        Joueur["Statut"] [caracteristique] = valeur_cible


def sortir_donjon(): #empeche de sortir du donjon
    modifier_derniere_action("Vous ne pensez tout-de même pas ressortir d'ici avant d'avoir accompli votre mission ? Ou peut-être ne savez-vous pas quelle est l'espérence de vie des traîtres au Royaume de Vorstellungs...?", 0, True)



###############################################################
# fonctions de combat :
###############################################################


def lance_des_creature(): #lancé de dès de l'ennemi
    return(random.randint(Joueur["Statut_ennemi"] [1], Joueur["Statut_ennemi"] [2]) - Joueur["Statut"] [4])

def lance_des_joueur(): #lancé de dès du joueur 
    return(random.randint(1,6) + Joueur["Statut"] [3])

def lance_des_soin(): #lancé de dès pour soin
    return(random.randint(1,6) + Joueur["Statut"] [5])


def creer_ennemi(nom, statut):
    global Joueur
    Joueur["creature_combatue"] = nom
    Joueur["Statut_ennemi"] = statut
    Joueur["Ancien_statut_ennemi"] = statut #pour ne pas considérer la différence avec le monstre précédent comme une variation à afficher
    # avec ces variables, on a toutes les données pour relancer une fonction combat() à chaque affichage. Ca utilise la boucle principale (boucle_de_jeu) du programme, le système d'entrée et d'affichage principal du programme plutot qu'à refaire des while, print et input dans chaque fonction. En plus, ça conserve l'affichage scindé.

def combattre(creature): #affiche l'ennemi et lui attribut ses statistiques
    if creature == "la licorne":
        creer_ennemi(creature, [25, 6, 11, "une gemme flamboyante"])
        ajouter_phrase("Quoi ? Une majestueuse licorne se dresse devant vous ! Pas de quartier, on est dans un donjon, il faut la tuer !")
    if creature == "le lapin":
        creer_ennemi(creature, [7, 1, 1, 1]) #PV, dés min, dés max, or laché (ou objet si une chaine de caractère)
        ajouter_phrase("Votre premier monstre ! Un lapin au regard vicieux ! Tuez le vite avant qu'il ne s'acharne contre vous !")
    if creature == "le gobelin":
        creer_ennemi(creature, [15, 1, 6, "un anneau"])
        ajouter_phrase("Une petite créature se dresse devant vous. C'est un gobelin. Il n'est pas très bien équipé, mais il cherche à vous attaquer.")
    if creature == "l'orc":
        creer_ennemi(creature, [20, 1, 9, 9])
        ajouter_phrase("Une ombre vous fait face. A l'odeur nauséabonde, vous reconnaissez un orc. Celui ci dispose d'une armure en acier. A voir l'hostilité émanant de son regard, il n'a pas l'air d'apprecier de vous trouver ici.")
    if creature == "le squelette":
        creer_ennemi(creature, [30, 5, 6, 0])
        ajouter_phrase("Un garde squelette... Decidement, ce donjon nous reserve bien des surprises. Comment tuer ce qui est déjà mort ?")
    if creature == "le squelette ressuscité":
        creer_ennemi(creature, [30, 5, 6, 0])
        ajouter_phrase("A ces mots, un tas d'os apparaît. vous reconnaissez ce qu'il reste de votre adversaire de la salle précédente... Qui se reconstitue sous vos yeux ! Shlepper sort l'artillerie lourde, et vous en profitez pour vous soigner.")
    ajouter_phrase("")
    fin_tour()

def attaquer(): #lance les dès pour le joueur et pour l'adversaire
    dommages(lance_des_joueur(), lance_des_creature())

def soigner(): #sort de soin pour regagner un peu de vie
    global Joueur
    h = random.randint(1,5) + Joueur["Statut"] [5]
    if Joueur["Statut"] [0] + h <= Joueur["Statut"] [1]:
        ajouter_phrase(colorer("Vous gagnez {} points de vie.".format(h), "vert"))
        Joueur["Statut"] [0] = Joueur["Statut"] [0] + h
    else:
        ajouter_phrase(colorer("Vous récupérez {} points de vie.".format(Joueur["Statut"] [1] - Joueur["Statut"] [0]), "vert"))
        Joueur["Statut"] [0] = Joueur["Statut"] [1]
    dommages(0, lance_des_creature())

def patate(): #utilisation de la patate, permet d'obtenir un lancé de dès de 100
    global Joueur
    ajouter_phrase("Vous mangez la patate...")
    ajouter_phrase("Cela inflige d'importants dégats à l'adversaire, qui est immobilisé ce tour !")
    ajouter_phrase(colorer(Joueur["creature_combatue"].capitalize() + " perd {} points de vie".format(100), "rouge"))
    ajouter_phrase("")
    Joueur["Inventaire"][0] = False
    retirer_action_persistante(patate)
    dommages(100, 0)


def phrase_attaque(score_joueur, score_creature): #phrases pour les attaques
    if score_joueur < score_creature:
        attaquant = ("ennemi" if score_creature != 0 else "")
        defenseur = ("joueur" if score_joueur != 0 else "")
    if score_joueur == score_creature:
        attaquant = ("égalité" if (score_creature != 0 and score_joueur) != 0 else "")
    if score_joueur > score_creature:
        attaquant = ("joueur" if score_joueur != 0 else "")
        defenseur = ("ennemi" if score_creature != 0 else "")
    
    if Joueur["creature_combatue"] != "Shlepper":
        if attaquant == "joueur":
            ajouter_phrase("*Vous atteignez votre cible !*")
        elif attaquant == "ennemi":
            if defenseur == "joueur":
                ajouter_phrase("*L'ennemi esquive, et en profite pour vous attaquer !*")
            else:
                ajouter_phrase(Joueur["creature_combatue"].capitalize() + " continue de vous attaquer !")
        elif attaquant == "égalité":
            ajouter_phrase("L'ennemi pare votre attaque")
    else:
        if attaquant == "joueur":
            ajouter_phrase("*Vous parvenez à percer la défense de Shlepper !*")
        elif attaquant == "ennemi":
            a = random.randint(1,3)
            if a == 1:
                ajouter_phrase("*Shlepper{}vous envoit un trait d'ombre !*".format(" esquive, et " if defenseur == "joueur" else " "))
            elif a == 2:
                ajouter_phrase("*{} en profite pour vous projeter contre le mur*".format("Votre attaque ne fait rien au nécromancien, qui" if defenseur == "joueur" else "Le nécromancien"))
            elif a == 3:
                ajouter_phrase("*Shlepper{}vous envoit une boule de feu*".format(" est bien trop puissant pour être terrassé par ce genre d'attaque, il " if defenseur == "joueur" else " "))
        elif attaquant == "égalité":
            ajouter_phrase("*Le bouclier magique de Shlepper absorbe l'attaque !*")

def dommages(score_joueur, score_creature): #dmmages infligés par les attaques
    global Joueur
    if score_joueur != 0:
        ajouter_phrase("Vous obtenez un score de {}".format(comparer_et_colorer(score_joueur, score_creature)))
    if score_creature != 0:
        ajouter_phrase("Votre adversaire obtient un score de {}".format(comparer_et_colorer(score_creature, score_joueur)))
    if score_joueur < score_creature: # and c != d inutile puisque c < d
        if Joueur["Statut"] [0] - score_creature > 0:
            Joueur["Statut"] [0] = Joueur["Statut"] [0] - score_creature
            ajouter_phrase(colorer("Vous perdez {} points de vie".format(score_creature), "rouge"))
        else: # évite de se retrouver avec -3 points de vie
            Joueur["Statut"] [0] = 0
        phrase_attaque(score_joueur, score_creature)
    elif score_joueur == score_creature:
        phrase_attaque(score_joueur, score_creature)
    else:
        Joueur["Statut_ennemi"] [0] = Joueur["Statut_ennemi"] [0] - score_joueur
        phrase_attaque(score_joueur, score_creature)
        ajouter_phrase(colorer(Joueur["creature_combatue"].capitalize() + " perd {} points de vie".format(score_joueur), "rouge"))
    
    if Joueur["Statut_ennemi"] [0] < 1: #Monstre mort
        if Joueur["creature_combatue"] == "Shlepper" or Joueur["creature_combatue"] == "Shlepper enragé":
            Joueur["Statut"] [0] = Joueur["Statut"] [1] #vie = vie max
            shlepper(3)
        elif Joueur["creature_combatue"] == "le squelette ressuscité":
            shlepper(4)
        else:
            victoire()
    elif Joueur["Statut"] [0] < 1: #Joueur mort
        if Joueur["creature_combatue"] == "Shlepper" or Joueur["creature_combatue"] == "Shlepper enragé":
            game_over("\nD'un revers de la main, Shlepper vous ejecte par la fenêtre de son donjon, s'en est finit de votre quête.")
        else:
            game_over("Tué par {}.".format(Joueur["creature_combatue"]))
    elif Joueur["creature_combatue"] == "Shlepper" and Joueur["Statut_ennemi"] [0] < 51:
        shlepper(2)
        fin_tour()
    else:
        fin_tour()

def fin_tour():
    # ajouter_phrase(Joueur["creature_combatue"].capitalize() + " a {} points de vie".format(Joueur["Statut_ennemi"] [0]))
    # ajouter_phrase("Il vous reste {} points de vie".format(Joueur["Statut"] [0]))
    ajouter_action("1: attaquer", attaquer)
    ajouter_action("2: lancer sort de soin", soigner)


def game_over(cause): #mort en combat
    global Systeme
    Systeme["fin_partie"] = True
    ajouter_phrase(cause)
    ajouter_phrase("\n____GAME\n\n__________OVER") #temporaire(*)
    affichage_scinde() #pour afficher le dernier tour et les deux lignes ci-dessus
    cinput("... ") #attendre confirmation
    effacer_ecran() # (*)mettre un écran de game over ici

def victoire(): #fin de combat, donne les objet lootés par l'ennemi ainsi que de l'or
    global Joueur
    if type(Joueur["Statut_ennemi"] [3]) == str:
        obtenir_objet(Joueur["Statut_ennemi"] [3])
    elif Joueur["Statut_ennemi"] [3] != 0:
        obtenir_or(Joueur["Statut_ennemi"] [3])
    #sortie du combat :
    Joueur["Statut"] [0] = Joueur["Statut"] [1] #vie = vie max
    retirer_creature(Joueur["creature_combatue"])
    Joueur["creature_combatue"] = False


def retirer_creature(creature): #retire les créatures après les avoir vaincu
    for creature2 in salle_courante()[1]:
        if creature2[0][3] == creature: #[0] se réfère à la creature en elle-même (contrairement à [1] et [2] qui se réfèrent à ses coordonnées). [3] se réfère au nom de la créature.
            bonne_journee = creature2
    salle_courante()[1].remove(bonne_journee) #en dehors de la boucle de façon à ne le faire qu'une fois si plusieurs mêmes créatures sont présentes

def retirer_objet(objet): #retire les objets après les avoir récupérés
    for objet2 in salle_courante()[0]:
        if objet2[0][0] == objet: # le deuxième [0] se réfère à la description de l'objet, car ceux-ci n'ont pas de noms comme les créatures.
            au_revoir = objet2
    salle_courante()[0].remove(au_revoir)


def shlepper(phase = 1): #Combat contre le boss en trois phases
    global Joueur
    if phase == 1:
        affichage_scinde(afficher_actions = False)
        cinput("...")
        creer_ennemi("Shlepper", [150, 8, 12, 30]) # 150 PVs : imbattable sans les objets evidemment :) La patate apportera aussi un gros +
        affichage_scinde()
        afficher_progressivement( ["Le voilà. Devant vous se dresse le Tyran, Shlepper. Vous apercevez son trésor derière lui. Votre regard se pose sur son scèptre. Il en émane une aura troublante.", "\n«Alors c'est toi, l'impétueux mercenaire tentant de me détrôner. Je t'attendais» Vous lance-t-il. Vous vous lancez alors dans le combat, attiré par tant de pouvoir."], 2, image_fin = "Shlepper" )
        fin_tour()
    elif phase == 2: # Phase 2 : Plus gros dégats
        ajouter_phrase("\n«Argh ! Comment ose tu ?! Tu vas voir ce qu'est la souffrance !»")
        ajouter_phrase("*Le coup de trop, Shlepper enrage !*")
        Joueur["creature_combatue"] = "Shlepper enragé"
        Joueur["Statut_ennemi"] [1] += 2
        Joueur["Statut_ennemi"] [2] += 2
    elif phase == 3: #Phase 3 : invocation de mort vivant (bahoui, c'est un nécromancien, faut l'exploiter ça) avant l'éxécution du vilanpasbeau
        afficher_progressivement(["\n«*kof kof* Tu te débrouilles bien... Mais je ne me laisserais pas faire, héhé.. Zauberwort !»"], 1.5)
        combattre("le squelette ressuscité")
    elif phase == 4:
        ajouter_phrase("\nLe pauvre squelette s'effondre ; vous avez brisé la dernière arme du nécromancien.")
        affichage_scinde(afficher_actions = False)
        cinput("... ")
        Joueur["creature_combatue"] = "Shlepper"
        afficher_progressivement( ["Shlepper tombe à genoux. Il a perdu ce combat, et il le sait. Ses forces l'ont abandonné.", "Vous vous approchez."], 2, True)
        ajouter_action("1 : Asséner le coup de grâce au nécromancien, en saluant sa combativité", choix1)
        ajouter_action("2 : Narguer votre ennemi avant de le tuer comme un péon", choix2)
    elif phase == 5:
        retirer_creature("Shlepper")
        Joueur["creature_combatue"] = False
        Joueur["Statut_ennemi"] = "Dialogue"
        modifier_image("Salle_coffre")
        ajouter_action("1 : Prendre le scèptre et reigner sur Vorstellungskraft et sur le monde", fin1)
        ajouter_action("2 : Détruire le scèptre, et vous contenter du trésor", fin2)
        afficher_progressivement( ["Vous reprennez conscience bien plus tard.", "Plus aucune trace de Shlepper, seul le scèptre reste au milieu de la salle.", "L'aura qui en émane est plus démoniaque que précedemment."], 1.5, True)

def choix1():#tuer le sorcier avec honneur
    afficher_progressivement( ["Vous saluez Shlepper.", "Il vous sourit et baisse la tête.", "Vous le décapitez aussitôt.", "Vous n'avez pas le temps de ranger votre arme dans son fourreau que le cadavre du nécromancien explose, vous envoyant contre le mur !"], 2, image_fin = "le squelette ressuscité" )
    shlepper(5)

def choix2(): #se moquer du sorcier
    global Joueur
    modifier_image("Shlepper enragé")
    afficher_progressivement( ["Shlepper utilise ses dernières forces pour tenter de vous poignarder.", "Vous le décapitez aussitôt.", "Vous n'avez pas le temps de ranger votre arme dans son fourreau que le cadavre du nécromancien explose, vous envoyant contre le mur !", "Il vous reste {} points de vie...".format(Joueur["Statut"] [0] - 2  if Joueur["Statut"] [0] - 2 > 0  else 0) ], 1, image_fin = "le squelette ressuscité" )
    Joueur["Statut"] [0] -= 2
    if Joueur["Statut"] [0] < 1:
        game_over("Assassiné par Shlepper. La boulette.")
    shlepper(5)

def fin():
    global Systeme
    Fin = lignes_fichier("art/FIN.txt")
    decalage_X = int(Systeme["nombre_de_lettres_X"] / 2 - dimensions_texte(Fin)[0] / 2)
    for chaine in Fin:
        cprint( decalage_X*" " + chaine )
    Systeme["fin_partie"] = True

def fin1():#fin ou l'on garde le sceptre
    modifier_image("Salle_coffre")
    afficher_progressivement( ["Au contact du scèptre, vous ressentez une vive douleur.", "Vous levez la tête, arborant un rictus vicieux.", "« Le monde est à moi. »"], 1, image_fin = "Shlepper enragé")
    effacer_ecran()
    premiere_fin()

def premiere_fin(): #générique de fin après fin1()
    Phrases = ["Vous avez décidé de garder le sceptre de karoffel. Au final vous ne valez guère mieux que Schlepper.","Tandis qu'un orage gronde sur le chateau de Kartoffel, vous éclatez d'un rire diabolique.","A cause de vous, le monde de Vorstellungskraft va vivre un nouvel âge de ténèbre.","Etait-ce bien la peine d'entamer ce périple, pour au final avoir le même dénouement ?","De toutes façon, là n'est pas la question : vous êtes le maitre de ce pays maintenant.","Vous utilisez le pouvoir du scpetre afin d'invoquer une légion de mort-vivant.","Après les avoir envoyer pour concquérir le royaume, vous vous asseyez sur le sombre trône de ce donjon :","Les habitants de Vorstellungskraft vont voir qui est le plus puissant, maintenant.",]
    fin()
    for phrase in Phrases:
        cprint(phrase)
        time.sleep(4)
    cinput("... ")
    # ce serait bien de demander le nom du joueur victorieux, et de remplacer le nom du boss par celui-ci s'il a fait le choix de s'emparrer du sceptre !

def fin2(): #fin ou l'on détruit le sceptre
    modifier_image("Salle_coffre")
    afficher_progressivement( ["Vous frappez violemment le scèptre avec votre arme, le faisant éclater en plusieurs morceaux.", "Un leger frisson vous envahit. Le monde est sauf maintenant, et le trésor à vous !"], 1.5)
    # en contrepartie, on pourrait afficher dans l'introductioon, le nom des légendes du royaumes (personnes ayant brisé le sceptre).
    effacer_ecran()
    deuxieme_fin()

def deuxieme_fin(): #générique de fin après fin2()
    Phrases = ["Vous regardez le sceptre en morceau. Votre quete est enfin terminee.","Vous avez eu la force morale necessaire pour ne pas vous laisser corrompre par le pouvoir du sceptre.","Grace a vous, le monde est sauve, et un nouvel age de lumiere va commencer pour Vorstellungskraft.","Vous serrez maintenant connu comme le heros ayant vaincu Schlepper.","Vous sortez de ce terrible donjon, un nouveau jour se leve.","Le soleil commence a apparaitre, derriere les collines, cela sera la premiere belle journee depuis longtemps.","Vous regardez une derniere fois le donjon et vous dites que vous avez bien fait d'entammer ce periple.","Vous prenez maintenant la route pour de nouvelles aventures."]
    fin()
    for phrase in Phrases:
        cprint(phrase)
        time.sleep(4)
    cinput("... ")
    # on pourrait éventuellement afficher le nom des boss successifs dans les crédits ("merci à {} pour avoir joué le rôle du méchant... jusqu'à ce que {} mette un terme à son reigne !")



###############################################################
# fonctions de menus :
###############################################################


def boucle_de_jeu(): #on cycle entre l'affichage et l'execution des choix du joueur
    while not Systeme["fin_partie"]:
        affichage_scinde()
        action(cinput(Joueur["question"]) )

def changer_question(chaine):
    global Joueur
    Joueur["question"] = chaine + " "



###############################################################
#parametres d'initialisation :
#comme certaines données (textes, maps...) sont assez grosses, on les mettra dans des fichiers externes plus tard, que l'ouvrira avec le programme
###############################################################


def nouvelle_partie(Joueur, Donjon, Systeme):
    Systeme["fin_partie"] = False
    Systeme["nom_image"] = ""
    
    Joueur["pos_donjon_X"] = 0
    Joueur["pos_donjon_Y"] = 2
    Joueur["pos_piece_X"] = 0
    Joueur["pos_piece_Y"] = 0
    
    Joueur["Inventaire"] = [False for i in range(100)]  #un tableau de True/False avec une case pour chaque objet
    Joueur["Noms_objet"] = ["la patate", "une épée", "un bouclier", "un anneau", "une gemme flamboyante", "l'Épée de Feu"]
    # attention à rajouter un elif dans obtenir_objet si on rajoute un objet !
    
    Joueur["Statut"] = [20, 20, 0, 0, 0, 0] #le statut du joueur : vie, vie max, or, bonus attaque, armure, bonus soins
    Joueur["Ancien_statut"] = Joueur["Statut"][:] #pour garder une trace de la variation
    # 0: points de vie ; 1: PVs max, 2: or, 3: bonus d'attaque, 4: armure (réuction de dégats), 5: bonus aux soins
    Joueur["derniere_action"] = ["", 0, False] # phrase, durée, afficher avant la description (nb: afficher avant la description a été désactivé, durée pas implémenté)
    Joueur["creature_combatue"] = False # contient le nom de la creature combattu si en combat, False sinon
    Joueur["actions_supplementaires"] = [] #se réinitialise à chaque affichage
    Joueur["actions_persistantes"] = [] #même chose (structure légèrement différente) mais qui ne se réinitialise pas à chaque affichage
    Joueur["question"] = "Bienvenue dans le donjon ! " + colorer("Que voulez-vous faire ? ", "jaune")
    
    
    Joueur["Statut_ennemi"] = [0 for i in range(4)] ##le statut de l'ennemi combattu : 0: vie, 1: dés min, 2: dés max, 3: or laché ou objet si une chaine de caractère
    # vaut "Dialogue" si on es en dialogue plutôt qu'en combat
    Joueur["Ancien_statut_ennemi"] = Joueur["Statut_ennemi"][:] #pour garder une trace de la variation
    
    Donjon["Donjon1"] = [   [ 0, 0, 7, 0, 0 ],
                            [ 2, 0, 6, 8, 9 ],
                            [ 1, 3, 5, 0, 0 ],
                            [ 0, 4, 0, 0, 0 ]   ]
    
    Donjon["piece"] =   [   ["", "", []],
                            ["Entrée du donjon", "La première pièce vous submerge d'un sentiment d'oppression.", []],
                            ["Pièce du vendeur", "Vous apercevez un marchand ambulant, présence surréaliste dans un pareil endroit.", []],
                            ["Pièce du lapin", "La salle semble vide, mais vous vous sentez observé...", []],
                            ["Salle du coffre", "Un coffre trône au centre de la salle.", []],
                            ["Salle du gobelin", "Une créature, au fond de la salle, vous regarde fixement.", []],
                            ["Salle de l'Orc", "Cette salle est plus sombre que les autres. Vous entendez le souffle oppressant d'une créature non loin de vous.", []],
                            ["Salle merveilleuse", "Cette salle vous emplie d'un sentiment de bien être.", []],
                            ["Salle du Gardien", "Cette salle est bien éclairée contrairement aux autres. Une énorme porte vous fait face. Devant elle, un squelette lourdement armé, le gardien du donjon.", []],
                            ["Salle de Sheppler", "Vous poussez avec difficulté la lourde porte de pierre...", []]
                        ]
    
    # un choix : de la forme [ "description de l'action pour l'écran des actions possible = truc à taper qui permettent ce choix", fonction à déclencher ]
    # un objet : de la forme [ "description de l'objet", "caractère représentatif", [choix ajoutés] ]
    Porte_entree = ["la porte de l'entrée du donjon", colorer('>', "noir", "cyan"), [["sortir du donjon", sortir_donjon]]]
    Porte_haut = ["une porte menant vers le nord", colorer('┬', "cyan"), [["ouvrir la porte nord", deplacer_haut]]]
    Porte_droite = ["une porte menant vers l'est", colorer('┤', "cyan"), [["ouvrir la porte est", deplacer_droite]]]
    Porte_bas = ["une porte menant vers le sud", colorer('┴', "cyan"), [["ouvrir la porte sud", deplacer_bas]]]
    Porte_gauche = ["une porte menant vers l'ouest", colorer('├', "cyan"), [["ouvrir la porte ouest", deplacer_gauche]]]
    Porte_bas_vers_coffre = ["une porte menant vers le sud", colorer('┴', "cyan"), [["ouvrir la porte sud", deplacer_salle_coffre]]]
    Porte_droite_boss = ["une porte menant vers l'est", colorer('┤', "cyan"), [["ouvrir la porte est", deplacer_salle_shlepper]]]
    Coffre = ["un enorme coffre en bois", colorer('C', "violet"), [["ouvrir le coffre", ouvrir_coffre1]]]
    Butin_Shlepper = ["ce qui s'apparente au butin du maître des lieux", colorer('C', "violet"), [["s'emparrer du butin", ouvrir_coffre1]]]
    
    # une créature : de la forme [ "description", "caractère représentatif", [choix ajoutés], "nom du monstre", est agressif ? ]
    # NB: l'élément d'indice 3 ("nom du monstre") doit correspondre au nom du fichier de son visuel, et se retrouvera dans la variable creature_combature et dans certaines phrases de combat.
    Vendeur = ["le vendeur ambulant", colorer('V', "vert"), [["parler au vendeur", commercer]], "le Vendeur", False]
    Gobelin = ["un affreux gobelin", colorer('G', "rouge"), [["combattre le gobelin", lambda: combattre("le gobelin")]], "le gobelin", True] #on crée une fonction qui fait combattre("le gobelin"). Je n'ai trouvé que ce moyen pour stocker une fonction avec des paramètres dans une variable.
    Orc = ["un guerrier orc", colorer('O', "rouge"), [["combattre le guerrier orc", lambda: combattre("l'orc")]], "l'orc", True]
    Licorne = ["un rayonnement multicolore", colorer('L',"rouge"), [["avancer vers l'aura multicolore", lambda: combattre("la licorne")]], "la licorne", True]
    Lapin = ["une petite ombre se trémousser", colorer('L',"rouge"), [["avancer vers un potentiel ennemi", lambda: combattre("le lapin")]], "le lapin", True]
    Squelette = ["un garde squelette", colorer('S', "rouge"), [["combattre le garde squelette", lambda: combattre("le squelette")]], "le squelette", True]
    Shlepper = ["le terriible Shlepper", colorer('§', "rouge"), [], "Shlepper", False] #description et aggro dans sa fonction dédiée
    
    Donjon["Pieces"] =  [   [ [], [] ],
                            # [ liste des objets, liste des créatures (aliées ou pas) ]
                            # les actions possibles sont rajoutées par chaque objet/créature présent. La piece elle-même est traitée a part dans la liste Donjon["piece"].
                            # on pourra traiter la pièce comme un objet, que l'on placera conventionnellement en premier dans la pièce, afin de se passer de Donjon["piece"]
                            [ [[Porte_entree, -7, 0], [Porte_haut, 0, -3], [Porte_droite, 7, 0]], [] ],                             #Salle1
                            [ [[Porte_bas, 0, 3]], [[Vendeur, -1, -1]] ],                                                           #Salle2
                            [ [[Porte_gauche, -7, 0], [Porte_droite, 7, 0], [Porte_bas_vers_coffre, 0, 3]], [[Lapin, 5, 2]] ],      #Salle3
                            [ [[Porte_haut, 0, -3], [Coffre, 0, 2]], [] ],                                                          #Salle4
                            [ [[Porte_gauche, -7, 0], [Porte_haut, 0, -3]], [[Gobelin, -5, -1]] ],                                  #Salle5
                            [ [[Porte_droite, 7, 0], [Porte_haut, 0, -3], [Porte_bas, 0, 3]], [[Orc, 2, 0]] ],                      #Salle6
                            [ [[Porte_bas, 0, 3]], [[Licorne, 0, -2]] ],                                                            #Salle7
                            [ [[Porte_droite_boss, 7, 0], [Porte_gauche, -7, 0]], [[Squelette, 6, 0]] ],                            #Salle8
                            [ [[Butin_Shlepper, 5, 0], [Porte_gauche, -7, 0]], [[Shlepper, 0, 0]] ]                                 #Salle9
                        ]
    # pour accéder à la pièce où se trouve le perso : simple ! si x = Joueur["pos_donjon_X"] et y = Joueur["pos_donjon_"], Donjon["Pieces"] [ Donjon["Donjon1"] [x][y] ]
    
    Donjon["objets_en_vente"] = [
        ["une épée", 10, "cette épée de très bonne facture sur laquelle je peux vous faire un bon prix", "Excellent choix, cette épée vous aidera à triompher de vos adversaires !"],
        ["un bouclier", 5, "ou ce petit bouclier, si vous préferez vous protéger", "Excellent choix, ce bouclier vous permettra de survivre aux attaques mortelles de vos adversaires !"]
                                ]


Joueur = {}
Donjon = {}
Systeme = {}

Systeme["couleur_par_defaut"] = "blanc"
Systeme["fond_par_defaut"] = "noir"
Systeme["caractere_joueur"] = colorer('@', "jaune")
Systeme["caractere_mur"] = '#'
Systeme["caractere_donjon_joueur"] = colorer('@', "jaune")
Systeme["caractere_donjon_piece"] = colorer('#', "noir", "blanc")
Systeme["caractere_special"] = '&' #utilisé par le programme : à ne pas utiliser pour autre chose

Systeme["nombre_de_lettres_X"] = 113
Systeme["nombre_de_lettres_Y"] = 36 #sans la ligne d'input
# normalement X = 132, Y = 42



###############################################################
# programme :
###############################################################

Systeme["quitter"] = False
Systeme["fin_partie"] = False
while not Systeme["quitter"]: # on relance le jeu à chaque game over / victoire
    centrer_et_afficher_ecran_titre()
    nouvelle_partie(Joueur, Donjon, Systeme)
    boucle_de_jeu()
