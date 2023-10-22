import pandas as pd
import streamlit as st
import plotly.express as px
import requests
from io import StringIO


st.sidebar.title('Menu')
st.sidebar.subheader('Data Visualisation project')
st.sidebar.markdown(
    """
        <br>
        <div class="conteneur">
            <p>Teacher: Djallel DILMI</p>
            <p>Developer : Rémi Belmadani</p>
            <p>Efrei Paris- Promo 2025</p>
            <p>#datavz2023efrei</p>
            <div class="ma-div">
                <a href="https://www.linkedin.com/in/remiblmn/" target="_blank" style="text-decoration: none; color:white">
                <div style="background-color: #0077B5; color: white; padding: 10px 20px; border-radius: 5px; display: flex; align-items: center; width: 200px; justify-content: center;">
                    <img src="https://cdn.jsdelivr.net/npm/simple-icons@v3/icons/linkedin.svg" alt="LinkedIn Logo" height="20px" style="margin-right: 10px;">
                    LinkedIn
                </div>
            </a>
            </div>
        </div>
        """,
    unsafe_allow_html=True
)

st.title("Comment les jeunes diplômés s'insèrent-ils dans le milieu professionnel à la sortir de Master ?")

url = "https://data.enseignementsup-recherche.gouv.fr/explore/dataset/fr-esr-insertion_professionnelle-master/download?format=csv"
response = requests.get(url, verify=False)
csv_data = response.text
csv_file = StringIO(csv_data)
df = pd.read_csv(csv_file, sep=';')

clean_data = df.drop_duplicates()
clean_data = clean_data.drop(columns=['numero_de_l_etablissement','code_de_l_academie','code_du_domaine','code_de_la_discipline','poids_de_la_discipline','cle_disc','id_paysage'])
clean_data = clean_data.drop(columns=['salaire_net_mensuel_regional_1er_quartile','salaire_net_mensuel_regional_3eme_quartile','cle_etab','remarque'])

clean_data = clean_data[~clean_data["etablissementactuel"].notna()]
clean_data = clean_data[clean_data["femmes"].notna()]
clean_data = clean_data[clean_data["emplois_exterieurs_a_la_region_de_luniversite"].notna()]
clean_data = clean_data[clean_data["de_diplomes_boursiers"].notna()]

clean_data = clean_data[~clean_data["femmes"].isin(["ns", "nd", "."])]
clean_data = clean_data[~clean_data["emplois_exterieurs_a_la_region_de_luniversite"].isin(["ns", "nd", "."])]
clean_data = clean_data[~clean_data["emplois_cadre"].isin(["ns", "nd", "."])]
clean_data = clean_data[~clean_data["salaire_brut_annuel_estime"].isin(["ns", "nd", "."])]
clean_data = clean_data.query("`nombre_de_reponses`.notna() and `nombre_de_reponses` != 0 and `taux_de_reponse` > 50")
clean_data = clean_data.drop(columns=['etablissementactuel'])
clean_data = clean_data[clean_data["academie"].notna()]

# Show number of acamedies per city

clean_data['academie'] = clean_data['academie'].astype(str)
academie_counts = clean_data['academie'].value_counts().reset_index()
academie_counts.columns = ['Academie', 'Count']

fig = px.bar(academie_counts, x='Academie', y='Count')
fig.update_layout(
    title='Nombre d étudiant par académie',
    xaxis_title='Academie',
    yaxis_title='Nombre d étudiants'
)
st.plotly_chart(fig)

st.write("On remarque déjà que les académies sont concentrés dans les grandes villes")

# Student per year

students_per_year = clean_data.groupby('annee').size().reset_index()
students_per_year.columns = ['Année', 'Nombre d`étudiants']
fig = px.bar(students_per_year, x='Année', y='Nombre d`étudiants', labels={'Année': 'Année', 'Nombre d`étudiants': 'Nombre d`étudiants'})
fig.update_layout(xaxis_title='Année', yaxis_title='Nombre d`étudiants')
fig.update_xaxes(type='category')
st.plotly_chart(fig)

# Répartition étudiants par domaine et étude focus sur les femmes

selected_chart = st.selectbox("Sélectionnez le graphique à afficher", ["Répartition des domaines par rapport au nombre total d'étudiants", "Répartition des femmes par domaine"])

if selected_chart == "Répartition des domaines par rapport au nombre total d'étudiants":
    domaine_pourcent = clean_data['domaine'].value_counts().reset_index()
    domaine_pourcent.columns = ['Domaine', 'Nombre d`étudiants']
    total_students = len(clean_data)
    domaine_pourcent['Pourcentage'] = (domaine_pourcent['Nombre d`étudiants'] / total_students) * 100
    fig = px.pie(domaine_pourcent, names='Domaine', values='Pourcentage', title="Répartition des domaines par rapport au nombre total d'étudiants")
    st.plotly_chart(fig)

if selected_chart == "Répartition des femmes par domaine":
    clean_data['femmes'] = pd.to_numeric(clean_data['femmes'], errors='coerce')
    dom_femmes = clean_data.groupby('domaine')['femmes'].sum().reset_index()
    fig = px.pie(dom_femmes, names='domaine', values='femmes', title="Répartition des femmes par domaine")
    st.plotly_chart(fig)

st.write("On remarque que les femmes ont plus tendance à s'orienter vers le droit, l'économie, la gestion et les sciences humaines et sociales. Elles délaissent les technologies, les sciences et le domaine de la santé")

# Taux d'insertion et emplois cadre

clean_data['taux_dinsertion'] = pd.to_numeric(clean_data['taux_dinsertion'], errors='coerce')
clean_data['emplois_cadre'] = pd.to_numeric(clean_data['emplois_cadre'], errors='coerce')
selected_columns = clean_data[['domaine', 'taux_dinsertion', 'emplois_cadre']]
domaine_stats = selected_columns.groupby('domaine').mean()
domaine_stats = domaine_stats.rename(columns={'taux_dinsertion': 'Taux d insertion moyen', 'emplois_cadre': 'Taux de cadres moyen'})
st.write("Statistiques par domaine :")
st.write(domaine_stats)

st.write("Nous pouvons remarquer après avoir parcouru les données que les étudiants s'orientent vers le domaine général du droit ou de la technologie, des domaines porteurs, qui ont une insertion à la sortie de l'école plus haute que dans les autres domaines.")
st.write("Observons maintenant ces données en profondeur pour savoir si c'est la seule raison qui pousse les étudiants à se tourner vers ces domaines")


st.title("Partie 2 : Exploration en profondeur")

# Taux d'insertion par académie et salaire : corrélation ?

clean_data['salaire_brut_annuel_estime'] = pd.to_numeric(clean_data['salaire_brut_annuel_estime'], errors='coerce')
selected_chart = st.selectbox("Sélectionnez le graphique à afficher", ["Taux d'insertion par académie", "Salaire par académie"])

if selected_chart == "Taux d'insertion par académie":
    academie_taux_insertion = clean_data.groupby('academie')['taux_dinsertion'].mean().reset_index()
    academie_taux_insertion.columns = ['Academie', 'Taux d\'insertion moyen']
    fig_insertion = px.bar(academie_taux_insertion, x='Academie', y='Taux d\'insertion moyen', labels={'Taux d\'insertion moyen': 'Taux d\'insertion moyen'}, title='Taux d\'insertion moyen par académie')
    fig_insertion.update_xaxes(categoryorder='total ascending')
    st.plotly_chart(fig_insertion)

if selected_chart == "Salaire par académie":
    academie_salaire = clean_data.groupby('academie')['salaire_brut_annuel_estime'].mean().reset_index()
    academie_salaire.columns = ['Academie', 'Salaire brut annuel estimé']
    fig_salaire = px.bar(academie_salaire, x='Academie', y='Salaire brut annuel estimé', labels={'Salaire brut annuel estimé': 'Salaire brut annuel estimé'}, title='Salaire brut annuel estimé par académie')
    fig_salaire.update_xaxes(categoryorder='total ascending')
    st.plotly_chart(fig_salaire)

st.write("On remarque dans l'ensemble un très bon taux d'insertion à la sortie de master, quelque soit le domaine. On remarque aussi que le taux d'insertion par académie n'influe pas sur la différence des salaire.")

# Salaire par rapport au domaine

clean_data['salaire_brut_annuel_estime'] = pd.to_numeric(clean_data['salaire_brut_annuel_estime'], errors='coerce')
domaine_salaire = clean_data.groupby('domaine')['salaire_brut_annuel_estime'].mean().reset_index()
st.bar_chart(domaine_salaire.set_index('domaine'), use_container_width=True)
st.write("Nous pouvons tirer de ces graphiques c'est que les domaines où il y a le meilleur salaire sont les domaines des sciences et du droit.")


# Taux de chômage

clean_data['taux_de_chomage_regional'] = pd.to_numeric(clean_data['taux_de_chomage_regional'], errors='coerce')
clean_data['emplois_exterieurs_a_la_region_de_luniversite'] = pd.to_numeric(clean_data['emplois_exterieurs_a_la_region_de_luniversite'], errors='coerce')
selected_chart = st.selectbox("Sélectionnez le graphique à afficher", ["Taux de chômage régional", "Taux d'emplois extérieurs à la région"])

if selected_chart == "Taux de chômage régional":
    chom_academie = clean_data.groupby('academie')['taux_de_chomage_regional'].mean().reset_index()
    fig_academie = px.bar(chom_academie, x='academie', y='taux_de_chomage_regional', title='Taux de chômage régional par académie')
    fig_academie.update_xaxes(categoryorder='total ascending')
    st.plotly_chart(fig_academie)

if selected_chart == "Taux d'emplois extérieurs à la région":
    emplois_ext = clean_data.groupby('academie')['emplois_exterieurs_a_la_region_de_luniversite'].mean().reset_index()
    fig_ext = px.bar(emplois_ext, x='academie', y='emplois_exterieurs_a_la_region_de_luniversite', title='Taux d emplois extérieurs à la région')
    fig_ext.update_xaxes(categoryorder='total ascending')
    st.plotly_chart(fig_ext)

st.write("On remarque que le taux de chômage influe sur le fait que les nouveaux diplômés auront tendance à partir de la région de leur université pour trouver du travail.")

