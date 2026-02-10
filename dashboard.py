import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import json
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Dashboard de Voos - Aeroporto Pinto Martins (SBFZ)",
    page_icon="✈️",
    layout="wide"
)

# Constants
DATA_PATH = "/Users/tiago/anac_data_2025"
TARGET_AIRPORT = "SBFZ"

@st.cache_data
def load_data():
    """Loads all JSON files from the data directory and combines them into a DataFrame."""
    all_files = glob.glob(os.path.join(DATA_PATH, "*.json"))
    
    if not all_files:
        st.error(f"Nenhum arquivo JSON encontrado em {DATA_PATH}")
        return pd.DataFrame()
    
    df_list = []
    for f in all_files:
        try:
            with open(f, 'r', encoding='utf-8-sig') as file:
                data = json.load(file)
                # JSON data might be a list of dicts
                if isinstance(data, list):
                    df_list.extend(data)
        except Exception as e:
            st.warning(f"Erro ao ler arquivo {f}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    df = pd.DataFrame(df_list)
    
    # Convert date columns to datetime
    date_cols = ['PartidaPrevista', 'PartidaReal', 'ChegadaPrevista', 'ChegadaReal']
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
    return df

def main():
    st.title("✈️ Dashboard de Análise de Voos - Fortaleza (SBFZ)")
    st.markdown("Exploração interativa dos dados de voos da ANAC para o Aeroporto Pinto Martins.")

    with st.spinner('Carregando dados...'):
        df_raw = load_data()
        
    if df_raw.empty:
        st.warning("Não há dados disponíveis para exibir.")
        return

    # Sidebar Filters
    st.sidebar.header("Filtros")
    
    # Filter by Airport (Default SBFZ)
    airports = sorted(list(set(df_raw['ICAOAeródromoOrigem'].unique()) | set(df_raw['ICAOAeródromoDestino'].unique())))
    if TARGET_AIRPORT in airports:
        default_index = airports.index(TARGET_AIRPORT)
    else:
        default_index = 0
        
    selected_airport = st.sidebar.selectbox("Selecione o Aeroporto", airports, index=default_index)
    
    # Filter data for selected airport (either Origin or Destination)
    df = df_raw[(df_raw['ICAOAeródromoOrigem'] == selected_airport) | (df_raw['ICAOAeródromoDestino'] == selected_airport)].copy()
    
    # Filter by Date Range
    min_date = df['PartidaPrevista'].min().date()
    max_date = df['PartidaPrevista'].max().date()
    
    start_date, end_date = st.sidebar.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    df = df[
        (df['PartidaPrevista'].dt.date >= start_date) & 
        (df['PartidaPrevista'].dt.date <= end_date)
    ]

    # Filter by Airline
    airlines = sorted(df['ICAOEmpresaAérea'].unique())
    selected_airlines = st.sidebar.multiselect("Empresas Aéreas", airlines, default=airlines)
    
    if selected_airlines:
        df = df[df['ICAOEmpresaAérea'].isin(selected_airlines)]

    # --- Metrics Section ---
    st.header("Indicadores Principais (KPIs)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_flights = len(df)
    
    # Cancellations: Check for status other than REALIZADO or check missing Real times
    # Assuming "SituaçãoVoo" column exists and has "REALIZADO", "CANCELADO" etc.
    if 'SituaçãoVoo' in df.columns:
        cancelled = len(df[df['SituaçãoVoo'] != 'REALIZADO'])
        realized = len(df[df['SituaçãoVoo'] == 'REALIZADO'])
    else:
        cancelled = 0
        realized = total_flights

    # Calculate Delays (Departure Delay)
    # Delay = PartidaReal - PartidaPrevista
    df['AtrasoPartida'] = (df['PartidaReal'] - df['PartidaPrevista']).dt.total_seconds() / 60
    
    # Average delay (considering only positive delays for average delay metrics often, but let's take mean of all)
    avg_delay = df[df['AtrasoPartida'] > 0]['AtrasoPartida'].mean()
    
    with col1:
        st.metric("Total de Voos", f"{total_flights:,}")
    
    with col2:
        st.metric("Voos Realizados", f"{realized:,}")
        
    with col3:
        st.metric("Cancelamentos/Outros", f"{cancelled:,}", delta=f"{(cancelled/total_flights*100):.1f}%" if total_flights else "0%")
        
    with col4:
        st.metric("Atraso Médio (Partida)", f"{avg_delay:.1f} min" if not pd.isna(avg_delay) else "N/A")

    st.markdown("---")

    # --- Charts Section ---
    
    # 1. Flights Over Time
    st.subheader("Evolução de Voos por Dia")
    flights_per_day = df.groupby(df['PartidaPrevista'].dt.date).size().reset_index(name='Contagem')
    fig_line = px.line(flights_per_day, x='PartidaPrevista', y='Contagem', title='Voos Diários')
    st.plotly_chart(fig_line, use_container_width=True)
    
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        # 2. Airline Market Share
        st.subheader("Market Share (Empresas Aéreas)")
        airline_counts = df['ICAOEmpresaAérea'].value_counts().reset_index()
        airline_counts.columns = ['Empresa', 'Voos']
        fig_pie = px.pie(airline_counts, values='Voos', names='Empresa', title='Distribuição por Empresa Aérea')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with row1_col2:
        # 3. Flight Status Distribution
        st.subheader("Situação dos Voos")
        if 'SituaçãoVoo' in df.columns:
            status_counts = df['SituaçãoVoo'].value_counts().reset_index()
            status_counts.columns = ['Situação', 'Contagem']
            fig_bar_status = px.bar(status_counts, x='Situação', y='Contagem', title='Status dos Voos')
            st.plotly_chart(fig_bar_status, use_container_width=True)

    # 4. Top Destinations (for Departures from Selected Airport)
    st.subheader(f"Top Destinos (Partindo de {selected_airport})")
    
    departures = df[df['ICAOAeródromoOrigem'] == selected_airport]
    if not departures.empty:
        top_dest = departures['ICAOAeródromoDestino'].value_counts().head(10).reset_index()
        top_dest.columns = ['Destino', 'Voos']
        fig_bar_dest = px.bar(top_dest, x='Voos', y='Destino', orientation='h', title='Top 10 Destinos', color='Voos')
        fig_bar_dest.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_dest, use_container_width=True)
    else:
        st.info(f"Sem dados de partidas de {selected_airport} para exibir destinos.")

    # 5. Top Origins (for Arrivals to Selected Airport)
    st.subheader(f"Top Origens (Chegando em {selected_airport})")
    
    arrivals = df[df['ICAOAeródromoDestino'] == selected_airport]
    if not arrivals.empty:
        top_orig = arrivals['ICAOAeródromoOrigem'].value_counts().head(10).reset_index()
        top_orig.columns = ['Origem', 'Voos']
        fig_bar_orig = px.bar(top_orig, x='Voos', y='Origem', orientation='h', title='Top 10 Origens', color='Voos')
        fig_bar_orig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_orig, use_container_width=True)
    else:
        st.info(f"Sem dados de chegadas em {selected_airport} para exibir origens.")

    # Raw Data Expander
    with st.expander("Ver Dados Brutos"):
        st.dataframe(df)

if __name__ == "__main__":
    main()
