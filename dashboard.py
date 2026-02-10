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

# ICAO to Airport Name mapping
AIRPORT_NAMES = {
    "SBFZ": "Fortaleza (Pinto Martins)",
    "SBRF": "Recife (Guararapes)",
    "SBBR": "Brasília (Juscelino Kubitschek)",
    "SBGR": "São Paulo (Guarulhos)",
    "SBSP": "São Paulo (Congonhas)",
    "SBKP": "Campinas (Viracopos)",
    "SBRJ": "Rio de Janeiro (Santos Dumont)",
    "SBGL": "Rio de Janeiro (Galeão)",
    "SBCT": "Curitiba (Afonso Pena)",
    "SBPA": "Porto Alegre (Salgado Filho)",
    "SBCF": "Belo Horizonte (Confins)",
    "SBBH": "Belo Horizonte (Pampulha)",
    "SBEG": "Manaus (Eduardo Gomes)",
    "SBTE": "Teresina (Terceira)",
    "SBPV": "Porto Velho (Gov. Jorge Teixeira)",
    "SBNT": "Natal (Augusto Severo)",
    "SBMO": "Maceió (Zumbi dos Palmares)",
    "SBAR": "Aracaju (Santa Maria)",
    "SBCY": "Cuiabá (Marechal Rondon)",
    "SBCC": "Cascavel (Adalberto Mendes)",
    "SBFI": "Foz do Iguaçu (Cataratas)",
    "SBLO": "Londrina (Gov. José Richa)",
    "SBUL": "Uberlândia (Cesar Vinagri)",
    "SBCG": "Campo Grande (G. Mendes)",
    "SBMS": "Maringá (Sílvio Name Jr.)",
    "SBCZ": "Cascavel (Adalberto Mendes)",
    "SBNT": "Natal (Augusto Severo)",
    "SBFS": "Foz do Iguaçu (Cataratas)",
    "SBVT": "Vitória (Eurico Salles)",
    "SBJP": "João Pessoa (Castro Pinto)",
    "SBMC": "Macapá (Alberto Alcolumbre)",
    "SBIZ": "Ilhéus (Jorge Amado)",
    "SBPK": "Palmas (Brig. Lysias)",
    "SBCN": "Cascavel (Adalberto Mendes)",
    "SBFL": "Florianópolis (Hercílio Luz)",
    "SBNF": "Navegantes (Min. Victor Konder)",
    "SBPJ": "Palmas (Brig. Lysias)",
    "SBSV": "Salvador (Deputado Luís Magalhães)",
    "SBUR": "Uruguaiana (Rubem Berta)",
    "SBUG": "Bagé (Gustavo Kramer)",
    "SBBV": "Boa Vista (Atlas Brasil)",
    "SBFN": "Parnamirim (Gov. Dix-Sept Rosado)",
    "SBCR": "Carajás (Carajás)",
    "SBMN": "Manaus (Ponta Pelada)",
    "SBHT": "Altamira (Altamira)",
    "SBPL": "Ponta Pelada",
    "SBSL": "São Luís (Marechal Cunha Machado)",
    "SBMK": "Macaé (Macaé)",
    "SBCV": "Caravelas (Caravelas)",
    "SBTL": "Tefé (Tefé)",
    "SBCH": "Chapecó (Chapecó)",
    "SBJV": "Joinville (Joinville)",
    "SBCX": "Caxias do Sul (Caxias)",
    "SBDU": "Dourados (Dourados)",
    "SBCM": "São Carlos (São Carlos)",
    "SBRB": "Rio Branco (Rio Branco)",
    "SBCA": "Cabo Frio (Cabo Frio)",
    "SBCI": "São José dos Campos (Prof. Urbano Ernesto Stumpf)",
    "SBYS": "São José dos Campos (Três Rios)",
    "SBAS": "Iguape (Iguape)",
    "SBAU": "Araçatuba (Araçatuba)",
    "SBAQ": "Araraquara (Araraquara)",
    "SBAX": "Araçatuba (Araçatuba)",
    "SBJD": "Jundiaí (Jundiaí)",
    "SBSR": "Santarém (Maestro Wilson Fonseca)",
    "SBKG": "Bragança (Bragança)",
    "SBCO": "Comandante Rolim Adolpho Amaro",
    "SBST": "São Paulo (São Paulo)",
    "SBCR": "Corumbá (Corumbá)",
    "SBWG": "Tefé (Tefé)",
    "SBIL": "Ilet (Ilet)",
    "SBTL": "Tefé (Tefé)",
    "SBUC": "Uberaba (Uberaba)",
    "SBYS": "São José dos Campos (Três Rios)",
    "SBVH": "Vilhena (Vilhena)",
    "SBOV": "Ourinhos (Ourinhos)",
    "SBBM": "Bom Jesus da Lapa (Bom Jesus da Lapa)",
    "SBJU": "Juazeiro do Norte (Juazeiro do Norte)",
    "SBPF": "Parnaíba (Parnaíba)",
    "SBKN": "Kleber (Kleber)",
    "SBIU": "Ivaiporã (Ivaiporã)",
    "SBCG": "Campo Grande (Campo Grande)",
    "SBDV": "Divinópolis (Divinópolis)",
    "SBPO": "Patos de Minas (Patos de Minas)",
    "SBCD": "Caldas Novas (Caldas Novas)",
    "SBUG": "Bauru (Bauru)",
    "SBAU": "Araçatuba (Araçatuba)",
    "SBCP": "Campinas (Campinas)",
    "SBRP": "Ribeirão Preto (Ribeirão Preto)",
    "SBPP": "Bauru (Arealva)",
    "SBCJ": "São João del-Rei (São João del-Rei)",
    "SBCZ": "Cascavel (Cascavel)",
    "SBFI": "Foz do Iguaçu (Foz do Iguaçu)",
    "SBLO": "Londrina (Londrina)",
    "SBUF": "Franca (Franca)",
    "SBMS": "Maringá (Maringá)",
    "SBDU": "Dourados (Dourados)",
    "SBCV": "Crv (Crv)",
    "SBCG": "Campo Grande (Campo Grande)",
    "SBKP": "Viracopos (Viracopos)",
    "SBMT": "Marte (Marte)",
    "SBNT": "Natal (Natal)",
    "SBPV": "Porto Velho (Porto Velho)",
    "SBRB": "Rio Branco (Rio Branco)",
    "SBRF": "Recife (Recife)",
    "SBSV": "Salvador (Salvador)",
    "SBTE": "Teresina (Teresina)",
    "SBUL": "Uberlândia (Uberlândia)",
    "SBVT": "Vitória (Vitória)",
    "SBJP": "João Pessoa (João Pessoa)",
    "SBMO": "Maceió (Maceió)",
    "SBAR": "Aracaju (Aracaju)",
    "SBMC": "Macapá (Macapá)",
    "SBMK": "Macaé (Macaé)",
    "SBNF": "Navegantes (Navegantes)",
    "SBFL": "Florianópolis (Florianópolis)",
    "SBCX": "Caxias do Sul (Caxias do Sul)",
    "SBCI": "São José dos Campos (São José dos Campos)",
    "SBJV": "Joinville (Joinville)",
    "SBCH": "Chapecó (Chapecó)",
    "SBDU": "Dourados (Dourados)",
    "SBUR": "Uruguaiana (Uruguaiana)",
    "SBUG": "Bagé (Bagé)",
    "SBBV": "Boa Vista (Boa Vista)",
    "SBRB": "Rio Branco (Rio Branco)",
    "SBPJ": "Palmas (Palmas)",
    "SBPK": "Palmas (Palmas)",
    "SBSL": "São Luís (São Luís)",
    "SBFN": "Parnamirim (Parnamirim)",
    "SBRJ": "Rio de Janeiro (Santos Dumont)",
    "SBGL": "Rio de Janeiro (Galeão)",
    "SBVT": "Vitória (Vitória)",
    "SBCF": "Belo Horizonte (Confins)",
    "SBBH": "Belo Horizonte (Pampulha)",
    "SBCG": "Campo Grande (Campo Grande)",
    "SBCY": "Cuiabá (Cuiabá)",
    "SBEG": "Manaus (Eduardo Gomes)",
    "SBRF": "Recife (Guararapes)",
    "SBSV": "Salvador (Dep. Luís Eduardo)",
    "SBGO": "Goiânia (Goiânia)",
    "SBCT": "Curitiba (Afonso Pena)",
    "SBPA": "Porto Alegre (Salgado Filho)",
    "SBKP": "Campinas (Viracopos)",
    "SBSP": "São Paulo (Congonhas)",
    "SBGR": "São Paulo (Guarulhos)",
    "SBBR": "Brasília (Juscelino Kubitschek)",
    "SBFZ": "Fortaleza (Pinto Martins)",
}

def get_airport_name(icao_code):
    """Returns the airport name for a given ICAO code."""
    return AIRPORT_NAMES.get(icao_code, icao_code)

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

    # Local helper function for airport names (defined inside to avoid caching issues)
    def get_airport_name_local(icao_code):
        return AIRPORT_NAMES.get(icao_code, icao_code)

    # Derive additional columns for analysis
    # Route column (with full airport names) - use map() instead of apply() for better performance
    origin_names = df['ICAOAeródromoOrigem'].map(get_airport_name_local)
    dest_names = df['ICAOAeródromoDestino'].map(get_airport_name_local)
    df['Rota'] = origin_names + ' → ' + dest_names

    # Temporal columns from PartidaPrevista
    df['DiaSemana'] = df['PartidaPrevista'].dt.day_name()
    df['DiaSemanaNum'] = df['PartidaPrevista'].dt.dayofweek  # 0=Monday, 6=Sunday
    df['Mes'] = df['PartidaPrevista'].dt.month_name()
    df['MesNum'] = df['PartidaPrevista'].dt.month
    df['Hora'] = df['PartidaPrevista'].dt.hour
    df['Data'] = df['PartidaPrevista'].dt.date

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

    # Filter by Airport (Default SBFZ) - show full names
    airports_icao = sorted(list(set(df_raw['ICAOAeródromoOrigem'].unique()) | set(df_raw['ICAOAeródromoDestino'].unique())))
    airports_display = {icao: get_airport_name(icao) for icao in airports_icao}
    airports_sorted = sorted(airports_display.items(), key=lambda x: x[1])

    if TARGET_AIRPORT in airports_icao:
        default_index = [i for i, (icao, _) in enumerate(airports_sorted) if icao == TARGET_AIRPORT][0]
    else:
        default_index = 0

    selected_index = st.sidebar.selectbox(
        "Selecione o Aeroporto",
        range(len(airports_sorted)),
        format_func=lambda i: f"{airports_sorted[i][1]} ({airports_sorted[i][0]})",
        index=default_index
    )
    selected_airport = airports_sorted[selected_index][0]

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

    total_flights = len(df)

    # Cancellations: Check for status other than REALIZADO or check missing Real times
    # Assuming "SituaçãoVoo" column exists and has "REALIZADO", "CANCELADO" etc.
    if 'SituaçãoVoo' in df.columns:
        cancelled = len(df[df['SituaçãoVoo'] != 'REALIZADO'])
        realized = len(df[df['SituaçãoVoo'] == 'REALIZADO'])
    else:
        cancelled = 0
        realized = total_flights

    # Calculate Delays
    df['AtrasoPartida'] = (df['PartidaReal'] - df['PartidaPrevista']).dt.total_seconds() / 60
    df['AtrasoChegada'] = (df['ChegadaReal'] - df['ChegadaPrevista']).dt.total_seconds() / 60

    # Average delays
    avg_departure_delay = df[df['AtrasoPartida'] > 0]['AtrasoPartida'].mean()
    avg_arrival_delay = df[df['AtrasoChegada'] > 0]['AtrasoChegada'].mean()

    # Flights with significant delays (> 15 minutes)
    significant_delays = len(df[df['AtrasoPartida'] > 15])
    pct_significant_delays = (significant_delays / total_flights * 100) if total_flights else 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total de Voos", f"{total_flights:,}")

    with col2:
        st.metric("Voos Realizados", f"{realized:,}")

    with col3:
        st.metric("Cancelamentos/Outros", f"{cancelled:,}", delta=f"{(cancelled/total_flights*100):.1f}%" if total_flights else "0%")

    with col4:
        st.metric("Atraso Médio Partida", f"{avg_departure_delay:.1f} min" if not pd.isna(avg_departure_delay) else "N/A")

    with col5:
        st.metric("Atraso Médio Chegada", f"{avg_arrival_delay:.1f} min" if not pd.isna(avg_arrival_delay) else "N/A")

    with col6:
        st.metric("Atrasos > 15min", f"{pct_significant_delays:.1f}%")

    st.markdown("---")

    # --- Tabbed Interface ---
    tab1, tab2, tab3, tab4 = st.tabs(["Visão Geral", "Análise de Atrasos", "Padrões Temporais", "Rotas"])

    # =============================================================================
    # TAB 1: Visão Geral (existing visualizations)
    # =============================================================================
    with tab1:
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
        st.subheader(f"Top Destinos (Partindo de {get_airport_name(selected_airport)})")

        departures = df[df['ICAOAeródromoOrigem'] == selected_airport]
        if not departures.empty:
            top_dest = departures['ICAOAeródromoDestino'].value_counts().head(10).reset_index()
            top_dest.columns = ['Destino', 'Voos']
            top_dest['Destino_Nome'] = top_dest['Destino'].apply(get_airport_name)
            fig_bar_dest = px.bar(
                top_dest,
                x='Voos',
                y='Destino_Nome',
                orientation='h',
                title='Top 10 Destinos',
                color='Voos'
            )
            fig_bar_dest.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar_dest, use_container_width=True)
        else:
            st.info(f"Sem dados de partidas de {get_airport_name(selected_airport)} para exibir destinos.")

        # 5. Top Origins (for Arrivals to Selected Airport)
        st.subheader(f"Top Origens (Chegando em {get_airport_name(selected_airport)})")

        arrivals = df[df['ICAOAeródromoDestino'] == selected_airport]
        if not arrivals.empty:
            top_orig = arrivals['ICAOAeródromoOrigem'].value_counts().head(10).reset_index()
            top_orig.columns = ['Origem', 'Voos']
            top_orig['Origem_Nome'] = top_orig['Origem'].apply(get_airport_name)
            fig_bar_orig = px.bar(
                top_orig,
                x='Voos',
                y='Origem_Nome',
                orientation='h',
                title='Top 10 Origens',
                color='Voos'
            )
            fig_bar_orig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar_orig, use_container_width=True)
        else:
            st.info(f"Sem dados de chegadas em {get_airport_name(selected_airport)} para exibir origens.")

    # =============================================================================
    # TAB 2: Análise de Atrasos
    # =============================================================================
    with tab2:
        st.header("Análise de Atrasos")

        # Distribution of delays (histogram)
        st.subheader("Distribuição de Atrasos (Partida)")
        delay_data = df[df['AtrasoPartida'].notna()]
        if not delay_data.empty:
            fig_hist = px.histogram(
                delay_data,
                x='AtrasoPartida',
                nbins=50,
                title='Histograma de Atrasos de Partida (minutos)',
                labels={'AtrasoPartida': 'Atraso (minutos)'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.add_vline(x=0, line_dash="dash", line_color="red", annotation_text="Pontual")
            fig_hist.add_vline(x=15, line_dash="dash", line_color="orange", annotation_text="15min")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Sem dados de atrasos para exibir.")

        # Delays by airline (box plot)
        st.subheader("Atrasos por Empresa Aérea")
        col2a, col2b = st.columns(2)

        with col2a:
            st.write("**Atraso de Partida por Empresa**")
            if not delay_data.empty:
                fig_box_partida = px.box(
                    delay_data,
                    x='ICAOEmpresaAérea',
                    y='AtrasoPartida',
                    title='Box Plot: Atraso de Partida por Empresa',
                    labels={'ICAOEmpresaAérea': 'Empresa', 'AtrasoPartida': 'Atraso (min)'}
                )
                fig_box_partida.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_box_partida, use_container_width=True)

        with col2b:
            st.write("**Atraso de Chegada por Empresa**")
            arrival_delay_data = df[df['AtrasoChegada'].notna()]
            if not arrival_delay_data.empty:
                fig_box_chegada = px.box(
                    arrival_delay_data,
                    x='ICAOEmpresaAérea',
                    y='AtrasoChegada',
                    title='Box Plot: Atraso de Chegada por Empresa',
                    labels={'ICAOEmpresaAérea': 'Empresa', 'AtrasoChegada': 'Atraso (min)'}
                )
                fig_box_chegada.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_box_chegada, use_container_width=True)

        # Delays by hour
        st.subheader("Atrasos por Hora do Dia")
        delays_by_hour = df.groupby('Hora')['AtrasoPartida'].agg(['mean', 'median', 'count']).reset_index()
        delays_by_hour = delays_by_hour[delays_by_hour['count'] > 0]
        if not delays_by_hour.empty:
            fig_hour = px.bar(
                delays_by_hour,
                x='Hora',
                y='mean',
                title='Atraso Médio por Hora do Dia',
                labels={'Hora': 'Hora', 'mean': 'Atraso Médio (min)'},
                color='mean',
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_hour, use_container_width=True)

        # Heatmap: Day of Week x Hour
        st.subheader("Heatmap: Atrasos por Dia da Semana x Hora")
        heatmap_data = df.groupby(['DiaSemanaNum', 'Hora'])['AtrasoPartida'].mean().reset_index()
        if not heatmap_data.empty:
            # Order days correctly
            day_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            day_map = {0: 'Segunda', 1: 'Terça', 2: 'Quarta', 3: 'Quinta', 4: 'Sexta', 5: 'Sábado', 6: 'Domingo'}
            heatmap_data['DiaNome'] = heatmap_data['DiaSemanaNum'].map(day_map)

            fig_heat = px.density_heatmap(
                heatmap_data,
                x='Hora',
                y='DiaNome',
                z='AtrasoPartida',
                title='Atraso Médio (min) por Dia e Hora',
                labels={'Hora': 'Hora', 'DiaNome': 'Dia da Semana', 'AtrasoPartida': 'Atraso Médio (min)'},
                category_orders={'DiaNome': day_order},
                color_continuous_scale='RdYlGn_r'
            )
            st.plotly_chart(fig_heat, use_container_width=True)

    # =============================================================================
    # TAB 3: Padrões Temporais
    # =============================================================================
    with tab3:
        st.header("Padrões Temporais")

        # Flights by day of week
        st.subheader("Voos por Dia da Semana")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_pt_map = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        flights_by_day = df['DiaSemana'].value_counts().reindex(day_order).fillna(0).reset_index()
        flights_by_day.columns = ['Dia', 'Voos']
        flights_by_day['Dia_PT'] = flights_by_day['Dia'].map(day_pt_map)

        fig_day = px.bar(
            flights_by_day,
            x='Dia_PT',
            y='Voos',
            title='Distribuição de Voos por Dia da Semana',
            labels={'Dia_PT': 'Dia da Semana', 'Voos': 'Número de Voos'},
            color='Voos'
        )
        st.plotly_chart(fig_day, use_container_width=True)

        # Flights by month
        st.subheader("Voos por Mês")
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_pt_map = {
            'January': 'Jan', 'February': 'Fev', 'March': 'Mar', 'April': 'Abr',
            'May': 'Mai', 'June': 'Jun', 'July': 'Jul', 'August': 'Ago',
            'September': 'Set', 'October': 'Out', 'November': 'Nov', 'December': 'Dez'
        }
        flights_by_month = df['Mes'].value_counts().reindex(month_order).fillna(0).reset_index()
        flights_by_month.columns = ['Mes', 'Voos']
        flights_by_month['Mes_PT'] = flights_by_month['Mes'].map(month_pt_map)

        fig_month = px.bar(
            flights_by_month,
            x='Mes_PT',
            y='Voos',
            title='Distribuição de Voos por Mês',
            labels={'Mes_PT': 'Mês', 'Voos': 'Número de Voos'},
            color='Voos'
        )
        st.plotly_chart(fig_month, use_container_width=True)

        # Peak hours
        st.subheader("Horários de Pico")
        flights_by_hour = df['Hora'].value_counts().sort_index().reset_index()
        flights_by_hour.columns = ['Hora', 'Voos']

        fig_hour_vol = px.bar(
            flights_by_hour,
            x='Hora',
            y='Voos',
            title='Volume de Voos por Hora do Dia',
            labels={'Hora': 'Hora', 'Voos': 'Número de Voos'},
            color='Voos',
            color_continuous_scale='Blues'
        )
        fig_hour_vol.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
        st.plotly_chart(fig_hour_vol, use_container_width=True)

        # Weekday vs Weekend comparison
        st.subheader("Comparação: Dia de Semana vs Fim de Semana")
        df['TipoDia'] = df['DiaSemanaNum'].apply(lambda x: 'Fim de Semana' if x >= 5 else 'Dia de Semana')

        comparison = df.groupby('TipoDia').agg({
            'AtrasoPartida': 'mean',
            'Rota': 'count'
        }).reset_index()
        comparison.columns = ['TipoDia', 'AtrasoMedio', 'TotalVoos']
        comparison['AtrasoMedio'] = comparison['AtrasoMedio'].fillna(0)

        col3a, col3b = st.columns(2)

        with col3a:
            fig_comp_vol = px.bar(
                comparison,
                x='TipoDia',
                y='TotalVoos',
                title='Volume de Voos',
                labels={'TipoDia': 'Tipo de Dia', 'TotalVoos': 'Total de Voos'},
                color='TipoDia'
            )
            st.plotly_chart(fig_comp_vol, use_container_width=True)

        with col3b:
            fig_comp_delay = px.bar(
                comparison,
                x='TipoDia',
                y='AtrasoMedio',
                title='Atraso Médio',
                labels={'TipoDia': 'Tipo de Dia', 'AtrasoMedio': 'Atraso Médio (min)'},
                color='TipoDia'
            )
            st.plotly_chart(fig_comp_delay, use_container_width=True)

    # =============================================================================
    # TAB 4: Rotas
    # =============================================================================
    with tab4:
        st.header("Análise de Rotas")

        # Top routes by volume
        st.subheader("Top Rotas por Volume")
        route_counts = df['Rota'].value_counts().head(20).reset_index()
        route_counts.columns = ['Rota', 'Voos']

        fig_routes_vol = px.bar(
            route_counts,
            x='Voos',
            y='Rota',
            orientation='h',
            title='Top 20 Rotas por Número de Voos',
            labels={'Rota': 'Rota', 'Voos': 'Número de Voos'},
            color='Voos'
        )
        fig_routes_vol.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_routes_vol, use_container_width=True)

        # Routes with highest average delay
        st.subheader("Rotas com Maior Atraso Médio")
        route_delays = df.groupby('Rota')['AtrasoPartida'].agg(['mean', 'count']).reset_index()
        route_delays = route_delays[route_delays['count'] >= 5]  # Minimum 5 flights
        route_delays = route_delays.sort_values('mean', ascending=False).head(15)
        route_delays.columns = ['Rota', 'AtrasoMedio', 'Voos']

        fig_routes_delay = px.bar(
            route_delays,
            x='AtrasoMedio',
            y='Rota',
            orientation='h',
            title='Top 15 Rotas por Atraso Médio (mín. 5 voos)',
            labels={'Rota': 'Rota', 'AtrasoMedio': 'Atraso Médio (min)'},
            color='AtrasoMedio',
            color_continuous_scale='Reds'
        )
        fig_routes_delay.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_routes_delay, use_container_width=True)

        # Detailed route statistics table
        st.subheader("Tabela Detalhada de Rotas")

        route_stats = df.groupby('Rota').agg({
            'Rota': 'count',
            'AtrasoPartida': ['mean', 'std'],
            'AtrasoChegada': 'mean'
        }).reset_index()

        route_stats.columns = ['Rota', 'TotalVoos', 'AtrasoPartida_Medio', 'AtrasoPartida_Std', 'AtrasoChegada_Medio']

        # Calculate cancellation rate if status available
        if 'SituaçãoVoo' in df.columns:
            cancelled_by_route = df[df['SituaçãoVoo'] != 'REALIZADO'].groupby('Rota').size()
            route_stats['TaxaCancelamento'] = route_stats['Rota'].map(cancelled_by_route).fillna(0)
            route_stats['TaxaCancelamento_Pct'] = (route_stats['TaxaCancelamento'] / route_stats['TotalVoos'] * 100).round(1)
            display_cols = ['Rota', 'TotalVoos', 'AtrasoPartida_Medio', 'AtrasoChegada_Medio', 'TaxaCancelamento_Pct']
            display_col_names = ['Rota', 'Total Voos', 'Atraso Partida (médio)', 'Atraso Chegada (médio)', 'Cancelamentos (%)']
        else:
            display_cols = ['Rota', 'TotalVoos', 'AtrasoPartida_Medio', 'AtrasoChegada_Medio']
            display_col_names = ['Rota', 'Total Voos', 'Atraso Partida (médio)', 'Atraso Chegada (médio)']

        route_stats_display = route_stats[display_cols].copy()
        route_stats_display.columns = display_col_names
        route_stats_display['Atraso Partida (médio)'] = route_stats_display['Atraso Partida (médio)'].round(1)
        route_stats_display['Atraso Chegada (médio)'] = route_stats_display['Atraso Chegada (médio)'].round(1)

        # Sort by total flights and show top routes
        route_stats_display = route_stats_display.sort_values('Total Voos', ascending=False).head(50)
        st.dataframe(route_stats_display, use_container_width=True)

    # =============================================================================
    # Raw Data Expander (at the end, outside tabs)
    # =============================================================================
    st.markdown("---")
    with st.expander("Ver Dados Brutos"):
        st.dataframe(df)

if __name__ == "__main__":
    main()
