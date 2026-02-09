import altair as alt
import duckdb
import pandas as pd
import streamlit as st
import os
st.set_page_config(
    page_title="RetailStore Suisse – Performance commerciale",
    layout="wide",
    page_icon="📊",
)


@st.cache_data(ttl=3600, show_spinner=False)
def load_sales() -> pd.DataFrame:
    query = """
        select
            fs.id_commande,
            fs.id_magasin,
            fs.num_ligne,
            fs.date_commande,
            fs.date_livraison,
            fs.code_canal,
            fs.code_type_commande,
            fs.id_client,
            fs.code_transporteur,
            fs.code_produit,
            fs.code_produit_interne,
            fs.quantite_commandee,
            fs.montant_total_ligne,
            fs.montant_tva,
            fs.prix_unitaire_vente,
            ds.nom_magasin,
            ds.nom_court_magasin,
            ds.region,
            ds.type_site,
            ds.surface_m2,
            ds.latitude,
            ds.longitude,
            ds.code_postal,
            dp.nom_produit_fr,
            dp.famille_produit,
            dp.groupe_caracteristique,
            dp.libelle_groupe
        from fact_sales fs
        left join dim_store ds on fs.id_magasin = ds.id_magasin
        left join dim_product dp on fs.code_produit = dp.code_produit
    """

    db_dir = os.path.dirname(__file__)
    db_path = os.path.join(db_dir, "dev.duckdb")
    os.chdir(db_dir)
    with duckdb.connect(database=db_path, read_only=True) as con:
            df = con.sql(query).df()

    df["date_commande"] = pd.to_datetime(df["date_commande"])
    df["date_livraison"] = pd.to_datetime(df["date_livraison"])
    df["montant_total_ligne"] = pd.to_numeric(df["montant_total_ligne"], errors="coerce").fillna(0.0)
    df["quantite_commandee"] = pd.to_numeric(df["quantite_commandee"], errors="coerce").fillna(0.0)

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    df["jour_semaine"] = pd.Categorical(
        df["date_commande"].dt.day_name(),
        categories=weekday_order,
        ordered=True,
    )
    canal_map = {"0": "Magasin", "54": "Web"}
    df["canal_libelle"] = df["code_canal"].astype(str).map(canal_map).fillna("Autre canal")
    df["jour"] = df["date_commande"].dt.date
    df["semaine"] = df["date_commande"].dt.to_period("W-MON").apply(lambda p: p.start_time)
    df["mois"] = df["date_commande"].dt.to_period("M").dt.to_timestamp()
    df["annee"] = df["date_commande"].dt.year

    return df


def format_currency(value: float) -> str:
    return f"{value:,.0f} CHF".replace(",", " ")


df_sales = load_sales()

min_date = df_sales["date_commande"].min().date()
max_date = df_sales["date_commande"].max().date()

with st.sidebar:
    st.header("🎯 Filtres")
    start_date, end_date = st.date_input(
        "Période analysée",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    region_options = sorted(df_sales["region"].dropna().unique())
    selected_regions = st.multiselect(
        "Régions",
        options=region_options,
        default=region_options,
    )

    canal_options = sorted(df_sales["canal_libelle"].dropna().unique())
    selected_canaux = st.multiselect(
        "Canaux",
        options=canal_options,
        default=canal_options,
    )

    type_site_options = sorted(df_sales["type_site"].dropna().unique())
    selected_types = st.multiselect(
        "Type de site",
        options=type_site_options,
        default=type_site_options,
    )

    magasin_options = sorted(df_sales["nom_magasin"].dropna().unique())
    selected_magasins = st.multiselect(
        "Magasins",
        options=magasin_options,
    )

    st.caption("Retirer toutes les valeurs d'un filtre revient à afficher l'ensemble des données.")


mask = (
    (df_sales["date_commande"].dt.date >= start_date)
    & (df_sales["date_commande"].dt.date <= end_date)
)

if selected_regions:
    mask &= df_sales["region"].isin(selected_regions)
if selected_canaux:
    mask &= df_sales["canal_libelle"].isin(selected_canaux)
if selected_types:
    mask &= df_sales["type_site"].isin(selected_types)
if selected_magasins:
    mask &= df_sales["nom_magasin"].isin(selected_magasins)

df_filtered = df_sales.loc[mask].copy()

if df_filtered.empty:
    st.warning("Aucune vente ne correspond aux filtres sélectionnés.")
    st.stop()


st.title("📊 Performance commerciale RetailStore Suisse")
st.caption("Projet de : Nabil BOUTIYARZIST - Vue consolidée bâtie à partir des modèles marts (fact_sales, dim_store, dim_product).")


total_sales = df_filtered["montant_total_ligne"].sum()
order_count = df_filtered["id_commande"].nunique()
client_count = df_filtered["id_client"].nunique()
avg_basket = total_sales / order_count if order_count else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Chiffre d'affaires", format_currency(total_sales))
col2.metric("Commandes", f"{order_count:,}".replace(",", " "))
col3.metric("Clients", f"{client_count:,}".replace(",", " "))
col4.metric("Panier moyen", format_currency(avg_basket))

st.divider()

granularite = st.radio(
    "Granularité temporelle",
    ["Jour", "Semaine", "Mois", "Année"],
    horizontal=True,
)

freq_map = {
    "Jour": "D",
    "Semaine": "W-MON",
    "Mois": "M",
    "Année": "Y",
}

ts = (
    df_filtered.set_index("date_commande")["montant_total_ligne"]
    .resample(freq_map[granularite])
    .sum()
    .reset_index()
    .rename(columns={"date_commande": "periode", "montant_total_ligne": "chiffre_affaires"})
)

line_chart = (
    alt.Chart(ts)
    .mark_line(point=True)
    .encode(
        x=alt.X("periode:T", title="Période"),
        y=alt.Y("chiffre_affaires:Q", title="Chiffre d'affaires"),
        tooltip=["periode:T", alt.Tooltip("chiffre_affaires:Q", title="CA", format=",.0f")],
    )
    .properties(height=320)
)

dim_map = {
    "Région": "region",
    "Magasin": "nom_magasin",
    "Canal": "canal_libelle",
    "Type de site": "type_site",
}

comparison_choice = st.selectbox(
    "Comparer la performance par :",
    list(dim_map.keys()),
)

dimension_col = dim_map[comparison_choice]
comparison = (
    df_filtered.assign(_dimension=df_filtered[dimension_col].fillna("Non renseigné"))
    .groupby("_dimension")["montant_total_ligne"]
    .sum()
    .reset_index()
    .rename(columns={"_dimension": comparison_choice, "montant_total_ligne": "chiffre_affaires"})
)
comparison = comparison.sort_values("chiffre_affaires", ascending=False).head(15)

bar_chart = (
    alt.Chart(comparison)
    .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
    .encode(
        x=alt.X("chiffre_affaires:Q", title="Chiffre d'affaires"),
        y=alt.Y(f"{comparison_choice}:N", sort="-x", title=comparison_choice),
        tooltip=[comparison_choice, alt.Tooltip("chiffre_affaires:Q", title="CA", format=",.0f")],
        color=alt.Color("chiffre_affaires:Q", legend=None, scale=alt.Scale(scheme="blues")),
    )
    .properties(height=350)
)

col_time, col_split = st.columns((2, 1))
with col_time:
    st.subheader("📈 Évolution du chiffre d'affaires")
    st.altair_chart(line_chart, use_container_width=True)

with col_split:
    st.subheader(f"🏪 {comparison_choice} les plus contributeurs")
    st.altair_chart(bar_chart, use_container_width=True)

st.divider()

channel_mix = (
    df_filtered.assign(_canal=df_filtered["canal_libelle"].fillna("Non renseigné"))
    .groupby("_canal")["montant_total_ligne"]
    .sum()
    .reset_index()
    .rename(columns={"_canal": "Canal", "montant_total_ligne": "chiffre_affaires"})
)
channel_mix["part"] = channel_mix["chiffre_affaires"] / channel_mix["chiffre_affaires"].sum()

store_geo = (
    df_filtered.dropna(subset=["latitude", "longitude", "nom_magasin"])
    .groupby(["nom_magasin", "region", "latitude", "longitude"], as_index=False)["montant_total_ligne"]
    .sum()
    .rename(columns={"montant_total_ligne": "chiffre_affaires"})
)

col_mix, col_map = st.columns((1, 1))
with col_mix:
    st.subheader("🔀 Répartition du CA par canal")
    donut = (
        alt.Chart(channel_mix)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta("chiffre_affaires:Q"),
            color=alt.Color("Canal:N", title="Canal"),
            tooltip=["Canal", alt.Tooltip("chiffre_affaires:Q", title="CA", format=",.0f"), alt.Tooltip("part:Q", title="Part", format=".0%")],
        )
        .properties(height=300)
    )
    st.altair_chart(donut, use_container_width=True)

with col_map:
    st.subheader("🗺️ Magasins (CA cumulé)")
    if store_geo.empty:
        st.info("Pas de coordonnées exploitables pour cette sélection.")
    else:
        #st.map(store_geo.rename(columns={"latitude": "lat", "longitude": "lon"}))
        store_geo['taille_affichage'] = store_geo['chiffre_affaires'] / 600

        st.map(
            store_geo.rename(columns={"latitude": "lat", "longitude": "lon"}),
            size="taille_affichage", 
            color="#FF4B4B"
        )

st.divider()

top_categories = (
    df_filtered.assign(_famille=df_filtered["famille_produit"].fillna("Non renseigné"))
    .groupby("_famille")
    .agg(
        chiffre_affaires=("montant_total_ligne", "sum"),
        volume=("quantite_commandee", "sum"),
    )
    .reset_index()
    .rename(columns={"_famille": "Famille"})
)
top_categories = top_categories.sort_values("chiffre_affaires", ascending=False).head(10)

top_products = (
    df_filtered.assign(
        _code=df_filtered["code_produit_interne"].fillna("Non renseigné"),
        _produit=df_filtered["nom_produit_fr"].fillna("Non renseigné"),
    )
    .groupby(["_code", "_produit"])
    .agg(
        chiffre_affaires=("montant_total_ligne", "sum"),
        volume=("quantite_commandee", "sum"),
    )
    .reset_index()
    .rename(columns={"_code": "Code produit", "_produit": "Produit"})
)
top_products = top_products.sort_values("chiffre_affaires", ascending=False).head(15)

col_cat, col_prod = st.columns((1, 1))
with col_cat:
    st.subheader("🥇 Top 10 des familles produits")
    st.dataframe(
        top_categories.assign(
            chiffre_affaires=top_categories["chiffre_affaires"].map(format_currency),
        ),
        use_container_width=True,
        hide_index=True,
    )

with col_prod:
    st.subheader("🏆 Top 15 des produits")
    st.dataframe(
        top_products.assign(
            chiffre_affaires=top_products["chiffre_affaires"].map(format_currency),
        ),
        use_container_width=True,
        hide_index=True,
    )

