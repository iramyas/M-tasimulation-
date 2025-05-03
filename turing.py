# turing.py
from typing import Dict, Tuple, List, Set, Optional, Any
import sys

# --- Types (inspiré de Q8) ---
Etat = str
Symbole = str # Doit être un seul caractère ou un objet comparable simple. Alphabet={0, 1, □} (Source 31)
Direction = str  # 'L', 'R' ou 'N' (Gauche, Droite, Neutre/Stay)

# Transition: clé = (état actuel, symbole lu), valeur = (nouvel état, symbole écrit, direction)
TransitionTuring = Dict[Tuple[Etat, Symbole], Tuple[Etat, Symbole, Direction]]

# --- Structures de données (Q8, Q9) ---

class MachineTuring:
    """Représente une Machine de Turing."""
    def __init__(self,
                 etats: Set[Etat],
                 alphabet_travail: Set[Symbole], # Sigma U {□}
                 transitions: TransitionTuring,
                 etat_initial: Etat,
                 etats_accept: Set[Etat],
                 etats_reject: Set[Etat], # Ajout pour Q12
                 symbole_defaut: Symbole = '□'):
        """
        Initialise la Machine de Turing.

        Args:
            etats: Ensemble fini des états (Q).
            alphabet_travail: Ensemble des symboles utilisables sur le ruban (incluant '□').
            transitions: Fonction de transition (delta).
            etat_initial: L'état de départ (q0).
            etats_accept: Ensemble des états d'acceptation (F_accept).
            etats_reject: Ensemble des états rejets (F_reject).
            symbole_defaut: Symbole représentant une case vide ('□').
        """
        self.etats = etats
        self.alphabet_travail = alphabet_travail
        self.transitions = transitions
        self.etat_initial = etat_initial
        self.etats_accept = etats_accept
        self.etats_reject = etats_reject
        self.symbole_defaut = symbole_defaut

        # Validation
        if etat_initial not in etats:
            raise ValueError(f"État initial '{etat_initial}' n'est pas dans l'ensemble des états.")
        if not etats_accept.issubset(etats):
            raise ValueError(f"États acceptants {etats_accept - etats} non valides.")
        if not etats_reject.issubset(etats):
            raise ValueError(f"États rejets {etats_reject - etats} non valides.")
        if not etats_accept.isdisjoint(etats_reject):
             raise ValueError("Les états acceptants et rejets doivent être disjoints.")
        if symbole_defaut not in alphabet_travail:
             raise ValueError(f"Symbole par défaut '{symbole_defaut}' doit être dans l'alphabet de travail.")
        # On pourrait aussi valider que toutes les transitions utilisent des états/symboles valides.


class ConfigurationTuring:
    """Représente la configuration instantanée d'une Machine de Turing."""
    def __init__(self,
                 bande: Dict[int, Symbole], # Ruban: dictionnaire position -> symbole
                 tete: int,                  # Position de la tête de lecture/écriture
                 etat: Etat,                 # État actuel de l'automate fini
                 symbole_defaut: Symbole = '□'):
        self.bande = bande
        self.tete = tete
        self.etat = etat
        self.symbole_defaut = symbole_defaut # Nécessaire pour lire les cases vides

    def __str__(self) -> str:
        """Représentation textuelle de la configuration pour l'affichage."""
        try:
            # Gérer le cas d'une bande initialement vide
            if not self.bande:
                min_i = self.tete
                max_i = self.tete
            else:
                min_i = min(self.bande.keys())
                max_i = max(self.bande.keys())

            # Étendre légèrement la vue pour le contexte
            view_min = min(min_i, self.tete) - 5
            view_max = max(max_i, self.tete) + 5

            bande_str_list = []
            for i in range(view_min, view_max + 1):
                sym = self.bande.get(i, self.symbole_defaut)
                if i == self.tete:
                    bande_str_list.append(f'[{sym}]')
                else:
                    bande_str_list.append(f' {sym} ')

            bande_str = ''.join(bande_str_list).strip()
            return f"Etat: {self.etat:<5} | Tête: {self.tete:<3} | Bande: ...{bande_str}..."

        except Exception as e:
             # En cas d'erreur (ex: bande non initialisée), fournir une info minimale
             return f"Etat: {self.etat} | Tête: {self.tete} | Bande: (erreur affichage: {e})"

    def lire_symbole(self) -> Symbole:
        """Retourne le symbole sous la tête."""
        return self.bande.get(self.tete, self.symbole_defaut)

    def ecrire_symbole(self, symbole: Symbole):
        """Écrit un symbole sur la bande à la position de la tête."""
        self.bande[self.tete] = symbole

    def deplacer_tete(self, direction: Direction):
        """Déplace la tête de lecture/écriture."""
        if direction == "R":
            self.tete += 1
        elif direction == "L":
            self.tete -= 1
        elif direction == "N":
            pass # Ne bouge pas
        else:
            raise ValueError(f"Direction invalide : '{direction}'")


# --- Lecture et Simulation (Q10, Q11, Q12) ---

def lire_turing(fichier: str) -> MachineTuring:
    """
    Reads the definition of a Turing Machine from a file. (Q10)
    Expected format per line: "current_state,symbol_read,new_state,symbol_written,direction"
    Conventions for implicit information (must be specified in the file or here):
      - Initial state: 'q0' (can be overridden by a special line "# initial: qX")
      - Accepting states: 'ACCEPT' (can be overridden by "# accept: qA,qB")
      - Reject states: 'REJECT' (can be overridden by "# reject: qR")
      - Alphabet: {0, 1, □} (can be overridden by "# alphabet: a,b,c,□")
      - Default symbol: '□'
    Empty lines are ignored.
    Lines starting with '#' are directives or full-line comments.
    Comments at the end of a rule line (# ...) are also ignored.
    """
    transitions: TransitionTuring = {}
    etats_vus: Set[Etat] = set()
    alphabet_vus: Set[Symbole] = {'0', '1', '□'} # Base requise par l'énoncé (Source 31)
    symbole_defaut: Symbole = '□'
    etat_initial: Etat = "q0"
    etats_accept: Set[Etat] = {"ACCEPT"}
    etats_reject: Set[Etat] = {"REJECT"}

    try:
        with open(fichier, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue # Ignore empty lines

                if ligne.startswith("#"):
                    # Process special directives
                    if ligne.startswith("# initial:"):
                        etat_initial = ligne.split(":", 1)[1].strip()
                    elif ligne.startswith("# accept:"):
                        etats_accept = {e.strip() for e in ligne.split(":", 1)[1].split(",")}
                    elif ligne.startswith("# reject:"):
                        etats_reject = {e.strip() for e in ligne.split(":", 1)[1].split(",")}
                    elif ligne.startswith("# alphabet:"):
                        alphabet_vus = {s.strip() for s in ligne.split(":", 1)[1].split(",")}
                        if symbole_defaut not in alphabet_vus:
                             print(f"Avertissement: Symbole défaut '{symbole_defaut}' non listé dans l'alphabet explicite.", file=sys.stderr)
                             alphabet_vus.add(symbole_defaut) # On s'assure qu'il y est
                    # Ignore other full-line comments
                    continue

                # --- FIX: Remove end-of-line comments from rule lines ---
                # Only do this if it's not a directive line (already handled above)
                comment_index = ligne.find("#")
                if comment_index != -1:
                    ligne = ligne[:comment_index].strip()
                    if not ligne: # If the line was only a rule followed by a comment
                         continue
                # --- End FIX ---


                # Reading a transition
                try:
                    # Now 'ligne' should only contain the transition parts
                    parts = [part.strip() for part in ligne.split(",")]
                    if len(parts) != 5:
                         raise ValueError(f"Expected 5 parts for a transition, found {len(parts)}")

                    e1, s1, e2, s2, d = parts
                    direction = d.upper() # Accepter L, R, N en minuscule ou majuscule

                    if direction not in ['L', 'R', 'N']:
                         raise ValueError(f"Invalid direction '{d}'")

                    # Clé et Valeur de la transition
                    cle: Tuple[Etat, Symbole] = (e1, s1)
                    valeur: Tuple[Etat, Symbole, Direction] = (e2, s2, direction)

                    if cle in transitions:
                         # Optional: Warning for duplicate transitions
                         # print(f"Warning: Transition for {cle} redéfinie on line '{ligne}'", file=sys.stderr)
                         pass # Or handle as an error

                    transitions[cle] = valeur

                    # Collecter états et symboles vus
                    etats_vus.update([e1, e2])
                    alphabet_vus.update([s1, s2])

                except ValueError as e:
                    print(f"Erreur de format dans le fichier '{fichier}' ligne '{ligne}': {e}", file=sys.stderr)
                    continue # Ignore la ligne mal formée

    except FileNotFoundError:
        print(f"Erreur: Fichier machine Turing '{fichier}' non trouvé.", file=sys.stderr)
        raise

    # Ajouter les états spéciaux à l'ensemble des états s'ils ne sont pas déjà présents via les transitions
    etats_vus.add(etat_initial)
    etats_vus.update(etats_accept)
    etats_vus.update(etats_reject)

    # S'assurer que l'alphabet de travail inclut bien 0, 1, □
    alphabet_vus.update({'0', '1', '□'})

    try:
        return MachineTuring(etats_vus, alphabet_vus, transitions, etat_initial, etats_accept, etats_reject, symbole_defaut)
    except ValueError as e:
         print(f"Erreur lors de la création de la Machine de Turing: {e}", file=sys.stderr)
         # On pourrait retourner None ou relancer une exception spécifique
         raise


def pas_turing(machine: MachineTuring, config: ConfigurationTuring) -> Optional[ConfigurationTuring]:
    """
    Effectue un pas de calcul de la Machine de Turing. (Q11)

    Args:
        machine: La MachineTuring.
        config: La ConfigurationTuring actuelle.

    Returns:
        La nouvelle ConfigurationTuring après un pas, ou None si la machine est bloquée
        (aucune transition définie pour l'état et le symbole actuels).
        Ne modifie PAS la configuration d'origine, retourne une nouvelle instance (ou la même si bloquée?).
        Décision: Modifie la configuration en place pour la performance (comme souvent fait).
                  Retourne la config modifiée ou la config originale si bloquée.
    """
    etat_actuel = config.etat
    symbole_lu = config.lire_symbole()
    cle_transition: Tuple[Etat, Symbole] = (etat_actuel, symbole_lu)

    if cle_transition not in machine.transitions:
        # Machine bloquée in a non-final state
        return None # Signal d'arrêt par blocage

    # Appliquer la transition
    nouvel_etat, symbole_ecrit, direction = machine.transitions[cle_transition]

    config.ecrire_symbole(symbole_ecrit)
    config.etat = nouvel_etat
    config.deplacer_tete(direction)

    return config # Retourne la configuration modifiée


def simuler_turing(machine: MachineTuring, mot_entree: str, max_steps: int = 1000, afficher: bool = True) -> Tuple[str, ConfigurationTuring, int]:
    """
    Simule l'exécution de la Machine de Turing sur un mot d'entrée. (Q12)
    Stops if the machine reaches an ACCEPT, REJECT state, gets blocked, or exceeds max_steps.

    Args:
        machine: The MachineTuring to simulate.
        mot_entree: The initial word on the tape.
        max_steps: Maximum number of steps to prevent infinite loops.
        afficher: If True, displays each simulation step.

    Returns:
        A tuple containing:
          - The result ("ACCEPTED", "REJECTED", "BLOCKED", "MAX_STEPS")
          - The final configuration.
          - The number of steps performed.
    """
    # Initialize configuration
    bande: Dict[int, Symbole] = {i: symbole for i, symbole in enumerate(mot_entree)}
    config = ConfigurationTuring(bande, tete=0, etat=machine.etat_initial, symbole_defaut=machine.symbole_defaut)

    if afficher:
        print("--- Simulation Machine de Turing ---")
        print(f"Input word: '{mot_entree}'")
        print(f"Initial configuration: {config}")
        print("-" * 30)

    nb_pas = 0
    while nb_pas < max_steps:
        # Check if in a final state before taking a step
        # Moved check here to report final state immediately upon reaching it
        if config.etat in machine.etats_accept:
            if afficher: print("--- Etat ACCEPT atteint ---")
            return "ACCEPTED", config, nb_pas
        if config.etat in machine.etats_reject:
            if afficher: print("--- Etat REJECT atteint ---")
            return "REJECTED", config, nb_pas


        # Perform one step
        # Note: pas_turing modifies config in place
        config_suivante = pas_turing(machine, config)

        if config_suivante is None:
            # Machine blocked
            if afficher: print("--- Machine BLOQUEE (pas de transition) ---")
            return "BLOCKED", config, nb_pas

        # config was updated by pas_turing, proceed to next step
        nb_pas += 1
        if afficher:
            print(f"Pas {nb_pas}: {config}")

    # If the loop exits, max_steps was reached
    if afficher: print(f"--- Limite de {max_steps} pas atteinte ---")
    return "MAX_STEPS", config, nb_pas


# --- Exemple d'utilisation ---
if __name__ == "__main__":
    print("Exécution de l'exemple de turing.py")

    # 1. Lire la machine depuis un fichier
    try:
        # Assurez-vous que ce fichier existe et est correctement formaté
        # et qu'il définit bien les états accept/reject ou utilise les conventions
        mt = lire_turing("machines_turing/incrementeur.txt") # exemple
        print("Machine de Turing lue.")
        print(f"  Etat initial: {mt.etat_initial}")
        print(f"  Etats accept: {mt.etats_accept}")
        print(f"  Etats reject: {mt.etats_reject}")
        print(f"  Nombre de transitions: {len(mt.transitions)}")
    except Exception as e:
        print(f"Erreur lors de la lecture de la machine : {e}")
        sys.exit(1)

    # 2. Simuler sur un mot d'entrée
    mot = "101" # Exemple
    print(f"\nSimulation de la machine sur l'entrée '{mot}':")
    try:
        resultat, config_finale, n_pas = simuler_turing(mt, mot, max_steps=100, afficher=True)

        print("-" * 30)
        print(f"Résultat final: {resultat}")
        print(f"Nombre de pas: {n_pas}")
        print(f"Configuration finale: {config_finale}")

    except Exception as e:
        print(f"Erreur pendant la simulation : {e}")