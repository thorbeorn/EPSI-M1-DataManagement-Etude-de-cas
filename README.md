python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r "requirement.txt"

function transform_Dataframe_Mail,
supprime les mail sans @
supprime le deuxieme @ si le mail est xxx@@a ou xxx@a.
pour les mail valide il les laisse et cree une map avec les nom de domaine
poru les mail avec aa@bb, il regarde la map avec les nom de domaine et si un nom de dommain correspond a bb alors il prend la premiere occurence et corrige le mail