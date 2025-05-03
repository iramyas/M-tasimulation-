# test_turing.py
import unittest
import os
import tempfile

# Assurez-vous que les imports correspondent à la structure de votre projet
from turing import (
    MachineTuring, ConfigurationTuring, lire_turing,
    pas_turing, simuler_turing
)

# Fonction utilitaire pour créer des fichiers temporaires (identique à test_automate)
def creer_fichier_temp(contenu: str, suffix: str = ".txt") -> str:
    fd, nom_fichier = tempfile.mkstemp(suffix=suffix, text=True)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(contenu)
    return nom_fichier

class TestTuringStructures(unittest.TestCase):
    # Tests Q8 (Structure MT), Q9 (Structure Config MT)

    def test_creation_machine_ok(self):
        etats = {"q0", "q1", "ACCEPT", "REJECT"}
        alpha = {"0", "1", "□"}
        trans = {("q0", "1"): ("q1", "0", "R")}
        init = "q0"
        acc = {"ACCEPT"}
        rej = {"REJECT"}
        mt = MachineTuring(etats, alpha, trans, init, acc, rej, "□")
        self.assertEqual(mt.etats, etats)
        self.assertEqual(mt.alphabet_travail, alpha)
        self.assertEqual(mt.transitions, trans)
        self.assertEqual(mt.etat_initial, init)
        self.assertEqual(mt.etats_accept, acc)
        self.assertEqual(mt.etats_reject, rej)
        self.assertEqual(mt.symbole_defaut, "□")

    def test_creation_machine_erreurs_validation(self):
        etats = {"q0", "q1"}
        alpha = {"0", "1", "□"}
        trans = {}
        acc = {"ACCEPT"} # État accept non dans etats
        rej = {"REJECT"}
        with self.assertRaises(ValueError): # État initial non valide
            MachineTuring(etats, alpha, trans, "q_invalid", acc, rej, "□")
        with self.assertRaises(ValueError): # État accept non valide
            MachineTuring(etats, alpha, trans, "q0", acc, rej, "□")
        with self.assertRaises(ValueError): # État reject non valide
             MachineTuring(etats, alpha, trans, "q0", {"q0"}, rej, "□")
        with self.assertRaises(ValueError): # Symbole défaut non valide
             MachineTuring(etats, alpha, trans, "q0", {"q0"}, set(), "X")
        with self.assertRaises(ValueError): # Intersection Accept/Reject
             MachineTuring(etats.union({"HALT"}), alpha, trans, "q0", {"HALT"}, {"HALT"}, "□")


    def test_creation_config(self):
        bande = {0: "1", 1: "0"}
        config = ConfigurationTuring(bande, tete=1, etat="q1", symbole_defaut="□")
        self.assertEqual(config.bande, bande)
        self.assertEqual(config.tete, 1)
        self.assertEqual(config.etat, "q1")
        self.assertEqual(config.symbole_defaut, "□")

    def test_config_lire_ecrire_deplacer(self):
        bande = {0: "1", 1: "0"}
        config = ConfigurationTuring(bande, tete=0, etat="q0", symbole_defaut="□")
        self.assertEqual(config.lire_symbole(), "1") # Lit bande[0]
        config.ecrire_symbole("X")
        self.assertEqual(config.lire_symbole(), "X")
        self.assertEqual(config.bande[0], "X")
        config.deplacer_tete("R")
        self.assertEqual(config.tete, 1)
        self.assertEqual(config.lire_symbole(), "0") # Lit bande[1]
        config.deplacer_tete("R")
        self.assertEqual(config.tete, 2)
        self.assertEqual(config.lire_symbole(), "□") # Lit symbole par défaut
        config.ecrire_symbole("Y")
        self.assertEqual(config.bande[2], "Y")
        config.deplacer_tete("L")
        self.assertEqual(config.tete, 1)
        config.deplacer_tete("L")
        self.assertEqual(config.tete, 0)
        config.deplacer_tete("N")
        self.assertEqual(config.tete, 0)
        with self.assertRaises(ValueError):
            config.deplacer_tete("INVALID")

    # __str__ est testé implicitement via les tests de simulation

class TestTuringLecture(unittest.TestCase):
    # Tests Q10 (lire_turing)

    def setUp(self):
        self.fichiers_temp = []

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

    def test_lire_turing_ok_defauts(self):
        contenu = """
        # Machine simple qui change 1 en 0 et va à droite
        q0, 1, q1, 0, R
        q1, 0, ACCEPT, 0, N # Arrêt sur ACCEPT
        q0, 0, REJECT, 0, N # Arrêt sur REJECT si on commence par 0
        q1, 1, q1, 1, R # Boucle sur les 1 dans q1
        q1, □, ACCEPT, □, N # Accepte si fin de mot
        """
        nom_fichier = self.creer_et_enregistrer_temp(contenu)
        mt = lire_turing(nom_fichier)
        self.assertEqual(mt.etat_initial, "q0")
        self.assertEqual(mt.etats_accept, {"ACCEPT"})
        self.assertEqual(mt.etats_reject, {"REJECT"})
        self.assertEqual(mt.alphabet_travail, {"0", "1", "□"})
        self.assertIn(("q0", "1"), mt.transitions)
        self.assertEqual(mt.transitions[("q0", "1")], ("q1", "0", "R"))
        self.assertIn(("q1", "□"), mt.transitions)
        self.assertEqual(mt.transitions[("q1", "□")], ("ACCEPT", "□", "N"))
        self.assertIn("q0", mt.etats)
        self.assertIn("q1", mt.etats)
        self.assertIn("ACCEPT", mt.etats)
        self.assertIn("REJECT", mt.etats)

    def test_lire_turing_surcharge_directives(self):
        contenu = """
        # initial: start
        # accept: ok, done
        # reject: fail
        # alphabet: a, b, _
        start, a, move, b, R
        move, b, move, a, R
        move, _, ok, _, N
        start, b, fail, b, N
        """
        nom_fichier = self.creer_et_enregistrer_temp(contenu)
        mt = lire_turing(nom_fichier)
        self.assertEqual(mt.etat_initial, "start")
        self.assertEqual(mt.etats_accept, {"ok", "done"})
        self.assertEqual(mt.etats_reject, {"fail"})
        # L'alphabet doit contenir 0, 1, □ PLUS a, b, _
        self.assertEqual(mt.alphabet_travail, {"0", "1", "□", "a", "b", "_"})
        self.assertEqual(mt.symbole_defaut, "□") # Symbole défaut n'est pas changé par #alphabet
        self.assertIn(("start", "a"), mt.transitions)
        self.assertEqual(mt.transitions[("start", "a")], ("move", "b", "R"))
        self.assertIn("start", mt.etats)
        self.assertIn("move", mt.etats)
        self.assertIn("ok", mt.etats)
        self.assertIn("done", mt.etats)
        self.assertIn("fail", mt.etats)


    def test_lire_turing_fichier_vide(self):
        nom_fichier = self.creer_et_enregistrer_temp("")
        mt = lire_turing(nom_fichier)
        # Conventions par défaut
        self.assertEqual(mt.etat_initial, "q0")
        self.assertEqual(mt.etats_accept, {"ACCEPT"})
        self.assertEqual(mt.etats_reject, {"REJECT"})
        self.assertEqual(mt.alphabet_travail, {"0", "1", "□"})
        self.assertEqual(mt.transitions, {})
        self.assertEqual(mt.etats, {"q0", "ACCEPT", "REJECT"}) # États connus par défaut

    def test_lire_turing_fichier_inexistant(self):
        with self.assertRaises(FileNotFoundError):
            lire_turing("fichier_qui_n_existe_pas_998.txt")

    def test_lire_turing_format_invalide(self):
        contenu = "q0, 1, q1, 0, X" # Direction invalide
        nom_fichier = self.creer_et_enregistrer_temp(contenu)
        # La fonction ignore la ligne invalide
        mt = lire_turing(nom_fichier)
        self.assertEqual(mt.transitions, {})

class TestTuringCalcul(unittest.TestCase):
    # Tests Q11 (pas_turing)

    def setUp(self):
        # Machine simple: si 1 -> 0, R, q1 ; si 0 -> 1, L, q0 ; si □ -> □, N, ACCEPT
        etats = {"q0", "q1", "ACCEPT"}
        alpha = {"0", "1", "□"}
        trans = {
            ("q0", "1"): ("q1", "0", "R"),
            ("q0", "0"): ("q0", "1", "L"), # Change 0 en 1, revient à gauche
            ("q1", "1"): ("q1", "1", "R"), # Saute les 1
            ("q1", "0"): ("q1", "0", "R"), # Saute les 0
            ("q1", "□"): ("ACCEPT", "□", "N") # Accepte à la fin
        }
        init = "q0"
        acc = {"ACCEPT"}
        rej = set()
        self.mt_simple = MachineTuring(etats, alpha, trans, init, acc, rej, "□")

    def test_pas_turing_simple_R(self):
        # Config: q0, tête sur 1, bande {0:1, 1:1} => état q1, tête sur pos 1, bande {0:0, 1:1}
        bande = {0: "1", 1: "1"}
        config = ConfigurationTuring(bande, tete=0, etat="q0", symbole_defaut="□")
        config_modifiee = pas_turing(self.mt_simple, config)
        self.assertIsNotNone(config_modifiee)
        self.assertEqual(config.etat, "q1")
        self.assertEqual(config.tete, 1)
        self.assertEqual(config.bande[0], "0")
        self.assertEqual(config.bande[1], "1") # inchangé

    def test_pas_turing_simple_L(self):
        # Config: q0, tête sur 0, bande {0:0, 1:1} => état q0, tête sur pos -1, bande {0:1, 1:1}
        bande = {0: "0", 1: "1"}
        config = ConfigurationTuring(bande, tete=0, etat="q0", symbole_defaut="□")
        config_modifiee = pas_turing(self.mt_simple, config)
        self.assertIsNotNone(config_modifiee)
        self.assertEqual(config.etat, "q0")
        self.assertEqual(config.tete, -1)
        self.assertEqual(config.bande[0], "1")
        self.assertEqual(config.bande[1], "1") # inchangé

    def test_pas_turing_simple_N(self):
        # Config: q1, tête sur □ (pos 2), bande {0:0, 1:1} => état ACCEPT, tête pos 2, bande {0:0, 1:1}
        bande = {0: "0", 1: "1"}
        config = ConfigurationTuring(bande, tete=2, etat="q1", symbole_defaut="□")
        config_modifiee = pas_turing(self.mt_simple, config)
        self.assertIsNotNone(config_modifiee)
        self.assertEqual(config.etat, "ACCEPT")
        self.assertEqual(config.tete, 2)
        self.assertEqual(config.bande.get(2), "□") # N'écrit pas si lit et écrit □

    def test_pas_turing_bloque(self):
         # Config: q0, tête sur □ => bloqué car ("q0", "□") non défini
        bande = {}
        config = ConfigurationTuring(bande, tete=0, etat="q0", symbole_defaut="□")
        config_modifiee = pas_turing(self.mt_simple, config)
        self.assertIsNone(config_modifiee) # Doit retourner None si bloqué

class TestTuringSimulation(unittest.TestCase):
    # Tests Q12 (simuler_turing)

    def setUp(self):
        # MT qui accepte si le mot est "101"
        etats = {"q0", "q1", "q2", "q3", "ACCEPT", "REJECT"}
        alpha = {"0", "1", "□"}
        trans = {
            ("q0", "1"): ("q1", "1", "R"), # Lit 1
            ("q1", "0"): ("q2", "0", "R"), # Lit 0
            ("q2", "1"): ("q3", "1", "R"), # Lit 1
            ("q3", "□"): ("ACCEPT", "□", "N"), # Fin -> Accepte
            # Rejets si autre chose
            ("q0", "0"): ("REJECT", "0", "N"), ("q0", "□"): ("REJECT", "□", "N"),
            ("q1", "1"): ("REJECT", "1", "N"), ("q1", "□"): ("REJECT", "□", "N"),
            ("q2", "0"): ("REJECT", "0", "N"), ("q2", "□"): ("REJECT", "□", "N"),
            ("q3", "0"): ("REJECT", "0", "N"), ("q3", "1"): ("REJECT", "1", "N"),
        }
        init = "q0"
        acc = {"ACCEPT"}
        rej = {"REJECT"}
        self.mt_101 = MachineTuring(etats, alpha, trans, init, acc, rej, "□")

        # MT qui boucle (q0, 0 -> q0, 0, N)
        trans_boucle = {("q0", "0"): ("q0", "0", "N")}
        self.mt_boucle = MachineTuring({"q0"}, {"0","□"}, trans_boucle, "q0", set(), set(), "□")


    def test_simulation_accept(self):
        mot = "101"
        resultat, config_finale, n_pas = simuler_turing(self.mt_101, mot, max_steps=10, afficher=False)
        self.assertEqual(resultat, "ACCEPTED")
        self.assertEqual(config_finale.etat, "ACCEPT")
        self.assertEqual(n_pas, 4) # q0->q1(R), q1->q2(R), q2->q3(R), q3->ACCEPT(N)

    def test_simulation_reject_mauvais_symbole(self):
        mot = "111"
        resultat, config_finale, n_pas = simuler_turing(self.mt_101, mot, max_steps=10, afficher=False)
        self.assertEqual(resultat, "REJECTED")
        self.assertEqual(config_finale.etat, "REJECT") # Bloqué dans q1 sur le 2e '1'
        self.assertEqual(n_pas, 2) # q0->q1(R), q1->REJECT(N)

    def test_simulation_reject_trop_court(self):
        mot = "10"
        resultat, config_finale, n_pas = simuler_turing(self.mt_101, mot, max_steps=10, afficher=False)
        self.assertEqual(resultat, "REJECTED")
        self.assertEqual(config_finale.etat, "REJECT") # Bloqué dans q2 sur '□'
        self.assertEqual(n_pas, 3) # q0->q1(R), q1->q2(R), q2->REJECT(N)

    def test_simulation_reject_trop_long(self):
        mot = "1010"
        resultat, config_finale, n_pas = simuler_turing(self.mt_101, mot, max_steps=10, afficher=False)
        self.assertEqual(resultat, "REJECTED")
        self.assertEqual(config_finale.etat, "REJECT") # Bloqué dans q3 sur '0'
        self.assertEqual(n_pas, 4) # q0->q1(R), q1->q2(R), q2->q3(R), q3->REJECT(N)

    def test_simulation_bloque(self):
        # MT simple qui n'a pas de transition pour '0' dans q0
        mt_block = MachineTuring({"q0"}, {"0","□"}, {}, "q0", set(), set(), "□")
        mot = "0"
        resultat, config_finale, n_pas = simuler_turing(mt_block, mot, max_steps=10, afficher=False)
        self.assertEqual(resultat, "BLOCKED")
        self.assertEqual(config_finale.etat, "q0") # État où elle a bloqué
        self.assertEqual(n_pas, 0) # Bloquée avant le premier pas

    def test_simulation_max_steps(self):
        mot = "0"
        resultat, config_finale, n_pas = simuler_turing(self.mt_boucle, mot, max_steps=5, afficher=False)
        self.assertEqual(resultat, "MAX_STEPS")
        self.assertEqual(config_finale.etat, "q0") # Toujours dans q0
        self.assertEqual(n_pas, 5)

if __name__ == '__main__':
    unittest.main(verbosity=2)