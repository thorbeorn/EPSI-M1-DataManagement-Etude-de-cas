data folder est le fichier avec le csv d'entree
output folder est tout les fichier rendu generer par le script python

python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r "requirement.txt"

function transform_Dataframe_Mail,
supprime les mail sans @
supprime le deuxieme @ si le mail est xxx@@a ou xxx@a.
pour les mail valide il les laisse et cree une map avec les nom de domaine
poru les mail avec aa@bb, il regarde la map avec les nom de domaine et si un nom de dommain correspond a bb alors il prend la premiere occurence et corrige le mail

function transform_Dataframe_Salary
supprime les valeurs negative, un salaire ne peux etre negatif
supprime les valeurs fausse qui ne contionne pas de chiffre
supprimes les character qui ne sont pas des chiffres dans la valeur salaire et renvoi un nombre
transforme la colone en int

function transform_Dataframe_Employment_Date
reformat les date au bon format avec le bon separateur
transforme les date au format date et le reste en null si c'est pas transformable
supprime les valeurs nul

function security_Dataframe_Full_Name
hash le nom et le prenom en md5
supprime les colone nom et prenom

function security_Dataframe_Social_Number
supprime les numero de secu de moin de 15 char
mask les numero avec **** sauf la clé

function show_Dataframe_With_Role
affiche le dataframe suivant le role
admin vois tout
manager vois tous sauf numero de secu et le salaire brut arrondi au milier pret 41520 -> 41000