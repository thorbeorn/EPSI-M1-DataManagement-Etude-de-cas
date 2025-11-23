import pandas as pd
import duckdb as ddb

PATHS = {
    "csv": "data/employees_raw.csv"
}


def extract_Dataframe_From_CSV(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

def transform_Dataframe_Mail(df):
    # --- 0) Supprimer tout de suite les e-mails sans @ ---
    df[df["email"].str.contains("@", na=False)].copy()
    def fix_multiple_at(x):
        # Si x n'est pas une string, on supprime
        if not isinstance(x, str):
            return None
        # Si c'est "nan" (résultat de astype(str)), on supprime
        if x.lower() == "nan":
            return None
        parts = x.split("@")
        if len(parts) <= 2:
            return x
        # garder premier @, supprimer les autres
        return parts[0] + "@" + "".join(parts[1:])
    df["email"] = df["email"].apply(fix_multiple_at)
    df = df[df["email"].str.contains("@", na=False)].copy()
    # --- 1) Normaliser en minuscules ---
    df["email"] = df["email"].str.lower()
    # --- 2) Extraire domaine (avant le premier point) ---
    df["domain"] = df["email"].str.extract(r"@([^\.]+)")
    # --- 3) Extraire TLD (s’il existe) ---
    df["tld"] = df["email"].str.extract(r"\.([a-z]{2,})$")
    # --- 4) Construire dictionnaire domaine → TLD basé sur la première occurrence ---
    # On prend la TLD seulement si elle existe
    domain_tld_map = (
        df[df["tld"].notna()]
        .groupby("domain")["tld"]
        .first()           # première occurrence en cas de multiple occurrence
        .to_dict()
    )
    # --- 5) Inline function to fix mail in parent df ---
    def fix_email(row):
        email = row["email"]
        domain = row["domain"]
        tld = row["tld"]

        # Si déjà complet → OK
        if pd.notna(tld):
            return email

        # Si pas de TLD mais un connu existe → compléter
        if domain in domain_tld_map:
            return f"{email}.{domain_tld_map[domain]}"

        # Aucun TLD connu → ne rien changer
        return email
    # --- 6) Appliquer correction ---
    df["email"] = df.apply(fix_email, axis=1)
    # --- 7) Supprimer les emails non réparables ---
    df = df[df["email"].notna()].copy()
    # --- 8) Nettoyer colonnes temporaires ---
    df = df.drop(columns=["domain", "tld"])
    # Retourner le DataFrame dans le même schéma d'origine
    return df
def transform_Dataframe_Salary(df):
    return ddb.sql("""
    SELECT 
        * EXCLUDE (salaire_brut),
        CAST(REGEXP_REPLACE(salaire_brut, '[^0-9]', '', 'g') AS BIGINT) AS salaire_brut
    FROM df
    WHERE salaire_brut NOT LIKE '-%';
    """).df()
def transform_Dataframe_Employment_Date(df):
    return ddb.sql("""
    WITH cleaned AS (
        SELECT
            *,
            REPLACE(REPLACE(date_embauche, '/', '-'), '.', '-') AS date_norm
        FROM df
    ),
    parsed AS (
        SELECT
            * EXCLUDE (date_embauche, date_norm),
            CASE
                WHEN date_norm LIKE '__-__-____'
                    THEN STRPTIME(date_norm, '%d-%m-%Y')
                WHEN date_norm LIKE '____-__-__ __:__:__'
                    THEN STRPTIME(date_norm, '%Y-%m-%d %H:%M:%S')
                WHEN date_norm LIKE '____-__-__'
                    THEN STRPTIME(date_norm, '%Y-%m-%d')
                ELSE NULL
            END AS date_embauche
        FROM cleaned
    )

    select *
    FROM parsed
    WHERE date_embauche IS NOT NULL
      AND date_embauche <= CURRENT_DATE
    """).df()

def security_Dataframe_Full_Name(df):
    return ddb.sql("""
    SELECT 
        * EXCLUDE (nom, prenom),
        MD5(COALESCE(nom, '') || '|' || COALESCE(prenom, '')) AS Hash_ID
    FROM df
    """).df()
def security_Dataframe_Social_Number(df):
    return ddb.sql("""
    WITH masked AS (
        SELECT 
            * EXCLUDE (secu_sociale),
            CASE 
                WHEN secu_sociale IS NOT NULL AND LENGTH(secu_sociale) = 15 THEN
                    '***********' || RIGHT(secu_sociale, 2)
                ELSE NULL
            END AS secu_sociale
        FROM df
    )
    SELECT *
    FROM masked
    WHERE secu_sociale IS NOT NULL
    """).df()

def show_Dataframe_With_Role(df, role):
    role = role.lower()
    match role:
        case "admin":
            print(df)
        case "manager":
            df.drop('secu_sociale', inplace=True, axis=1)
            df['salaire_brut'] = df['salaire_brut'].round(-3)
            print(df)

def main():
    raw_Dataframe = extract_Dataframe_From_CSV(PATHS["csv"])

    silver_Dataframe = transform_Dataframe_Mail(raw_Dataframe)
    silver_Dataframe = transform_Dataframe_Salary(silver_Dataframe)
    silver_Dataframe = transform_Dataframe_Employment_Date(silver_Dataframe)

    gold_Dataframe = security_Dataframe_Full_Name(silver_Dataframe)
    gold_Dataframe = security_Dataframe_Social_Number(gold_Dataframe)

    show_Dataframe_With_Role(gold_Dataframe, "Admin")
    show_Dataframe_With_Role(gold_Dataframe, "Manager")

if __name__ == "__main__":
    main()