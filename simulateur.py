# simulateur.py
from typing import Tuple, Dict, Set
from turing import MachineTuring, lire_turing, Symbole, Etat as EtatTuring
from automate import AutomateCellulaire, Configuration as ConfigAutomate, State as EtatAutomate

# --- Construction de l'automate cellulaire simulant la MT (Q13) ---

# Type pour l'état de l'automate cellulaire simulant une MT
# C'est une paire (marqueur, symbole_ruban), où marqueur est '*' ou un état de la MT.
EtatAutomateSimu = Tuple[str, Symbole]
SymboleDefautAutomateSimu = ("*", "□") # Doit correspondre au symbole defaut de la MT

def construire_automate_depuis_turing(mt: MachineTuring) -> AutomateCellulaire:
    """
    Construit l'automate cellulaire A qui simule la machine de Turing M. (Q13)
    L'automate A travaille sur l'espace d'états (Q U {*}) x Sigma.
    Une configuration de A comme (*,l0),...,(q,li),...,(*,ln) représente
    la configuration de M : (q, i, l0...ln).
    """
    if mt.symbole_defaut != '□':
         print("Avertissement: La construction suppose symbole_defaut='□' pour la MT.", file=sys.stderr)

    marqueur_normal = "*"
    symbole_defaut_mt = mt.symbole_defaut
    etat_defaut_ac: EtatAutomateSimu = (marqueur_normal, symbole_defaut_mt)

    # Ensemble des états de l'automate cellulaire A
    etats_ac: Set[EtatAutomateSimu] = set()
    etats_ac.add(etat_defaut_ac)
    for etat_mt in mt.etats:
        for symbole in mt.alphabet_travail:
            etats_ac.add((etat_mt, symbole)) # État avec tête
            etats_ac.add((marqueur_normal, symbole)) # État sans tête

    # Fonction de transition de l'automate cellulaire A
    transitions_ac: Dict[Tuple[EtatAutomateSimu, EtatAutomateSimu, EtatAutomateSimu], EtatAutomateSimu] = {}

    # 1. Règle pour les cellules non survolées par la tête (Source 44)
    # f((*, l1), (*, l2), (*, l3)) = (*, l2)
    # Le centre ne change pas si personne n'a la tête autour.
    for l1 in mt.alphabet_travail:
        for l2 in mt.alphabet_travail:
            for l3 in mt.alphabet_travail:
                voisinage = ((marqueur_normal, l1), (marqueur_normal, l2), (marqueur_normal, l3))
                transitions_ac[voisinage] = (marqueur_normal, l2) # Le centre reste (*, l2)

    # 2. Règles pour simuler les transitions de la MT (Source 45)
    # On itère sur chaque transition de la MT : (q, s) -> (q', s', D)
    for (q, s), (q_prime, s_prime, direction) in mt.transitions.items():

        # Pour chaque symbole possible à gauche (l1) et à droite (l3) de la tête
        for l1 in mt.alphabet_travail:
            for l3 in mt.alphabet_travail:

                # Le voisinage où la tête est au centre
                voisinage_centre_tete = ((marqueur_normal, l1), (q, s), (marqueur_normal, l3))

                # Le voisinage où la tête est à gauche (utile pour déplacement L)
                voisinage_gauche_tete = ((q, s), (marqueur_normal, l1), (marqueur_normal, l3)) # l1 est au centre ici

                # Le voisinage où la tête est à droite (utile pour déplacement R)
                voisinage_droite_tete = ((marqueur_normal, l1), (marqueur_normal, l3), (q, s)) # l3 est au centre ici


                if direction == 'N':
                    # La tête reste sur la cellule centrale, met à jour état et symbole.
                    # f( (*,l1), (q,s), (*,l3) ) = (q', s')
                    transitions_ac[voisinage_centre_tete] = (q_prime, s_prime)

                elif direction == 'R':
                    # La tête se déplace vers la droite.
                    # a) La cellule centrale perd la tête et change de symbole.
                    #    f( (*,l1), (q,s), (*,l3) ) = (*, s')
                    transitions_ac[voisinage_centre_tete] = (marqueur_normal, s_prime)

                    # b) La cellule de droite reçoit la tête (avec le nouvel état q'). Son symbole l3 ne change pas.
                    #    Pour que la cellule de droite (l3) devienne (q', l3), il faut que son voisinage
                    #    dans l'étape *actuelle* mène à cet état. Son voisinage est ((q,s), (*,l3), (*,l4))
                    #    On doit donc définir f( (q,s), (*,l3), (*,l4) ) = (q', l3) pour tout l4.
                    for l4 in mt.alphabet_travail:
                         voisinage_pour_droite = ((q, s), (marqueur_normal, l3), (marqueur_normal, l4))
                         transitions_ac[voisinage_pour_droite] = (q_prime, l3)

                elif direction == 'L':
                    # La tête se déplace vers la gauche.
                    # a) La cellule centrale perd la tête et change de symbole.
                    #    f( (*,l1), (q,s), (*,l3) ) = (*, s')
                    transitions_ac[voisinage_centre_tete] = (marqueur_normal, s_prime)

                    # b) La cellule de gauche reçoit la tête (avec le nouvel état q'). Son symbole l1 ne change pas.
                    #    Pour que la cellule de gauche (l1) devienne (q', l1), il faut que son voisinage
                    #    dans l'étape *actuelle* mène à cet état. Son voisinage est ((*,l0), (*,l1), (q,s))
                    #    On doit donc définir f( (*,l0), (*,l1), (q,s) ) = (q', l1) pour tout l0.
                    for l0 in mt.alphabet_travail:
                         voisinage_pour_gauche = ((marqueur_normal, l0), (marqueur_normal, l1), (q, s))
                         transitions_ac[voisinage_pour_gauche] = (q_prime, l1)

    # Création de l'instance de l'Automate Cellulaire
    # Le symbole par défaut de l'automate est la paire ('*', symbole_defaut_mt)
    automate_simu = AutomateCellulaire(etats_ac, transitions_ac, etat_defaut_ac)

    return automate_simu


def creer_config_automate_pour_mt(mt: MachineTuring, mot_entree: str, contexte: int = 2) -> ConfigAutomate:
    """Crée la configuration initiale de l'automate cellulaire pour simuler la MT sur un mot."""
    config_etats: List[EtatAutomateSimu] = []
    marqueur_normal = "*"
    symbole_defaut_mt = mt.symbole_defaut
    etat_defaut_ac: EtatAutomateSimu = (marqueur_normal, symbole_defaut_mt)

    # Ajoute du contexte vide au début
    config_etats.extend([etat_defaut_ac] * contexte)

    # Ajoute le mot d'entrée, avec la tête sur le premier symbole
    for i, symbole in enumerate(mot_entree):
        if i == 0: # Place la tête ici
            config_etats.append((mt.etat_initial, symbole))
        else:
            config_etats.append((marqueur_normal, symbole))

    # Gérer le cas du mot vide : placer la tête sur un symbole par défaut
    if not mot_entree:
         config_etats.append((mt.etat_initial, symbole_defaut_mt))

    # Ajoute du contexte vide à la fin
    config_etats.extend([etat_defaut_ac] * contexte)

    return ConfigAutomate(config_etats)

# --- Exemple d'utilisation ---
if __name__ == "__main__":
    print("Exécution de l'exemple de simulateur.py")

    # 1. Lire la machine de Turing
    try:
        mt_test = lire_turing("machines_turing/incrementeur.txt") # Ou une autre MT simple
        print("Machine de Turing lue pour la simulation par automate.")
    except Exception as e:
        print(f"Erreur lors de la lecture de la MT : {e}")
        sys.exit(1)

    # 2. Construire l'automate cellulaire équivalent
    try:
        automate_equivalent = construire_automate_depuis_turing(mt_test)
        print(f"Automate cellulaire construit : {len(automate_equivalent.etats)} états, {len(automate_equivalent.fonction_transition)} transitions.")
    except Exception as e:
        print(f"Erreur lors de la construction de l'automate : {e}")
        sys.exit(1)

    # 3. Simuler la MT et l'Automate sur une entrée et comparer (visuellement)
    mot_test = "11"
    print(f"\nSimulation comparative sur l'entrée '{mot_test}'")

    print("\n--- Simulation MT Directe ---")
    try:
        resultat_mt, config_mt_finale, n_pas_mt = simuler_turing(mt_test, mot_test, max_steps=30, afficher=True)
        print(f"Résultat MT: {resultat_mt} en {n_pas_mt} pas.")
    except Exception as e:
        print(f"Erreur simulation MT: {e}")


    print("\n--- Simulation via Automate Cellulaire ---")
    from automate import simuler_automate, afficher_simulation # Import local pour l'exemple

    try:
        config_ac_init = creer_config_automate_pour_mt(mt_test, mot_test, contexte=5)
        print(f"Config AC initiale: {config_ac_init}")

        # Simuler l'automate (suffisamment de pas pour correspondre à la MT)
        # Attention: 1 pas de MT peut nécessiter 1 ou 2 pas d'AC selon l'implémentation exacte
        # Prenons une marge. Si la MT prend N pas, simulons l'AC pour ~2N pas.
        pas_ac_necessaires = n_pas_mt * 2 + 10 # Marge de sécurité
        historique_ac = simuler_automate(automate_equivalent, config_ac_init, mode="steps", valeur=pas_ac_necessaires, max_steps=pas_ac_necessaires+10)

        # Affichage amélioré pour l'automate simulant la MT
        def mapping_simu(etat: EtatAutomateSimu) -> str:
             marqueur, symbole = etat
             base_char = {'□': '_', '0': '0', '1': '1'}.get(symbole, '?')
             if marqueur != '*': # C'est la tête
                 #return f"[{base_char}]" # Ou avec l'état : f"[{marqueur}:{base_char}]"
                 return base_char.upper() # Symbole en majuscule pour voir la tête
             else:
                 return base_char

        # Crée le dictionnaire de mapping dynamique basé sur les états présents
        mapping_ac_simu = {etat: mapping_simu(etat) for etat in automate_equivalent.etats}

        print(f"\nAffichage simulation AC (Mapping: Tête=MAJ, _:□):")
        afficher_simulation(historique_ac, mapping_etats=mapping_ac_simu)
        # Sauvegarde aussi dans un fichier pour analyse
        afficher_simulation(historique_ac, mapping_etats=mapping_ac_simu, fichier_sortie="simulation_ac_depuis_mt.txt")
        print("Sortie AC sauvegardée dans simulation_ac_depuis_mt.txt")

        # TODO Q13: Ajouter une fonction pour vérifier formellement que le résultat final
        # de la simulation AC correspond à la configuration finale de la MT.

    except Exception as e:
        print(f"Erreur simulation via AC: {e}")