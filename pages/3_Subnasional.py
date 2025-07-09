import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.colors as pc
from random import choice

st.set_page_config(page_title="Deforestasi dan Emisi Karbon", layout="wide")
st.title("Deforestasi dan Emisi Karbon Subnasional")

# =====================================
# 🗕️ Load Data
# =====================================
tree_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Subnational 1 tree cover loss")
primary_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Subnational 1 primary loss")
carbon_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Subnational 1 carbon data")

# Tambahkan kolom gabungan: Country - Subnational
tree_loss_df['sub_display'] = tree_loss_df['country'] + " - " + tree_loss_df['subnational1']
primary_loss_df['sub_display'] = primary_loss_df['country'] + " - " + primary_loss_df['subnational1']
carbon_df['sub_display'] = carbon_df['country'] + " - " + carbon_df['subnational1']

# =====================================
# 📌 Sidebar Filter
# =====================================
st.sidebar.title("Filter")

sub_countries = sorted(tree_loss_df['country'].unique())
default_countries = ["Indonesia", "Brazil"]
selected_countries = st.sidebar.multiselect("Pilih Negara", sub_countries, default=default_countries)

# Ambil daftar sub_display yang sesuai negara
filtered_sub_df = tree_loss_df[tree_loss_df['country'].isin(selected_countries)]
subnational_display_list = sorted(filtered_sub_df['sub_display'].unique())
default_subs_display = [s for s in subnational_display_list if any(x in s for x in ["Aceh", "Bahia"])]
selected_sub_display = st.sidebar.multiselect("Pilih Subnasional", subnational_display_list, default=default_subs_display)

tahun_min, tahun_max = st.sidebar.slider("Rentang Tahun", 2001, 2024, (2001, 2024))
thresholds = sorted(tree_loss_df['threshold'].unique())
selected_threshold = st.sidebar.selectbox("Threshold (%)", thresholds)

st.sidebar.info("Threshold adalah ambang minimum persentase tajuk pohon yang dihitung sebagai hutan.")

# =====================================
# 📌 Data Preprocessing
# =====================================
years_cols = [col for col in tree_loss_df.columns if col.startswith('tc_loss_ha_')]
years = [int(col.split('_')[-1]) for col in years_cols]
year_range = [y for y in years if tahun_min <= y <= tahun_max]

prim_cols = [col for col in primary_loss_df.columns if col.startswith('tc_loss_ha_')]
prim_years = [int(col.split('_')[-1]) for col in prim_cols]
prim_range = [y for y in prim_years if tahun_min <= y <= tahun_max]

# Warna
warna_preset = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
extra_colors = pc.qualitative.Plotly + pc.qualitative.Set3 + pc.qualitative.Pastel
warna_negara = {}
used_colors = set(warna_preset)

for i, s in enumerate(selected_sub_display):
    if i < len(warna_preset):
        warna_negara[s] = warna_preset[i]
    else:
        unused_colors = [color for color in extra_colors if color not in used_colors]
        chosen_color = choice(unused_colors) if unused_colors else choice(extra_colors)
        warna_negara[s] = chosen_color
        used_colors.add(chosen_color)

# =====================================
# 📌 Total KPI Cards
# =====================================
total_tc_loss = 0
total_primary_loss = 0
total_emission = 0

for s in selected_sub_display:
    df_tc = tree_loss_df[(tree_loss_df['sub_display'] == s) & (tree_loss_df['threshold'] == selected_threshold)]
    if not df_tc.empty:
        total_tc_loss += df_tc.iloc[0][[f'tc_loss_ha_{y}' for y in year_range]].sum()

    df_primary = primary_loss_df[primary_loss_df['sub_display'] == s]
    if not df_primary.empty:
        total_primary_loss += df_primary.iloc[0][[f'tc_loss_ha_{y}' for y in prim_range]].sum()

    df_carbon = carbon_df[carbon_df['sub_display'] == s]
    if not df_carbon.empty:
        emission_cols = [f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
                         for y in prim_range if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in df_carbon.columns]
        total_emission += df_carbon.iloc[0][emission_cols].sum() if emission_cols else 0

col1, col2, col3 = st.columns(3)
col1.metric("Kehilangan Area Berpohon", f"{total_tc_loss:,.0f} ha")
col2.metric("Kehilangan Hutan Primer", f"{total_primary_loss:,.0f} ha")
col3.metric("Total Emisi CO₂e", f"{total_emission:,.0f} Mg")

st.markdown("---")

# =====================================
# 📌 Tren Kehilangan Area Berpohon
# =====================================
st.subheader(f"Tren Kehilangan Area Berpohon ({tahun_min}–{tahun_max})")
st.write(f"*Threshold: {selected_threshold}%*")

trend_data = []
insight_data = []

for s in selected_sub_display:
    df_tc = tree_loss_df[(tree_loss_df['sub_display'] == s) & (tree_loss_df['threshold'] == selected_threshold)]
    if not df_tc.empty:
        losses = df_tc.iloc[0][[f'tc_loss_ha_{y}' for y in year_range]].values
        trend_data.append(pd.DataFrame({'Tahun': [str(y) for y in year_range], 'Subnasional': s, 'Loss': losses}))
        insight_data.append(f"**{s}** kehilangan total {losses.sum():,.0f} ha pohon selama periode {tahun_min}–{tahun_max}.")

if trend_data:
    df_trend = pd.concat(trend_data)
    fig_tc = px.line(df_trend, x="Tahun", y="Loss", color="Subnasional", markers=True,
                     labels={'Loss': 'Kehilangan (ha)', 'Tahun': 'Tahun'},
                     color_discrete_map=warna_negara)
    fig_tc.update_layout(yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig_tc, use_container_width=True)
    st.info("\n\n".join(insight_data))
else:
    st.info("Data tidak tersedia.")

st.markdown("---")

# =====================================
# 📌 Pie dan Stacked Bar
# =====================================
st.markdown(f"### Perbandingan Kehilangan Hutan Primer dan Komposisi Kehilangan Area Berpohon ({tahun_min}–{tahun_max})")
col_pie, col_bar = st.columns(2)

with col_pie:
    pie_data = []
    for s in selected_sub_display:
        df_s = tree_loss_df[(tree_loss_df['sub_display'] == s) & (tree_loss_df['threshold'] == selected_threshold)]
        if not df_s.empty:
            total = df_s.iloc[0][[f'tc_loss_ha_{y}' for y in year_range]].sum()
            pie_data.append({'Subnasional': s, 'Loss': total})

    if pie_data:
        df_pie = pd.DataFrame(pie_data)
        fig_pie = px.pie(df_pie, names='Subnasional', values='Loss', hole=0.4,
                         color='Subnasional', color_discrete_map=warna_negara)
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(title_text=f"Komposisi Kehilangan Area Berpohon ({tahun_min}–{tahun_max})")
        st.plotly_chart(fig_pie, use_container_width=True)

with col_bar:
    bar_data = []
    for s in selected_sub_display:
        df_s = primary_loss_df[primary_loss_df['sub_display'] == s]
        if not df_s.empty:
            values = df_s.iloc[0][[f'tc_loss_ha_{y}' for y in prim_range]].values
            bar_data.append(pd.DataFrame({'Tahun': [str(y) for y in prim_range], 'Subnasional': s, 'Loss': values}))

    if bar_data:
        df_bar = pd.concat(bar_data)
        fig_bar = px.bar(df_bar, x="Tahun", y="Loss", color="Subnasional", barmode="stack",
                         labels={'Loss': 'Kehilangan (ha)'}, color_discrete_map=warna_negara)
        fig_bar.update_layout(title_text=f"Perbandingan Kehilangan Hutan Primer ({tahun_min}–{tahun_max})")
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# =====================================
# 📌 Emisi CO₂e Total dan Tren
# =====================================
st.markdown(f"### Emisi CO₂e Subnasional Terpilih ({tahun_min}–{tahun_max})")

emission_cols_selected = [f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
                          for y in range(tahun_min, tahun_max + 1)
                          if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in carbon_df.columns]

carbon_df['total_emission_selected'] = carbon_df[emission_cols_selected].sum(axis=1)

top_emission_selected = carbon_df[carbon_df['sub_display'].isin(selected_sub_display)]
fig_bar_total = px.bar(top_emission_selected, x='sub_display', y='total_emission_selected',
                       labels={'sub_display': 'Subnasional', 'total_emission_selected': 'Total Emisi (Mg CO₂e)'},
                       color='sub_display', color_discrete_map=warna_negara)
fig_bar_total.update_layout(yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig_bar_total, use_container_width=True)

st.markdown(f"### Tren Emisi CO₂e per Tahun")

trend_data = []
insight_data = []

for s in selected_sub_display:
    df_carbon_sub = carbon_df[carbon_df['sub_display'] == s]
    if not df_carbon_sub.empty:
        emission_cols = [f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
                         for y in prim_range if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in df_carbon_sub.columns]
        if emission_cols:
            emissions = df_carbon_sub.iloc[0][emission_cols].values
            years_emission = [int(col.split('_')[5]) for col in emission_cols]
            trend_data.append(pd.DataFrame({'Tahun': [str(y) for y in years_emission], 'Subnasional': s, 'Emisi': emissions}))

            max_idx = emissions.argmax()
            min_idx = emissions.argmin()
            insight_data.append(
                f"**{s}** — Tertinggi: {years_emission[max_idx]} ({emissions[max_idx]:,.0f} Mg), "
                f"Terendah: {years_emission[min_idx]} ({emissions[min_idx]:,.0f} Mg), "
                f"Rata-rata: {emissions.mean():,.0f} Mg")

if trend_data:
    df_emission = pd.concat(trend_data)
    fig_emission = px.line(df_emission, x="Tahun", y="Emisi", color="Subnasional", markers=True,
                           labels={'Emisi': 'Emisi (Mg CO₂e)', 'Tahun': 'Tahun'},
                           color_discrete_map=warna_negara)
    fig_emission.update_layout(yaxis=dict(rangemode="tozero"))
    st.plotly_chart(fig_emission, use_container_width=True)
    st.info("\n\n".join(insight_data))
else:
    st.info("Data emisi tidak tersedia.")
