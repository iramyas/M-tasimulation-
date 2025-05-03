# Simulateur d’Automate Cellulaire

## Utilisation

Pour lancer une simulation (par exemple de la règle 110) :

```bash
make run
```

## Question 14 - Est-ce que HALTING-CELLULAR-AUTOMATON est décidable ?

Non, ce problème n’est pas décidable.

Les automates cellulaires unidimensionnels sont capables de simuler des machines de Turing. Ainsi, on peut encoder une machine de Turing arbitraire dans un automate cellulaire.

Si on pouvait décider automatiquement si une configuration contenant un certain état s apparaîtra, on pourrait décider si la machine de Turing simulée s’arrête. Or, le problème de l’arrêt est indécidable.

Conclusion : HALTING-CELLULAR-AUTOMATON est indécidable, car cela reviendrait à résoudre le problème de l'arrêt.