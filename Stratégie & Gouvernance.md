# **Stratégie & Gouvernance — Politique d’archivage lors du départ d’un employé**

---

# Principes légaux et de conformité (points clefs)

* Le **RGPD** impose le principe de minimisation et de durée limitée : les données ne doivent pas être conservées indéfiniment et la durée doit être justifiée par l’objectif du traitement.
* Pour les **bulletins de paie**, la réglementation française impose à l’employeur de conserver un double pendant au moins **5 ans**, et l’employeur doit garantir la disponibilité des fiches de paie électroniques **jusqu’à 50 ans** ou jusqu’à ce que le salarié ait 75 ans (selon modalités). Ces obligations légales limitent ce que vous pouvez supprimer/anonymiser.
* La CNIL donne des bonnes pratiques : par exemple, les données liées à la gestion de la paie ou au contrôle du temps peuvent être conservées 5 ans (exemple indicatif) ; pour le reste, définir une durée au regard de l’objectif et documenter-la.

---

## **1) Passage de la base active (Hot storage) vers l’archive (Cold storage)**

**Moment du basculement :**
Les données RH opérationnelles de l’employé sont déplacées depuis la base active **12 mois après la date de sortie**.
Cette période permet de traiter les éventuels litiges internes (solde de tout compte, attestations, correction de paie).

Après ce délai :

* Le dossier RH devient inactif.
* Les données ne sont plus utilisées dans les systèmes opérationnels.
* Elles sont automatiquement transférées vers un **stockage d’archive chiffré**, à accès restreint.

---

## **2) Ce qui est conservé en archive (Cold storage)**

Pour respecter la loi française :

* **Les bulletins de paie** doivent être conservés **au moins 5 ans**, et lorsqu’ils sont électroniques, l’employeur doit garantir leur accessibilité très longue durée (minimum 20 ans).
* Les justificatifs comptables (cotisations, déclarations légales) doivent également être archivés pendant les durées réglementaires.

**Ces documents sont donc conservés en Cold storage**, en mode immuable (WORM), avec journalisation des accès.

---

## **3) Ce qui est supprimé ou anonymisé**

Pour respecter le RGPD, toute donnée non nécessaire à une obligation légale est **épurée** :

### **Supprimé définitivement :**

* Adresse personnelle, email personnel, numéro de téléphone
* Documents administratifs non obligatoires (copies de carte d’identité, RIB anciens, CV, lettres de motivation)
* Notes d’évaluation ou feedback non liés à un dossier disciplinaire
* Logs internes n’ayant plus d’intérêt métier

### **Anonymisé (pseudonymisation ou anonymisation irréversible) :**

* Données utilisées à des fins statistiques (ex : analyses People Analytics)
* Identité du salarié remplacée par un Hash_ID
* Données de performance éventuellement conservées pour analyses historiques

---

## **4) Règles d’accès et gouvernance**

* L’accès aux archives est limité au **service Paie / Juridique**, en lecture seule.
* Les clés de chiffrement sont séparées du système RH actif (KMS).
* Toute restauration depuis l’archive est enregistrée dans un audit log.
* La politique de conservation est documentée dans le **registre de traitement RGPD**.