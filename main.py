import pandas as pd
import duckdb as ddb
import numpy as np
import yaml

PATHS = {
    "csv": "data/employees_raw.csv",
    "yaml_metadata_gold": "output/gold_Dataframe_Metadata.yaml"
}
DESCRIPTION = {
    "id": "Identifiant unique de l'employé dans la base de données.",
    "Hash_ID": "Remplace nom/prenom, pseudonymisé",
    "sexe": "Sexe de l'employé, généralement 'M' pour masculin ou 'F' pour féminin.",
    "date_naissance": "Date de naissance de l'employé au format AAAA-MM-JJ.",
    "categorie": "Type de contrat ou statut de l'employé, par exemple 'Alternant', 'CDI', 'CDD'.",
    "email": "Adresse e-mail professionnelle de l'employé.",
    "salaire_brut": "Salaire brut annuel ou mensuel de l'employé, selon le contexte.",
    "date_embauche": "Date à laquelle l'employé a été embauché, au format AAAA-MM-JJ HH:MM:SS.",
    "secu_sociale": "Numéro de sécurité sociale de l'employé, identifiant unique pour les démarches administratives."
}
CONFIDENTIALITY = {
    "id": "Confidentiel",
    "Hash_ID": "Confidentiel",
    "sexe": "PII",
    "date_naissance": "PII",
    "categorie": "Public",
    "email": "PII",
    "salaire_brut": "Confidentiel",
    "date_embauche": "Confidentiel",
    "secu_sociale": "PII"
}
OWNER = {
    "id": "IT",
    "Hash_ID": "RH",
    "sexe": "RH",
    "date_naissance": "RH",
    "categorie": "RH",
    "email": "RH",
    "salaire_brut": "Finance",
    "date_embauche": "RH",
    "secu_sociale": "RH"
}

def extract_Dataframe_From_CSV(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Error loading data: {e}")

def transform_Dataframe_Mail(df, kpi):
    df = df.copy()
    
    kpi["emails_total"] = len(df)
    
    before = len(df)
    df = df[df["email"].str.contains("@", na=False)].copy()
    kpi["emails_supprimes_sans_at"] = before - len(df)
    
    def fix_multiple_at(x):
        if not isinstance(x, str) or x.lower() == "nan":
            return None
        parts = x.split("@")
        if len(parts) <= 2:
            return x
        return parts[0] + "@" + "".join(parts[1:])
    
    df["email_before_fix"] = df["email"]
    df["email"] = df["email"].apply(fix_multiple_at)
    
    before = len(df)
    df = df[df["email"].str.contains("@", na=False)].copy()
    kpi["emails_supprimes_apres_fix"] = before - len(df)
    
    df["email"] = df["email"].str.lower()
    df["domain"] = df["email"].str.extract(r"@([^\.]+)")
    df["tld"] = df["email"].str.extract(r"\.([a-z]{2,})$")
    
    domain_tld_map = df[df["tld"].notna()].groupby("domain")["tld"].first().to_dict()
    
    def fix_email(row):
        email = row["email"]
        domain = row["domain"]
        tld = row["tld"]
        if pd.notna(tld):
            return email
        if domain in domain_tld_map:
            return f"{email}.{domain_tld_map[domain]}"
        return email
    
    df["email"] = df.apply(fix_email, axis=1)
    
    kpi["emails_corriges_tld"] = int((df["email"] != df["email_before_fix"]).sum())
    
    before = len(df)
    df = df[df["email"].notna()].copy()
    kpi["emails_supprimes_non_reparables"] = before - len(df)
    
    df = df.drop(columns=["domain", "tld", "email_before_fix"])
    
    return df, kpi
def transform_Dataframe_Salary(df, kpi):
    temp_df = ddb.sql("""
    SELECT 
        * EXCLUDE (salaire_brut),
        CAST(REGEXP_REPLACE(salaire_brut, '[^0-9]', '', 'g') AS BIGINT) AS salaire_brut
    FROM df
    WHERE salaire_brut NOT LIKE '-%';
    """).df()

    kpi["salaire_total"] = len(df)
    kpi["salaire_supprimes"] = len(df) - len(temp_df)

    return temp_df, kpi
def transform_Dataframe_Employment_Date(df, kpi):
    temp_df = ddb.sql("""
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
    kpi["salaire_total"] = len(df)
    kpi["salaire_supprimes"] = len(df) - len(temp_df)

    return temp_df, kpi

def security_Dataframe_Full_Name(df):
    return ddb.sql("""
    SELECT 
        * EXCLUDE (nom, prenom),
        CAST(MD5(COALESCE(nom, '') || '|' || COALESCE(prenom, '')) AS VARCHAR) AS Hash_ID
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
def generate_Dataframe_To_Dataframe(df):
    gold_Dataframe_Metadata = {
        col: {
            "type": "string" if str(dtype) == "object" else str(dtype), 
            "description": DESCRIPTION.get(col, ""), 
            "confidentiality": CONFIDENTIALITY.get(col, "Confidentiel"),
            "owner": OWNER.get(col, "Unknown")
        }
        for col, dtype in df.dtypes.items()
    }
    with open(PATHS["yaml_metadata_gold"], "w", encoding="utf-8") as file:
        yaml.dump(gold_Dataframe_Metadata, file, allow_unicode=True, sort_keys=False)

def main():
    kpi = {}

    raw_Dataframe = extract_Dataframe_From_CSV(PATHS["csv"])

    silver_Dataframe, kpi = transform_Dataframe_Mail(raw_Dataframe, kpi)
    silver_Dataframe, kpi = transform_Dataframe_Salary(silver_Dataframe, kpi)
    silver_Dataframe, kpi = transform_Dataframe_Employment_Date(silver_Dataframe, kpi)

    gold_Dataframe = security_Dataframe_Full_Name(silver_Dataframe)
    gold_Dataframe = security_Dataframe_Social_Number(gold_Dataframe)

    show_Dataframe_With_Role(gold_Dataframe, "Admin")
    show_Dataframe_With_Role(gold_Dataframe, "Manager")
    print(kpi)
    
    generate_Dataframe_To_Dataframe(gold_Dataframe)

if __name__ == "__main__":
    main()