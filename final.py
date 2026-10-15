import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Coffee Insight Premium", layout="wide", page_icon="☕")

# --- 2. CUSTOM CSS PREMIUM UI ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Kanit:wght@500;700&display=swap');
    .stApp {{ background-color: #1A1A1A; font-family: 'Inter', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: #121212; border-right: 1px solid #333; }}
    .main-header-container {{ border: 1px solid #333; border-radius: 25px; padding: 40px 50px; background-color: #161616; margin-bottom: 40px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }}
    .custom-kpi-card {{ background-color: #222222; border-radius: 18px; padding: 25px; border-bottom: 6px solid #D97706; display: flex; align-items: center; min-height: 120px; }}
    .kpi-icon-box {{ margin-right: 20px; display: flex; align-items: center; justify-content: center; }}
    .kpi-label {{ font-size: 13px; color: #AAAAAA; text-transform: uppercase; letter-spacing: 1px; }}
    .kpi-value {{ font-size: 24px; font-weight: 700; color: white; font-family: 'Kanit', sans-serif; }}
    div[data-testid="stSidebar"] button {{ background-color: #262626 !important; border: 1px solid #333 !important; border-radius: 12px !important; padding: 12px 20px !important; margin-bottom: 10px !important; color: #CCCCCC !important; width: 100% !important; }}
    div[data-testid="stSidebar"] button:hover {{ border-color: #D97706 !important; }}
    div[data-testid="stSidebar"] button[kind="primary"] {{ background-color: #D97706 !important; border-color: #D97706 !important; color: white !important; font-weight: 700 !important; }}
    h1, h2, h3 {{ font-family: 'Kanit', sans-serif !important; color: #FFFFFF !important; }}
    /* Styling khusus button download agar mencolok */
    .stDownloadButton button {{
        background-color: #D97706 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }}
    </style>
    """, unsafe_allow_html=True)

ACCENT_ORANGE = "#D97706"
SOFT_BROWN = "#967259"
COFFEE_PALETTE = ["#3D2B1F", "#634832", "#89674C", "#D4A373", "#E9EDC9", "#A68A64", "#582F0E"]

# --- 3. LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('Coffe_sales dataset.csv') 
        df['Date'] = pd.to_datetime(df['Date'])
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        df['Month_name'] = pd.Categorical(df['Month_name'], categories=month_order, ordered=True)
        day_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        df['Weekday'] = pd.Categorical(df['Weekday'], categories=day_order, ordered=True)
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- 4. SIDEBAR ---
    with st.sidebar:
        st.markdown('<div style="text-align:center; padding-bottom:20px;"><img src="https://cdn-icons-png.flaticon.com/512/924/924514.png" width="100"></div>', unsafe_allow_html=True)
        
        # Filter Produk
        selected_coffee = st.selectbox("Pilih Produk", options=["Semua"] + list(df['coffee_name'].unique()))
        filtered_df = df if selected_coffee == "Semua" else df[df['coffee_name'] == selected_coffee]

        if 'menu_aktif' not in st.session_state: st.session_state.menu_aktif = "Dashboard Overview"
        
        st.markdown("---")
        # Navigasi Menu
        for m in ["Dashboard Overview", "Tren Bulanan", "Produk Terlaris"]:
            if st.button(m, use_container_width=True, type="primary" if st.session_state.menu_aktif == m else "secondary"):
                st.session_state.menu_aktif = m
                st.rerun()

        st.markdown("---")
        # FITUR DOWNLOAD DATA (Taruh di Sidebar)
        st.markdown("### 📥 Export Data")
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Filtered Data (.CSV)",
            data=csv,
            file_name=f'coffee_sales_{selected_coffee.lower().replace(" ", "_")}.csv',
            mime='text/csv',
            use_container_width=True
        )

    # --- 5. HEADER & KPI ---
    st.markdown('<div class="main-header-container">', unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 40px; margin-bottom: 40px;'>{st.session_state.menu_aktif}</h1>", unsafe_allow_html=True)
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    def draw_kpi(col, label, value, icon_url):
        with col:
            st.markdown(f'<div class="custom-kpi-card"><div class="kpi-icon-box"><img src="{icon_url}" width="45"></div><div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div></div>', unsafe_allow_html=True)

    draw_kpi(col_kpi1, "Pendapatan", f"${filtered_df['money'].sum():,.2f}", "https://cdn-icons-png.flaticon.com/512/924/924514.png")
    draw_kpi(col_kpi2, "Cups Terjual", f"{len(filtered_df)} Cup", "https://cdn-icons-png.flaticon.com/512/3127/3127450.png")
    draw_kpi(col_kpi3, "Rata-rata", f"${filtered_df['money'].mean():.2f}", "https://cdn-icons-png.flaticon.com/512/2489/2489756.png")
    draw_kpi(col_kpi4, "Payment", filtered_df['cash_type'].mode()[0].title() if not filtered_df.empty else "N/A", "https://cdn-icons-png.flaticon.com/512/3361/3361413.png")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- 6. AREA VISUALISASI ---
    selected = st.session_state.menu_aktif

    if selected == "Tren Bulanan":
        with st.container(border=True):
            st.subheader("Pertumbuhan Pendapatan Bulanan dan Analisis Trend Penjualan")
            stats = filtered_df.groupby('Month_name', observed=True)['money'].sum().reset_index()
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=stats['Month_name'], y=stats['money'], marker_color=SOFT_BROWN, text=stats['money'].round(0), textposition='inside', insidetextanchor='middle', name="Revenue"))
            fig1.add_trace(go.Scatter(x=stats['Month_name'], y=stats['money'], line=dict(color=ACCENT_ORANGE, width=4, shape='spline'), mode='lines+markers', name="Trend"))
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=500, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

    elif selected == "Produk Terlaris":
        with st.container(border=True):
            st.subheader("Produk dengan Performa Penjualan Tertinggi")
            best = filtered_df['coffee_name'].value_counts().reset_index().head(10)
            best.columns = ['coffee_name', 'count']
            fig2 = px.bar(best, x='count', y='coffee_name', orientation='h', color='count', color_continuous_scale=['#4E342E', ACCENT_ORANGE])
            fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), coloraxis_showscale=False, height=600)
            st.plotly_chart(fig2, use_container_width=True)

    else:
        # --- DASHBOARD OVERVIEW ---
        with st.container(border=True):
            st.subheader("Pertumbuhan Pendapatan Bulanan dan Analisis Trend Penjualan")
            stats = filtered_df.groupby('Month_name', observed=True)['money'].sum().reset_index()
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=stats['Month_name'], y=stats['money'], marker_color=SOFT_BROWN, text=stats['money'].round(0), textposition='inside', insidetextanchor='middle', name="Revenue"))
            fig1.add_trace(go.Scatter(x=stats['Month_name'], y=stats['money'], line=dict(color=ACCENT_ORANGE, width=4, shape='spline'), mode='lines+markers', name="Trend"))
            fig1.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=400, margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                st.subheader("Analisis Preferensi Produk Berdasarkan Segmen Waktu")
                time_coffee = filtered_df.groupby(['Time_of_Day', 'coffee_name']).size().reset_index(name='Jumlah')
                
                # Bagian Latte=Putih, sisanya COFFEE_PALETTE lu
                fig5 = px.bar(time_coffee, x='Time_of_Day', y='Jumlah', color='coffee_name', 
                             color_discrete_map={"Latte": "#FFFFFF"},
                             color_discrete_sequence=COFFEE_PALETTE)
                
                fig5.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)', 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    font=dict(color="#FFFFFF"), 
                    xaxis=dict(showgrid=False, title="Waktu"), 
                    yaxis=dict(showgrid=True, gridcolor='#333333', title="Jumlah Gelas"),
                    legend=dict(title=None, font=dict(size=10))
                )
                st.plotly_chart(fig5, use_container_width=True)

        with col4:
            with st.container(border=True):
                st.subheader("Variansi Pendapatan Harian dan Performa Mingguan")
                day_perf = filtered_df.groupby('Weekday', observed=True)['money'].sum().reset_index()
                fig9 = px.line(day_perf, x='Weekday', y='money', markers=True, color_discrete_sequence=[ACCENT_ORANGE])
                fig9.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="#FFFFFF"), xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#333333'))
                st.plotly_chart(fig9, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            with st.container(border=True):
                st.subheader("Produk dengan Performa Penjualan Tertinggi")
                best = filtered_df['coffee_name'].value_counts().reset_index().head(8)
                best.columns = ['coffee_name', 'count']
                fig2 = px.bar(best, x='count', y='coffee_name', orientation='h', color='count', color_continuous_scale=['#4E342E', ACCENT_ORANGE])
                fig2.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), coloraxis_showscale=False, height=350)
                st.plotly_chart(fig2, use_container_width=True)
        with c2:
            with st.container(border=True):
                st.subheader("Distribusi Arus Kunjungan dan Jam Sibuk")
                busy = filtered_df.groupby('hour_of_day').size().reset_index(name='Kunjungan')
                fig3 = px.area(busy, x='hour_of_day', y='Kunjungan', color_discrete_sequence=[ACCENT_ORANGE])
                fig3.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=350)
                st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.expander("📑 View Data Details"):
        st.dataframe(filtered_df.head(50), use_container_width=True)
else:
    st.error("Data tidak ditemukan.")