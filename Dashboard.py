# radio_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import folium_static
import random
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Localisation des Émetteurs - Freedom Radio Île de la Réunion",
    page_icon="📻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(45deg, #FF6B00, #FF9500, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .live-badge {
        background: linear-gradient(45deg, #FF6B00, #FF9500);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    .emitter-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B00;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #FF6B00;
        border-bottom: 2px solid #FF9500;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .status-active {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        color: #155724;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .status-inactive {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        color: #721c24;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .status-maintenance {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
        padding: 0.3rem 0.8rem;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

class RadioEmitterDashboard:
    def __init__(self):
        self.emitters = self.initialize_emitters()
        self.signal_data = self.initialize_signal_data()
        
    def initialize_emitters(self):
        """Initialise les données des 12 émetteurs de radio Freedom à La Réunion"""
        # Coordonnées approximatives des villes principales de La Réunion
        cities = {
            'Saint-Denis': (-20.8789, 55.4481),
            'Saint-Paul': (-21.0073, 55.2854),
            'Saint-Pierre': (-21.3429, 55.4787),
            'Le Tampon': (-21.3583, 55.5250),
            'Saint-André': (-20.9667, 55.6333),
            'Saint-Louis': (-21.2833, 55.4167),
            'Sainte-Marie': (-20.9167, 55.5667),
            'Sainte-Suzanne': (-20.8833, 55.6167),
            'Le Port': (-20.9333, 55.2833),
            'La Possession': (-20.9167, 55.3333),
            'Saint-Joseph': (-21.3667, 55.6167),
            'Cilaos': (-21.1333, 55.4667)
        }
        
        emitters = []
        emitter_id = 1
        
        for city, (lat, lon) in cities.items():
            # Ajout d'une légère variation aux coordonnées pour simuler des emplacements précis
            lat += random.uniform(-0.05, 0.05)
            lon += random.uniform(-0.05, 0.05)
            
            # Fréquences FM typiques
            frequency = random.uniform(88.0, 108.0)
            
            # Puissance en watts (varie selon l'emplacement)
            if city in ['Saint-Denis', 'Saint-Paul', 'Saint-Pierre']:
                power = random.choice([1000, 2000, 5000])  # Émetteurs principaux
            else:
                power = random.choice([100, 250, 500])  # Émetteurs secondaires
            
            # Statut aléatoire
            status_options = ['Actif', 'Actif', 'Actif', 'Maintenance', 'Inactif']
            status = random.choice(status_options)
            
            emitters.append({
                'id': f"FR-{emitter_id:03d}",
                'nom': f"Freedom Radio - {city}",
                'ville': city,
                'latitude': lat,
                'longitude': lon,
                'frequence': round(frequency, 1),
                'puissance': power,
                'altitude': random.randint(100, 1500),
                'date_installation': f"{random.randint(2005, 2022)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                'statut': status,
                'couverture': round(power * random.uniform(0.8, 1.2) / 10, 1),  # Rayon en km
                'technicien': f"Tech-{random.randint(1, 5):02d}",
                'derniere_maintenance': f"{random.randint(2023, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
            })
            emitter_id += 1
        
        return pd.DataFrame(emitters)
    
    def initialize_signal_data(self):
        """Initialise les données de signal pour chaque émetteur"""
        signal_data = []
        
        for _, emitter in self.emitters.iterrows():
            # Génération de données de signal pour les 7 derniers jours
            for day in range(7):
                date = pd.Timestamp.now() - pd.Timedelta(days=day)
                
                # Qualité du signal (0-100%)
                base_quality = random.uniform(70, 95)
                
                # Variations selon l'heure de la journée
                for hour in range(24):
                    hourly_quality = base_quality + random.uniform(-10, 10)
                    
                    # Périodes de maintenance
                    if emitter['statut'] == 'Maintenance' and hour in [2, 3, 4]:
                        hourly_quality = 0
                    
                    # Réduction de qualité la nuit
                    if hour in [0, 1, 2, 3, 4, 5]:
                        hourly_quality *= 0.9
                    
                    signal_data.append({
                        'emitter_id': emitter['id'],
                        'date': date,
                        'heure': hour,
                        'qualite': max(0, min(100, hourly_quality)),
                        'puissance': emitter['puissance'] * random.uniform(0.9, 1.1)
                    })
        
        return pd.DataFrame(signal_data)
    
    def display_header(self):
        """Affiche l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">📻 Localisation des Émetteurs Freedom Radio - Île de la Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="live-badge">🔴 SURVEILLANCE EN TEMPS RÉEL</div>', 
                       unsafe_allow_html=True)
            st.markdown("**Cartographie et surveillance des 12 émetteurs de radio Freedom à La Réunion**")
        
        current_time = pd.Timestamp.now().strftime('%H:%M:%S')
        st.sidebar.markdown(f"**🕐 Dernière mise à jour: {current_time}**")
    
    def display_key_metrics(self):
        """Affiche les métriques clés des émetteurs"""
        st.markdown('<h3 class="section-header">📊 INDICATEURS CLÉS DES ÉMETTEURS</h3>', 
                   unsafe_allow_html=True)
        
        # Calcul des métriques
        total_emitters = len(self.emitters)
        active_emitters = len(self.emitters[self.emitters['statut'] == 'Actif'])
        maintenance_emitters = len(self.emitters[self.emitters['statut'] == 'Maintenance'])
        inactive_emitters = len(self.emitters[self.emitters['statut'] == 'Inactif'])
        total_power = self.emitters['puissance'].sum()
        avg_coverage = self.emitters['couverture'].mean()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Émetteurs Actifs",
                f"{active_emitters}/{total_emitters}",
                f"{active_emitters - inactive_emitters - maintenance_emitters:+d}",
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Puissance Totale",
                f"{total_power/1000:.1f} kW",
                f"{random.randint(-5, 10)}% vs mois dernier"
            )
        
        with col3:
            st.metric(
                "Couverture Moyenne",
                f"{avg_coverage:.1f} km",
                f"{random.uniform(-2, 3):+.1f} km"
            )
        
        with col4:
            st.metric(
                "Émetteurs en Maintenance",
                f"{maintenance_emitters}",
                f"{maintenance_emitters - 1:+d} vs semaine dernière"
            )
    
    def create_map_view(self):
        """Crée la vue cartographique des émetteurs"""
        st.markdown('<h3 class="section-header">🗺️ CARTE DES ÉMETTEURS</h3>', 
                   unsafe_allow_html=True)
        
        # Création de la carte centrée sur La Réunion
        m = folium.Map(location=[-21.1151, 55.5364], zoom_start=10)
        
        # Ajout des marqueurs pour chaque émetteur
        for _, emitter in self.emitters.iterrows():
            # Couleur selon le statut
            if emitter['statut'] == 'Actif':
                color = 'green'
            elif emitter['statut'] == 'Maintenance':
                color = 'orange'
            else:
                color = 'red'
            
            # Création du popup avec informations
            popup_html = f"""
            <b>{emitter['nom']}</b><br>
            ID: {emitter['id']}<br>
            Fréquence: {emitter['frequence']} MHz<br>
            Puissance: {emitter['puissance']} W<br>
            Altitude: {emitter['altitude']} m<br>
            Couverture: {emitter['couverture']} km<br>
            Statut: {emitter['statut']}<br>
            Technicien: {emitter['technicien']}<br>
            Dernière maintenance: {emitter['derniere_maintenance']}
            """
            
            # Ajout du marqueur
            folium.Marker(
                location=[emitter['latitude'], emitter['longitude']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=f"{emitter['nom']} - {emitter['frequence']} MHz",
                icon=folium.Icon(color=color, icon='broadcast-tower', prefix='fa')
            ).add_to(m)
            
            # Ajout du cercle de couverture
            folium.Circle(
                location=[emitter['latitude'], emitter['longitude']],
                radius=emitter['couverture'] * 1000,  # Conversion en mètres
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.2,
                popup=f"Zone de couverture: {emitter['couverture']} km"
            ).add_to(m)
        
        # Affichage de la carte
        folium_static(m, width=1200, height=600)
    
    def create_emitter_details(self):
        """Affiche les détails de chaque émetteur"""
        st.markdown('<h3 class="section-header">📻 DÉTAILS DES ÉMETTEURS</h3>', 
                   unsafe_allow_html=True)
        
        # Filtres
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Filtrer par statut:", 
                                        ['Tous', 'Actif', 'Maintenance', 'Inactif'])
        with col2:
            power_filter = st.selectbox("Filtrer par puissance:", 
                                       ['Toutes', '> 1000W', '500-1000W', '< 500W'])
        with col3:
            sort_by = st.selectbox("Trier par:", 
                                  ['ID', 'Nom', 'Fréquence', 'Puissance', 'Statut'])
        
        # Application des filtres
        filtered_emitters = self.emitters.copy()
        
        if status_filter != 'Tous':
            filtered_emitters = filtered_emitters[filtered_emitters['statut'] == status_filter]
        
        if power_filter == '> 1000W':
            filtered_emitters = filtered_emitters[filtered_emitters['puissance'] > 1000]
        elif power_filter == '500-1000W':
            filtered_emitters = filtered_emitters[
                (filtered_emitters['puissance'] >= 500) & 
                (filtered_emitters['puissance'] <= 1000)
            ]
        elif power_filter == '< 500W':
            filtered_emitters = filtered_emitters[filtered_emitters['puissance'] < 500]
        
        # Tri
        if sort_by == 'ID':
            filtered_emitters = filtered_emitters.sort_values('id')
        elif sort_by == 'Nom':
            filtered_emitters = filtered_emitters.sort_values('nom')
        elif sort_by == 'Fréquence':
            filtered_emitters = filtered_emitters.sort_values('frequence')
        elif sort_by == 'Puissance':
            filtered_emitters = filtered_emitters.sort_values('puissance', ascending=False)
        elif sort_by == 'Statut':
            filtered_emitters = filtered_emitters.sort_values('statut')
        
        # Affichage des émetteurs
        for _, emitter in filtered_emitters.iterrows():
            # Classe CSS pour le statut
            status_class = ""
            if emitter['statut'] == 'Actif':
                status_class = "status-active"
            elif emitter['statut'] == 'Maintenance':
                status_class = "status-maintenance"
            else:
                status_class = "status-inactive"
            
            # Affichage de la carte d'émetteur
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**{emitter['id']}**")
                    st.markdown(f"<div class='{status_class}'>{emitter['statut']}</div>", 
                               unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"**{emitter['nom']}**")
                    st.markdown(f"📍 {emitter['latitude']:.4f}, {emitter['longitude']:.4f}")
                    st.markdown(f"📅 Installé le {emitter['date_installation']}")
                
                with col3:
                    st.markdown(f"**{emitter['frequence']} MHz**")
                    st.markdown(f"⚡ {emitter['puissance']} W")
                    st.markdown(f"📡 Couverture: {emitter['couverture']} km")
                
                with col4:
                    st.markdown(f"**Technicien:** {emitter['technicien']}")
                    st.markdown(f"**Dernière maintenance:** {emitter['derniere_maintenance']}")
                    
                    # Bouton pour voir les détails
                    if st.button(f"Détails {emitter['id']}", key=f"details_{emitter['id']}"):
                        st.session_state[f"show_details_{emitter['id']}"] = not st.session_state.get(f"show_details_{emitter['id']}", False)
                
                # Section de détails (cachée par défaut)
                if st.session_state.get(f"show_details_{emitter['id']}", False):
                    with st.expander(f"Informations détaillées - {emitter['id']}", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Informations techniques**")
                            st.markdown(f"- Altitude: {emitter['altitude']} m")
                            st.markdown(f"- Type d'antenne: Directionnelle")
                            st.markdown(f"- Azimut: {random.randint(0, 360)}°")
                            st.markdown(f"- Modèle d'émetteur: FM-{random.randint(1000, 9999)}")
                        
                        with col2:
                            st.markdown("**Historique de maintenance**")
                            for i in range(3):
                                date = pd.Timestamp.now() - pd.Timedelta(days=30*i)
                                st.markdown(f"- {date.strftime('%Y-%m-%d')}: Maintenance {random.choice(['préventive', 'corrective', 'upgrade'])}")
                        
                        # Graphique de qualité du signal
                        emitter_signal = self.signal_data[self.signal_data['emitter_id'] == emitter['id']]
                        if not emitter_signal.empty:
                            # Moyenne par heure pour les 7 derniers jours
                            hourly_avg = emitter_signal.groupby('heure')['qualite'].mean().reset_index()
                            
                            fig = px.line(
                                hourly_avg, 
                                x='heure', 
                                y='qualite',
                                title=f"Qualité du signal moyenne par heure - {emitter['id']}",
                                labels={'heure': 'Heure de la journée', 'qualite': 'Qualité du signal (%)'}
                            )
                            fig.update_layout(yaxis_range=[0, 100])
                            st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
    
    def create_signal_analysis(self):
        """Analyse des signaux des émetteurs"""
        st.markdown('<h3 class="section-header">📈 ANALYSE DES SIGNAUX</h3>', 
                   unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Qualité du Signal", "Puissance d'Émission", "Couverture"])
        
        with tab1:
            # Qualité du signal par émetteur
            col1, col2 = st.columns(2)
            
            with col1:
                # Qualité actuelle par émetteur
                current_quality = []
                for _, emitter in self.emitters.iterrows():
                    # Qualité actuelle simulée
                    if emitter['statut'] == 'Actif':
                        quality = random.uniform(70, 95)
                    elif emitter['statut'] == 'Maintenance':
                        quality = random.uniform(0, 50)
                    else:
                        quality = 0
                    
                    current_quality.append({
                        'emitter_id': emitter['id'],
                        'nom': emitter['nom'],
                        'qualite': quality,
                        'statut': emitter['statut']
                    })
                
                quality_df = pd.DataFrame(current_quality)
                
                fig = px.bar(
                    quality_df, 
                    x='nom', 
                    y='qualite',
                    color='statut',
                    title="Qualité actuelle du signal par émetteur",
                    labels={'qualite': 'Qualité du signal (%)', 'nom': 'Émetteur'},
                    color_discrete_map={'Actif': 'green', 'Maintenance': 'orange', 'Inactif': 'red'}
                )
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Évolution de la qualité sur 7 jours
                daily_avg = self.signal_data.groupby(['emitter_id', 'date'])['qualite'].mean().reset_index()
                
                # Sélection de quelques émetteurs pour la lisibilité
                selected_emitters = random.sample(list(self.emitters['id'].unique()), min(5, len(self.emitters)))
                filtered_data = daily_avg[daily_avg['emitter_id'].isin(selected_emitters)]
                
                fig = px.line(
                    filtered_data, 
                    x='date', 
                    y='qualite',
                    color='emitter_id',
                    title="Évolution de la qualité du signal (7 derniers jours)",
                    labels={'qualite': 'Qualité du signal (%)', 'date': 'Date'}
                )
                fig.update_layout(yaxis_range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Analyse de la puissance d'émission
            col1, col2 = st.columns(2)
            
            with col1:
                # Puissance par émetteur
                fig = px.bar(
                    self.emitters, 
                    x='nom', 
                    y='puissance',
                    color='statut',
                    title="Puissance d'émission par émetteur",
                    labels={'puissance': 'Puissance (W)', 'nom': 'Émetteur'},
                    color_discrete_map={'Actif': 'green', 'Maintenance': 'orange', 'Inactif': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition de la puissance
                power_ranges = ['< 500W', '500-1000W', '> 1000W']
                power_counts = [
                    len(self.emitters[self.emitters['puissance'] < 500]),
                    len(self.emitters[(self.emitters['puissance'] >= 500) & (self.emitters['puissance'] <= 1000)]),
                    len(self.emitters[self.emitters['puissance'] > 1000])
                ]
                
                fig = px.pie(
                    values=power_counts, 
                    names=power_ranges,
                    title="Répartition des émetteurs par puissance",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Analyse de la couverture
            col1, col2 = st.columns(2)
            
            with col1:
                # Couverture par émetteur
                fig = px.bar(
                    self.emitters, 
                    x='nom', 
                    y='couverture',
                    color='statut',
                    title="Rayon de couverture par émetteur",
                    labels={'couverture': 'Rayon de couverture (km)', 'nom': 'Émetteur'},
                    color_discrete_map={'Actif': 'green', 'Maintenance': 'orange', 'Inactif': 'red'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Carte de chaleur de couverture
                # Création d'une grille pour la carte de chaleur
                lat_min, lat_max = -21.4, -20.8
                lon_min, lon_max = 55.2, 55.7
                
                # Génération de points sur une grille
                grid_points = 50
                lats = np.linspace(lat_min, lat_max, grid_points)
                lons = np.linspace(lon_min, lon_max, grid_points)
                
                heatmap_data = []
                for lat in lats:
                    for lon in lons:
                        # Calcul de la force du signal à ce point
                        signal_strength = 0
                        for _, emitter in self.emitters.iterrows():
                            if emitter['statut'] == 'Actif':
                                # Distance simple (approximation)
                                distance = np.sqrt((lat - emitter['latitude'])**2 + (lon - emitter['longitude'])**2)
                                # Signal décroît avec la distance
                                emitter_signal = max(0, 100 - distance * 100 / emitter['couverture'])
                                signal_strength = max(signal_strength, emitter_signal)
                        
                        heatmap_data.append([lat, lon, signal_strength])
                
                heatmap_df = pd.DataFrame(heatmap_data, columns=['lat', 'lon', 'signal'])
                
                fig = px.density_heatmap(
                    heatmap_df, 
                    x='lon', 
                    y='lat', 
                    z='signal',
                    title="Carte de chaleur de la couverture radio",
                    labels={'lon': 'Longitude', 'lat': 'Latitude', 'signal': 'Force du signal (%)'},
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    def create_maintenance_view(self):
        """Vue de maintenance des émetteurs"""
        st.markdown('<h3 class="section-header">🔧 PLANIFICATION DE LA MAINTENANCE</h3>', 
                   unsafe_allow_html=True)
        
        # Tableau de maintenance
        maintenance_schedule = []
        
        for _, emitter in self.emitters.iterrows():
            # Prochaine maintenance planifiée
            if emitter['statut'] == 'Maintenance':
                next_maintenance = pd.Timestamp.now()
                priority = "Élevée"
            else:
                days_until = random.randint(1, 90)
                next_maintenance = pd.Timestamp.now() + pd.Timedelta(days=days_until)
                
                if days_until < 7:
                    priority = "Élevée"
                elif days_until < 30:
                    priority = "Moyenne"
                else:
                    priority = "Basse"
            
            maintenance_schedule.append({
                'emitter_id': emitter['id'],
                'nom': emitter['nom'],
                'statut': emitter['statut'],
                'derniere_maintenance': emitter['derniere_maintenance'],
                'prochaine_maintenance': next_maintenance.strftime('%Y-%m-%d'),
                'priorite': priority,
                'technicien': emitter['technicien'],
                'taches': random.choice(["Vérification antenne", "Calibrage fréquence", "Remplacement pièces", "Mise à jour logiciel"])
            })
        
        maintenance_df = pd.DataFrame(maintenance_schedule)
        
        # Tri par priorité et date
        priority_order = {"Élevée": 0, "Moyenne": 1, "Basse": 2}
        maintenance_df['priorite_order'] = maintenance_df['priorite'].map(priority_order)
        maintenance_df = maintenance_df.sort_values(['priorite_order', 'prochaine_maintenance'])
        
        # Affichage du tableau
        for _, maintenance in maintenance_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{maintenance['emitter_id']}**")
                if maintenance['statut'] == 'Maintenance':
                    st.markdown('<div class="status-maintenance">En cours</div>', unsafe_allow_html=True)
                elif maintenance['priorite'] == 'Élevée':
                    st.markdown('<div class="status-inactive">Urgent</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-active">Planifié</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{maintenance['nom']}**")
                st.markdown(f"Tâche: {maintenance['taches']}")
            
            with col3:
                st.markdown(f"**{maintenance['prochaine_maintenance']}**")
                st.markdown(f"Dernière: {maintenance['derniere_maintenance']}")
            
            with col4:
                st.markdown(f"**Priorité:** {maintenance['priorite']}")
                st.markdown(f"**Technicien:** {maintenance['technicien']}")
            
            with col5:
                if st.button(f"Planifier", key=f"plan_{maintenance['emitter_id']}"):
                    st.session_state[f"plan_{maintenance['emitter_id']}"] = True
            
            # Formulaire de planification (caché par défaut)
            if st.session_state.get(f"plan_{maintenance['emitter_id']}", False):
                with st.expander(f"Planification de maintenance - {maintenance['emitter_id']}", expanded=True):
                    with st.form(key=f"maintenance_form_{maintenance['emitter_id']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            date = st.date_input("Date de maintenance", value=pd.Timestamp.now())
                            heure = st.time_input("Heure de maintenance", value=pd.Timestamp.now().time())
                            technicien = st.selectbox("Technicien", [f"Tech-{i:02d}" for i in range(1, 6)])
                        
                        with col2:
                            duree = st.number_input("Durée estimée (heures)", min_value=1, max_value=24, value=2)
                            taches = st.multiselect("Tâches à effectuer", [
                                "Vérification antenne", "Calibrage fréquence", "Remplacement pièces", 
                                "Mise à jour logiciel", "Nettoyage équipement", "Test de signal"
                            ])
                            notes = st.text_area("Notes additionnelles")
                        
                        submitted = st.form_submit_button("Confirmer la planification")
                        if submitted:
                            st.success(f"Maintenance planifiée pour {maintenance['emitter_id']} le {date} à {heure}")
                            st.session_state[f"plan_{maintenance['emitter_id']}"] = False
            
            st.markdown("---")
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        st.sidebar.markdown("## 🎛️ CONTRÔLES D'ANALYSE")
        
        # Filtres temporels
        st.sidebar.markdown("### 📅 Période d'analyse")
        date_debut = st.sidebar.date_input("Date de début", 
                                         value=pd.Timestamp.now() - pd.Timedelta(days=7))
        date_fin = st.sidebar.date_input("Date de fin", 
                                       value=pd.Timestamp.now())
        
        # Filtres de statut
        st.sidebar.markdown("### 📻 Filtres des émetteurs")
        statuts_selectionnes = st.sidebar.multiselect(
            "Statuts à afficher:",
            list(self.emitters['statut'].unique()),
            default=list(self.emitters['statut'].unique())
        )
        
        # Options d'affichage
        st.sidebar.markdown("### ⚙️ Options")
        auto_refresh = st.sidebar.checkbox("Rafraîchissement automatique", value=True)
        show_coverage = st.sidebar.checkbox("Afficher zones de couverture", value=True)
        
        # Bouton de rafraîchissement manuel
        if st.sidebar.button("🔄 Rafraîchir les données"):
            st.rerun()
        
        # Informations système
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📡 INFORMATIONS SYSTÈME")
        
        # Statistiques système
        st.sidebar.metric(
            "Émetteurs surveillés",
            len(self.emitters)
        )
        
        st.sidebar.metric(
            "Alertes actives",
            random.randint(0, 3)
        )
        
        st.sidebar.metric(
            "Mises à jour aujourd'hui",
            random.randint(1, 5)
        )
        
        return {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'statuts_selectionnes': statuts_selectionnes,
            'auto_refresh': auto_refresh,
            'show_coverage': show_coverage
        }

    def run_dashboard(self):
        """Exécute le dashboard complet"""
        # Sidebar
        controls = self.create_sidebar()
        
        # Header
        self.display_header()
        
        # Métriques clés
        self.display_key_metrics()
        
        # Navigation par onglets
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗺️ Carte", 
            "📻 Émetteurs", 
            "📈 Signaux", 
            "🔧 Maintenance",
            "ℹ️ À Propos"
        ])
        
        with tab1:
            self.create_map_view()
        
        with tab2:
            self.create_emitter_details()
        
        with tab3:
            self.create_signal_analysis()
        
        with tab4:
            self.create_maintenance_view()
        
        with tab5:
            st.markdown("## 📋 À propos de ce dashboard")
            st.markdown("""
            Ce dashboard présente une vue d'ensemble des 12 émetteurs de radio Freedom 
            situés sur l'île de La Réunion.
            
            **Fonctionnalités:**
            - Cartographie des émetteurs avec zones de couverture
            - Surveillance en temps réel du statut des émetteurs
            - Analyse de la qualité du signal
            - Planification des maintenances
            
            **Données affichées:**
            - Localisation géographique précise
            - Fréquences et puissances d'émission
            - Statut opérationnel
            - Historique de maintenance
            
            **⚠️ Avertissement:** 
            Les données présentées sont simulées pour la démonstration.
            Les coordonnées et informations techniques sont des exemples.
            """)
            
            st.markdown("---")
            st.markdown("""
            **📞 Contact:**
            - Service technique: tech@freedomradio.re
            - Urgence: +262 262 123 456
            - Siège: Saint-Denis, La Réunion
            """)

# Lancement du dashboard
if __name__ == "__main__":
    dashboard = RadioEmitterDashboard()
    dashboard.run_dashboard()