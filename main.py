# main.py
import argparse
import sys
import os

# Importer les fonctions nécessaires depuis les autres modules
try:
    from automate import (
        lire_automate, Configuration as ConfigAutomate,
        simuler_automate, afficher_simulation, State # Import State for mapping type hint
    )
    from turing import (
        lire_turing, simuler_turing, ConfigurationTuring, MachineTuring
    )
    from simulateur import (
        construire_automate_depuis_turing, creer_config_automate_pour_mt,
        EtatAutomateSimu # Import type for mapping
    )
except ImportError as e:
    print(f"Erreur d'importation: {e}", file=sys.stderr)
    print("Vérifiez que les fichiers automate.py, turing.py, simulateur.py sont dans le même répertoire ou accessibles.", file=sys.stderr)
    sys.exit(1)

# --- Fonctions pour chaque type de simulation ---

def executer_simulation_automate(args):
    """Lance la simulation d'un automate cellulaire."""
    print(f"--- Simulation Automate Cellulaire ({args.automate_file}) ---")
    try:
        # Check file existence here after parsing
        if not os.path.exists(args.automate_file):
             print(f"Erreur: Fichier automate '{args.automate_file}' introuvable.", file=sys.stderr)
             sys.exit(1)

        automate = lire_automate(args.automate_file)
        config_init = ConfigAutomate(list(args.input_word))
        print(f"Config initiale: {config_init}")

        # Choisir le mode et la valeur
        mode_simu = args.mode
        valeur_simu = args.value
        if mode_simu == "steps":
             # Ensure value is an integer for steps mode
             try:
                 valeur_simu = int(args.value) if args.value is not None else 10 # Valeur par défaut pour steps
             except (ValueError, TypeError):
                  print(f"Erreur: La valeur pour le mode 'steps' doit être un entier. Reçu: '{args.value}'", file=sys.stderr)
                  sys.exit(1) # Exit if value is incorrect
        elif mode_simu == "stable":
             valeur_simu = None # Pas de valeur numérique pour stable
        # elif mode_simu == "transition": # Non implémenté dans l'exemple
        #      print("Mode 'transition' non supporté dans cette interface.", file=sys.stderr)
        #      return # Or sys.exit(1)
        else:
             # This case should ideally not be reached due to choices= in argparse
             print(f"Mode '{mode_simu}' non reconnu pour automate.", file=sys.stderr)
             sys.exit(1)


        historique = simuler_automate(
            automate,
            config_init,
            mode=mode_simu,
            valeur=valeur_simu,
            max_steps=args.max_steps
        )

        # Préparer le mapping d'affichage si fourni
        mapping: Optional[Dict[State, str]] = None # Use the imported State type
        if args.mapping:
             try:
                 # Exemple de format pour --mapping: "0: ,1:█,□:."
                 # Split by comma, then each item by colon
                 mapping = {}
                 for item in args.mapping.split(","):
                     if ":" in item:
                         key, val = item.split(":", 1) # Split only on the first colon
                         mapping[key.strip()] = val.strip()
                     else:
                         # Handle cases like just "□" or "1" if needed, though format suggests key:value
                         print(f"Avertissement: Format de mapping invalide pour l'élément '{item}'. Ignoré.", file=sys.stderr)

                 print(f"Utilisation du mapping d'affichage: {mapping}")
             except Exception as e:
                 print(f"Erreur lors du parsing du mapping '{args.mapping}': {e}. Utilisation du défaut.", file=sys.stderr)
                 mapping = None # Revenir au défaut


        afficher_simulation(
            historique,
            pas_intervalle=args.display_interval,
            fichier_sortie=args.output_file,
            mapping_etats=mapping
        )
        if args.output_file:
            print(f"Résultat de la simulation sauvegardé dans '{args.output_file}'")

    except FileNotFoundError:
        # This might be caught by the os.path.exists check now, but keep for robustness
        print(f"Erreur: Fichier automate '{args.automate_file}' non trouvé.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
         print(f"Erreur de valeur: {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue lors de la simulation de l'automate: {e}", file=sys.stderr)
        sys.exit(1)


def executer_simulation_turing(args):
    """Lance la simulation d'une machine de Turing."""
    print(f"--- Simulation Machine de Turing ({args.turing_file}) ---")
    try:
        # Check file existence here after parsing
        if not os.path.exists(args.turing_file):
             print(f"Erreur: Fichier machine Turing '{args.turing_file}' introuvable.", file=sys.stderr)
             sys.exit(1)

        machine = lire_turing(args.turing_file)
        mot = args.input_word
        print(f"Simulation sur le mot d'entrée: '{mot}'")

        resultat, config_finale, n_pas = simuler_turing(
            machine,
            mot,
            max_steps=args.max_steps,
            afficher=not args.quiet # Affiche si --quiet n'est pas utilisé
        )

        print("-" * 30)
        print(f"Simulation terminée.")
        print(f"Résultat: {resultat}")
        print(f"Pas effectués: {n_pas}")
        print(f"Configuration finale: {config_finale}")

        if args.output_file:
            try:
                with open(args.output_file, "w", encoding="utf-8") as f:
                    f.write(f"Result: {resultat}\n")
                    f.write(f"Steps: {n_pas}\n")
                    f.write(f"Final Config: {config_finale}\n")
                print(f"Résumé de la simulation sauvegardé dans '{args.output_file}'")
            except IOError as e:
                 print(f"Erreur lors de la sauvegarde du résultat: {e}", file=sys.stderr)


    except FileNotFoundError:
        # This might be caught by the os.path.exists check now, but keep for robustness
        print(f"Erreur: Fichier machine Turing '{args.turing_file}' non trouvé.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
         print(f"Erreur de valeur: {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue lors de la simulation de la MT: {e}", file=sys.stderr)
        sys.exit(1)


def executer_simulation_via_automate(args):
    """Lance la simulation d'une MT via un automate cellulaire."""
    print(f"--- Simulation MT ({args.turing_file}) via Automate Cellulaire ---")
    try:
        # Check file existence here after parsing
        if not os.path.exists(args.turing_file):
             print(f"Erreur: Fichier machine Turing '{args.turing_file}' introuvable.", file=sys.stderr)
             sys.exit(1)

        # 1. Lire la MT
        machine_mt = lire_turing(args.turing_file)
        mot = args.input_word
        print(f"Simulation sur le mot d'entrée: '{mot}'")

        # (Optionnel) Simuler la MT directement pour comparaison
        if args.compare:
             print("\n--- (Comparaison) Simulation MT Directe ---")
             res_mt, cfg_mt, n_pas_mt = simuler_turing(machine_mt, mot, max_steps=args.max_steps, afficher=False)
             print(f"Résultat MT directe: {res_mt} en {n_pas_mt} pas.")
             print(f"Config finale MT: {cfg_mt}")
             # Estimer le nombre de pas AC nécessaires
             # Use a more robust estimation or rely on the tm_originale stopping condition
             pas_ac_estimes = max(10, n_pas_mt * 3 + 20) # Heuristique ajustée

        else:
             # If not comparing, we still need a step limit for the AC simulation
             # Use max_steps provided by the user, but the AC sim will stop on TM halt
             pas_ac_estimes = args.max_steps


        print(f"\n--- Simulation via Automate ---")
        # 2. Construire l'Automate Cellulaire
        automate_simu = construire_automate_depuis_turing(machine_mt)
        print(f"Automate équivalent construit.")

        # 3. Créer la configuration AC initiale
        # Use a larger context for robustness, especially with Left movements
        config_ac_init = creer_config_automate_pour_mt(machine_mt, mot, contexte=10) # Increased context
        print(f"Config AC initiale créée (contexte={10}): {config_ac_init}")

        # 4. Simuler l'Automate Cellulaire
        print(f"Simulation de l'automate (max {args.max_steps} pas)...") # Report user's max_steps
        historique_ac = simuler_automate(
            automate_simu,
            config_ac_init,
            mode="steps", # We still use steps mode as a safety net
            valeur=args.max_steps, # Use the user's max_steps as the value limit
            max_steps=args.max_steps, # Use the user's max_steps as the hard limit
            tm_originale=machine_mt # Pass the original MT object to enable halting check
        )

        # 5. Afficher/Sauvegarder le résultat de la simulation AC
        # Mapping spécifique pour la visualisation de la simulation de MT
        def mapping_simu(etat: EtatAutomateSimu) -> str: # Use imported type
             marqueur, symbole = etat
             # Utilise _ pour □, ? pour autre chose non défini
             base_char = {'□': '_', '0': '0', '1': '1'}.get(symbole, '?')
             if marqueur != '*': # C'est la tête
                 # Retourne le symbole en MAJUSCULE pour indiquer la tête
                 return base_char.upper()
             else: # Pas de tête
                 return base_char

        # Create the dynamic mapping dictionary based on the states present
        # Ensure we only try to map tuple states
        mapping_dict: Dict[State, str] = {
            etat: mapping_simu(etat)
            for etat in automate_simu.etats
            if isinstance(etat, tuple) and len(etat) == 2 # Ensure it's the correct tuple format
        }
        # Add the default symbol mapping explicitly if needed
        if automate_simu.symbole_defaut not in mapping_dict:
             mapping_dict[automate_simu.symbole_defaut] = mapping_simu(automate_simu.symbole_defaut)


        print(f"\nAffichage simulation AC (Mapping: Tête=MAJ, _:□):")
        afficher_simulation(
            historique_ac,
            pas_intervalle=args.display_interval,
            fichier_sortie=args.output_file,
            mapping_etats=mapping_dict
        )
        if args.output_file:
            print(f"Résultat de la simulation AC sauvegardé dans '{args.output_file}'")
        else:
            print("\n(Fin de l'affichage de la simulation AC)")

        # You could add a function here to interpret the final AC configuration
        # and compare it formally to the direct MT simulation result if args.compare is True.
        # This would involve finding the head state and the tape content from the final AC config.


    except FileNotFoundError:
        # This might be caught by the os.path.exists check now, but keep for robustness
        print(f"Erreur: Fichier machine Turing '{args.turing_file}' non trouvé.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
         print(f"Erreur de valeur: {e}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue lors de la simulation via automate: {e}", file=sys.stderr)
        sys.exit(1)


# --- Point d'entrée principal ---

def main():
    parser = argparse.ArgumentParser(description="Métasimulateur: Automates Cellulaires et Machines de Turing.")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Type de simulation à exécuter')

    # --- Arguments Communs ---
    # Define common arguments here, but only add them to subparsers where needed
    # Keeping this structure but not using parents
    common_parser_args = argparse.ArgumentParser(add_help=False)
    common_parser_args.add_argument('-i', '--input-word', type=str, required=True, help='Mot d\'entrée pour la simulation.')
    common_parser_args.add_argument('--max-steps', type=int, default=1000, help='Nombre maximum de pas de simulation (défaut: 1000).')
    common_parser_args.add_argument('-o', '--output-file', type=str, default=None, help='Fichier pour sauvegarder la sortie de la simulation.')
    common_parser_args.add_argument('--display-interval', type=int, default=1, help="Afficher la configuration tous les N pas (défaut: 1).")
    common_parser_args.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux, n\'affiche pas les étapes intermédiaires (utile pour MT).')


    # --- Sous-commande pour Automate Cellulaire ---
    # Add common arguments explicitly, defining positional argument first
    parser_ac = subparsers.add_parser('automate', help='Simuler un automate cellulaire.')
    parser_ac.add_argument('automate_file', type=str, help='Fichier décrivant l\'automate cellulaire.') # Positional argument FIRST
    # Add common arguments needed for automate subcommand directly
    parser_ac.add_argument('-i', '--input-word', type=str, required=True, help='Mot d\'entrée pour la simulation.')
    parser_ac.add_argument('--max-steps', type=int, default=1000, help='Nombre maximum de pas de simulation (défaut: 1000).')
    parser_ac.add_argument('-o', '--output-file', type=str, default=None, help='Fichier pour sauvegarder la sortie de la simulation.')
    parser_ac.add_argument('--display-interval', type=int, default=1, help="Afficher la configuration tous les N pas (défaut: 1).")
    # Note: '--quiet' is not typically relevant for AC simulation display, can omit if desired
    # parser_ac.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux (ignored for AC).') # Optional: include but ignore

    parser_ac.add_argument('--mode', type=str, default='steps', choices=['steps', 'stable'], help='Mode d\'arrêt de la simulation (défaut: steps).')
    parser_ac.add_argument('--value', type=str, default='10', help='Valeur pour le mode d\'arrêt (nombre de pas pour "steps").')
    parser_ac.add_argument('--mapping', type=str, default=None, help='Mapping pour l\'affichage (ex: "0: ,1:█,□:.").')
    parser_ac.set_defaults(func=executer_simulation_automate)

    # --- Sous-commande pour Machine de Turing ---
    # Add common arguments explicitly, defining positional argument first
    parser_mt = subparsers.add_parser('turing', help='Simuler une machine de Turing.')
    parser_mt.add_argument('turing_file', type=str, help='Fichier décrivant la machine de Turing.') # Positional argument FIRST
    # Add common arguments needed for turing subcommand directly
    parser_mt.add_argument('-i', '--input-word', type=str, required=True, help='Mot d\'entrée pour la simulation.')
    parser_mt.add_argument('--max-steps', type=int, default=1000, help='Nombre maximum de pas de simulation (défaut: 1000).')
    parser_mt.add_argument('-o', '--output-file', type=str, default=None, help='Fichier pour sauvegarder la sortie de la simulation.')
    parser_mt.add_argument('--display-interval', type=int, default=1, help="Afficher la configuration tous les N pas (défaut: 1).") # Maybe not needed for MT display?
    parser_mt.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux, n\'affiche pas les étapes intermédiaires.')

    # Pas besoin d'arguments mode/valeur spécifiques pour la MT, elle s'arrête sur ACCEPT/REJECT/BLOCK/MAX_STEPS
    parser_mt.set_defaults(func=executer_simulation_turing)

    # --- Sous-commande pour Simulation MT via AC ---
    # Add common arguments explicitly, defining positional argument first
    parser_simu = subparsers.add_parser('simulate', help='Simuler une MT via un automate cellulaire.')
    parser_simu.add_argument('turing_file', type=str, help='Fichier décrivant la machine de Turing à simuler.') # Positional argument FIRST
    # Add common arguments needed for simulate subcommand directly
    parser_simu.add_argument('-i', '--input-word', type=str, required=True, help='Mot d\'entrée pour la simulation.')
    parser_simu.add_argument('--max-steps', type=int, default=1000, help='Nombre maximum de pas de simulation (défaut: 1000).')
    parser_simu.add_argument('-o', '--output-file', type=str, default=None, help='Fichier pour sauvegarder la sortie de la simulation.')
    parser_simu.add_argument('--display-interval', type=int, default=1, help="Afficher la configuration tous les N pas (défaut: 1).")
    # Quiet mode might be useful to suppress AC step display
    parser_simu.add_argument('-q', '--quiet', action='store_true', help='Mode silencieux, n\'affiche pas les étapes intermédiaires de l\'AC.')

    parser_simu.add_argument('--compare', action='store_true', help='Exécuter aussi la simulation MT directe pour comparer.')
    # Utilise max_steps pour déterminer la durée de la simulation AC
    parser_simu.set_defaults(func=executer_simulation_via_automate)

    # --- Parsing et Exécution ---
    args = parser.parse_args()

    # File existence checks are now done within the subcommand functions


    args.func(args) # Appelle la fonction associée à la sous-commande

if __name__ == "__main__":
    # Exemple de commandes en ligne:
    # python main.py automate automates/regle110.txt -i 0001000 --mode steps --value 20 -o output/sim_regle110.txt
    # python main.py automate automates/regle110.txt -i 0001000 --mode stable --max-steps 50 -o output/stable_sim.txt
    # python main.py turing machines_turing/incrementeur.txt -i 101 --max-steps 50 -o output/sim_incrementeur_mt.txt --quiet
    # python main.py simulate machines_turing/incrementeur.txt -i 101 --max-steps 100 --compare -o output/simu_ac_from_mt.txt
    main()
