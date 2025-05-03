# test_simulateur.py
import unittest
import os
import tempfile
from typing import Tuple, Dict, Set, List # Add List here
# Ensure imports match your project structure
from turing import lire_turing, MachineTuring, simuler_turing
from automate import Configuration as ConfigAutomate, simuler_automate
from simulateur import (
    construire_automate_depuis_turing, creer_config_automate_pour_mt,
    EtatAutomateSimu # Import type for verification
)

# Helper to create temporary MT file
def creer_fichier_temp(contenu: str, suffix: str = ".txt") -> str:
    fd, nom_fichier = tempfile.mkstemp(suffix=suffix, text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(contenu)
    return nom_fichier


class TestSimulateurConstruction(unittest.TestCase):
    # Tests Q13 (construire_automate_depuis_turing)

    def setUp(self):
        self.fichiers_temp = []
        # Create a very simple MT: q0 on '1' writes '0', moves right -> ACCEPT
        contenu_mt_simple = """
        # initial: q0
        # accept: ACCEPT
        # alphabet: 0, 1, □
        q0, 1, ACCEPT, 0, R
        """
        self.nom_fichier_mt_simple = self.creer_et_enregistrer_temp(contenu_mt_simple)
        self.mt_simple = lire_turing(self.nom_fichier_mt_simple)
        self.automate_simu = construire_automate_depuis_turing(self.mt_simple)

    def tearDown(self):
        for f in self.fichiers_temp:
            try:
                os.remove(f)
            except OSError:
                pass

    def creer_et_enregistrer_temp(self, contenu):
        nom_fichier = creer_fichier_temp(contenu)
        self.fichiers_temp.append(nom_fichier)
        return nom_fichier

    def test_etats_automate_simu(self):
        # Expected states: ('q0', '0'), ('q0', '1'), ('q0', '□'),
        #                 ('ACCEPT', '0'), ('ACCEPT', '1'), ('ACCEPT', '□'),
        #                 ('REJECT', '0'), ('REJECT', '1'), ('REJECT', '□'),
        #                 ('*', '0'), ('*', '1'), ('*', '□')
        etats_attendus = {
            ('q0', '0'), ('q0', '1'), ('q0', '□'),
            ('ACCEPT', '0'), ('ACCEPT', '1'), ('ACCEPT', '□'),
            ('REJECT', '0'), ('REJECT', '1'), ('REJECT', '□'),
            ('*', '0'), ('*', '1'), ('*', '□')
        }
        self.assertEqual(self.automate_simu.etats, etats_attendus)
        self.assertEqual(self.automate_simu.symbole_defaut, ('*', '□'))

    def test_transitions_automate_simu_non_tete(self):
        # Check f( (*,l1), (*,l2), (*,l3) ) = (*, l2)
        for l1 in "01□":
            for l2 in "01□":
                for l3 in "01□":
                    vois = ( ('*', l1), ('*', l2), ('*', l3) )
                    attendu = ('*', l2)
                    self.assertIn(vois, self.automate_simu.fonction_transition)
                    self.assertEqual(self.automate_simu.fonction_transition[vois], attendu)

    def test_transitions_automate_simu_mouvement_R(self):
        # Simple MT: q0, 1 -> ACCEPT, 0, R
        q, s = "q0", "1"
        q_prime, s_prime, direction = "ACCEPT", "0", "R"

        # Check generated AC transitions for this R movement
        for l1 in "01□": # Symbol to the left
            for l3 in "01□": # Symbol to the right (which will be under the head next)
                 # a) Center loses the head: f( (*,l1), (q,s), (*,l3) ) = (*, s')
                 vois_centre = ( ('*', l1), (q, s), ('*', l3) )
                 attendu_centre = ('*', s_prime)
                 self.assertIn(vois_centre, self.automate_simu.fonction_transition)
                 self.assertEqual(self.automate_simu.fonction_transition[vois_centre], attendu_centre)

                 # b) Right receives the head: f( (q,s), (*,l3), (*,l4) ) = (q', l3)
                 for l4 in "01□": # Symbol even further right
                      vois_droite = ( (q, s), ('*', l3), ('*', l4) )
                      attendu_droite = (q_prime, l3) # New state, old symbol
                      self.assertIn(vois_droite, self.automate_simu.fonction_transition)
                      self.assertEqual(self.automate_simu.fonction_transition[vois_droite], attendu_droite)

    # Add similar tests here for L and N movements if the MT contains them

    def test_creer_config_automate_pour_mt(self):
        mot = "10"
        contexte = 2
        config_ac = creer_config_automate_pour_mt(self.mt_simple, mot, contexte)
        # Expected: [(*,□), (*,□), (q0,1), (*,0), (*,□), (*,□)]
        attendu_etats = [
            ('*', '□'), ('*', '□'),
            ('q0', '1'),
            ('*', '0'),
            ('*', '□'), ('*', '□')
        ]
        self.assertEqual(config_ac.etats, attendu_etats)

    def test_creer_config_automate_mot_vide(self):
        mot = ""
        contexte = 1
        config_ac = creer_config_automate_pour_mt(self.mt_simple, mot, contexte)
        # Expected: [(*,□), (q0,□), (*,□)]
        attendu_etats = [
            ('*', '□'),
            ('q0', '□'), # Head on the default symbol
            ('*', '□')
        ]
        self.assertEqual(config_ac.etats, attendu_etats)


class TestSimulateurIntegration(unittest.TestCase):
     # Integration Test Q13: Comparison of MT and AC simulation

    def setUp(self):
        self.fichiers_temp = []
        # Simple MT: inverts the first bit and accepts if it was '1'
        contenu_mt = """
        # initial: q0
        # accept: ACCEPT
        # reject: REJECT
        q0, 1, q_inv, 0, N
        q0, 0, q_inv, 1, N
        q_inv, 0, ACCEPT, 0, N
        q_inv, 1, REJECT, 1, N
        q0, □, REJECT, □, N # Reject empty word
        """
        self.nom_fichier_mt = self.creer_et_enregistrer_temp(contenu_mt)
        self.mt = lire_turing(self.nom_fichier_mt)
        self.automate_simu = construire_automate_depuis_turing(self.mt)

    def tearDown(self):
        for f in self.fichiers_temp:
            try:
                os.remove(f)
            except OSError:
                pass

    def creer_et_enregistrer_temp(self, contenu):
        nom_fichier = creer_fichier_temp(contenu)
        self.fichiers_temp.append(nom_fichier)
        return nom_fichier

    def get_etat_final_ac_simu(self, historique_ac: List[ConfigAutomate]) -> str:
        """Interprets the final state of the AC simulation."""
        config_finale = historique_ac[-1]
        etat_mt_final = "UNKNOWN"
        for etat_ac in config_finale.etats:
            if isinstance(etat_ac, tuple) and etat_ac[0] != '*':
                 etat_mt_final = etat_ac[0] # Find the TM head state
                 break
        # Simplification: return just the TM state found
        if etat_mt_final in self.mt.etats_accept: return "ACCEPTED"
        if etat_mt_final in self.mt.etats_reject: return "REJECTED"
        # We could also check if the AC stabilized in a non-final state of the MT
        return "RUNNING_OR_OTHER" # Or the TM state itself

    def test_simulation_comparee_accept(self):
        mot = "1"
        # Simu MT
        res_mt, cfg_mt, n_pas_mt = simuler_turing(self.mt, mot, max_steps=10, afficher=False)
        self.assertEqual(res_mt, "ACCEPTED")

        # Simu AC
        config_ac_init = creer_config_automate_pour_mt(self.mt, mot, contexte=2)
        # Simulate AC, passing the original TM object and enough steps
        # We still need a generous step limit because the number of AC steps per TM step can vary.
        historique_ac = simuler_automate(
            self.automate_simu,
            config_ac_init,
            mode="steps", # Still use steps mode, but the simuler_automate will now also check TM state
            valeur=30, # Keep a large enough value, but it should stop early now
            tm_originale=self.mt # Pass the MT object here
        )
        res_ac = self.get_etat_final_ac_simu(historique_ac)
        self.assertEqual(res_ac, "ACCEPTED")
        # Optional: Assert that the history length is reasonably short, showing it stopped early
        self.assertLess(len(historique_ac), 30 + 1)

    def test_simulation_comparee_reject(self):
        mot = "0"
         # Simu MT
        res_mt, cfg_mt, n_pas_mt = simuler_turing(self.mt, mot, max_steps=10, afficher=False)
        self.assertEqual(res_mt, "REJECTED")

        # Simu AC
        config_ac_init = creer_config_automate_pour_mt(self.mt, mot, contexte=2)
        # Simulate AC, passing the original TM object
        historique_ac = simuler_automate(
            self.automate_simu,
            config_ac_init,
            mode="steps",
            valeur=30, # Keep a large enough value
            tm_originale=self.mt # Pass the MT object here
        )
        res_ac = self.get_etat_final_ac_simu(historique_ac)
        self.assertEqual(res_ac, "REJECTED")
        # Optional: Assert that the history length is reasonably short
        self.assertLess(len(historique_ac), 30 + 1)

    def test_simulation_comparee_reject_vide(self):
        mot = ""
         # Simu MT
        res_mt, cfg_mt, n_pas_mt = simuler_turing(self.mt, mot, max_steps=10, afficher=False)
        self.assertEqual(res_mt, "REJECTED") # q0, □ -> REJECT

        # Simu AC
        config_ac_init = creer_config_automate_pour_mt(self.mt, mot, contexte=2)
        # Simulate AC, passing the original TM object
        historique_ac = simuler_automate(
            self.automate_simu,
            config_ac_init,
            mode="steps",
            valeur=30, # Keep a large enough value
            tm_originale=self.mt # Pass the MT object here
        )
        res_ac = self.get_etat_final_ac_simu(historique_ac)
        self.assertEqual(res_ac, "REJECTED")
        # Optional: Assert that the history length is reasonably shot
        self.assertLess(len(historique_ac), 30 + 1)



if __name__ == '__main__':
    unittest.main(verbosity=2)