### 1️⃣ Relancer le calcul uniquement sur les mois concernés

**Problème :** Le bug affecte uniquement les salariés embauchés après 2022, et seulement pour les augmentations entre 2022 et 2025. On veut corriger les salaires sans recalculer tout l’historique depuis 2018.

**Approche :**

* Identifier **les salariés concernés** (embauchés après 2022).
* Identifier **la période affectée** (mois depuis l’embauche jusqu’à aujourd’hui, uniquement les années 2022–2025).
* Relancer le calcul de salaire **seulement pour ces salariés et ces mois**, en appliquant correctement les augmentations manquantes.

**Exemple en pseudo-logique :**
```text
Pour chaque salarié S embauché après 2022 :
    Pour chaque mois M entre date_embauche(S) et aujourd'hui :
        Si M >= Janvier 2022 :
            recalculer salaire en appliquant les augmentations manquantes
```

* Les mois précédant 2022 ou les salariés embauchés avant 2022 **ne sont pas touchés**, donc on évite un recalcul inutile.

**Avantage :** gain de temps, ressources et évite de perturber les historiques corrects.

---

### 2️⃣ Mécanisme de stockage facilitant cette opération

Pour pouvoir recalculer seulement certaines périodes sans tout refaire :

* **Format orienté transactionnel ou incrémental**, où chaque changement de salaire est stocké par **période / événement**

* Chaque mise à jour de salaire crée un **nouvel enregistrement** plutôt que d’écraser l’ancien.

* **Avantages :**

  * On peut recalculer uniquement les mois erronés.
  * Historique complet conservé (audit possible).
  * Permet des correctifs incrémentaux.

* **Formats possibles :**

  * **Parquet** est idéal si les volumes sont importants : lecture sélective par colonnes et filtres par date rapides.
  * Base de données relationnelle (PostgreSQL, MySQL) avec tables historiques.