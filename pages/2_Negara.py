import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from random import choice
import plotly.colors as pc

st.set_page_config(page_title="Deforestasi dan Emisi Karbon", layout="wide")
st.title("Deforestasi dan Emisi Karbon Negara")

# =====================================
# 🗕️ Load Data
# =====================================
tree_cover_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country tree cover loss")
primary_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country primary loss")
carbon_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country carbon data")

# =====================================
# 📌 Sidebar Filter
# =====================================
st.sidebar.title("Filter")

country_list = sorted(tree_cover_loss_df['country'].unique())
default_countries = ["Indonesia", "Brazil"]
default_selected = [c for c in default_countries if c in country_list]
selected_countries = st.sidebar.multiselect(
    "Pilih Negara",
    country_list,
    default=default_selected,
    help="Pilih satu atau lebih negara untuk dibandingkan"
)

tahun_min, tahun_max = st.sidebar.slider("Rentang Tahun", 2001, 2024, (2001, 2024))
thresholds = sorted(tree_cover_loss_df['threshold'].unique())
selected_threshold = st.sidebar.selectbox("Threshold (%)", thresholds)

st.sidebar.info(
    "Threshold adalah ambang minimum persentase tajuk pohon yang dihitung sebagai hutan."
)

# =====================================
# 📌 Data Preprocessing
# =====================================
years_cols = [col for col in tree_cover_loss_df.columns if col.startswith('tc_loss_ha_')]
years = [int(col.split('_')[-1]) for col in years_cols]
mask_years = [y for y in years if tahun_min <= y <= tahun_max]

years_cols_p = [col for col in primary_loss_df.columns if col.startswith('tc_loss_ha_')]
years_p = [int(col.split('_')[-1]) for col in years_cols_p]
mask_p = [y for y in years_p if tahun_min <= y <= tahun_max]

# =====================================
# 📌 Warna Negara
# =====================================
warna_preset = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
extra_colors = pc.qualitative.Plotly + pc.qualitative.Set3 + pc.qualitative.Pastel
warna_negara = {}
used_colors = set(warna_preset)

for i, c in enumerate(selected_countries):
    if i < len(warna_preset):
        warna_negara[c] = warna_preset[i]
    else:
        unused_colors = [color for color in extra_colors if color not in used_colors]
        chosen_color = choice(unused_colors) if unused_colors else choice(extra_colors)
        warna_negara[c] = chosen_color
        used_colors.add(chosen_color)

# =====================================
# 📌 Total KPI Cards
# =====================================
total_tc_loss = 0
total_primary_loss = 0
total_emission = 0

for c in selected_countries:
    df_tc = tree_cover_loss_df[
        (tree_cover_loss_df['country'] == c) &
        (tree_cover_loss_df['threshold'] == selected_threshold)
    ]
    if not df_tc.empty:
        total_tc_loss += df_tc.iloc[0][[f'tc_loss_ha_{y}' for y in mask_years]].sum()

    df_primary = primary_loss_df[primary_loss_df['country'] == c]
    if not df_primary.empty:
        total_primary_loss += df_primary.iloc[0][[f'tc_loss_ha_{y}' for y in mask_p]].sum()

    df_carbon = carbon_df[carbon_df['country'] == c]
    if not df_carbon.empty:
        emission_cols = [
            f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
            for y in mask_p if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in df_carbon.columns
        ]
        total_emission += df_carbon.iloc[0][emission_cols].sum() if emission_cols else 0

st.title("Negara")

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
for c in selected_countries:
    df_tc = tree_cover_loss_df[
        (tree_cover_loss_df['country'] == c) &
        (tree_cover_loss_df['threshold'] == selected_threshold)
    ]
    if not df_tc.empty:
        losses = df_tc.iloc[0][[f'tc_loss_ha_{y}' for y in mask_years]].values
        trend_data.append(pd.DataFrame({'Tahun': [str(y) for y in mask_years], 'Negara': c, 'Loss': losses}))
        total_loss = losses.sum()
        insight_data.append(f"**{c}** kehilangan total {total_loss:,.0f} ha pohon selama periode {tahun_min}-{tahun_max}.")

if trend_data:
    df_trend = pd.concat(trend_data)
    fig_tc = px.line(
        df_trend, x="Tahun", y="Loss", color="Negara",
        markers=True,
        labels={'Loss': 'Kehilangan (ha)', 'Tahun': 'Tahun'},
        color_discrete_map=warna_negara
    )
    fig_tc.update_layout(yaxis=dict(rangemode="tozero"))  # <=== Mulai dari 0
    st.plotly_chart(fig_tc, use_container_width=True)
    st.info("\n\n".join(insight_data))
else:
    st.info("Data kehilangan area berpohon tidak tersedia.")

st.markdown("---")

# =====================================
# 📌 Perbandingan Kehilangan Hutan Primer dan Komposisi Kehilangan Area Berpohon
# =====================================
st.markdown(f"### Perbandingan Kehilangan Hutan Primer dan Komposisi Kehilangan Area Berpohon ({tahun_min}–{tahun_max})")
col_pie, col_bar = st.columns(2)

# Donut Chart
with col_pie:
    pie_data = []
    for c in selected_countries:
        df_c = tree_cover_loss_df[
            (tree_cover_loss_df['country'] == c) &
            (tree_cover_loss_df['threshold'] == selected_threshold)
        ]
        if not df_c.empty:
            total = df_c.iloc[0][[f'tc_loss_ha_{y}' for y in mask_years]].sum()
            pie_data.append({'Negara': c, 'Loss': total})

    if pie_data:
        df_pie = pd.DataFrame(pie_data)
        fig_pie = px.pie(
            df_pie, names='Negara', values='Loss',
            hole=0.4,
            color='Negara',
            color_discrete_map=warna_negara
        )
        fig_pie.update_traces(textinfo='percent+label')
        fig_pie.update_layout(
            title_text=f"Komposisi Kehilangan Area Berpohon ({tahun_min}–{tahun_max})",
            legend_title_text="Negara",
            margin=dict(t=50, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# Stacked Bar Chart
with col_bar:
    comp_data = []
    for c in selected_countries:
        df_c = primary_loss_df[primary_loss_df['country'] == c]
        if not df_c.empty:
            values = df_c.iloc[0][[f'tc_loss_ha_{y}' for y in mask_p]].values
            comp_data.append(pd.DataFrame({'Tahun': [str(y) for y in mask_p], 'Negara': c, 'Loss': values}))

    if comp_data:
        df_comp = pd.concat(comp_data)
        fig_bar = px.bar(
            df_comp, x="Tahun", y="Loss", color="Negara",
            barmode="stack",
            labels={'Loss': 'Kehilangan (ha)', 'Tahun': 'Tahun'},
            color_discrete_map=warna_negara
        )
        fig_bar.update_layout(
            title_text=f"Perbandingan Kehilangan Hutan Primer ({tahun_min}–{tahun_max})",
            margin=dict(t=50, b=40, l=40, r=40)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.info(
    f"Diagram di atas menunjukkan perbandingan kehilangan hutan primer (kanan) dan komposisi kehilangan area berpohon (kiri) "
    f"antara dan negara pembanding selama {tahun_min}-{tahun_max}. "
    f"Negara yang tampil di donut chart namun tidak muncul di stacked bar chart berarti tidak memiliki data kehilangan hutan primer pada periode tersebut."
)

st.markdown("---")

# =====================================
# 📌 Perbandingan Total Emisi CO₂e Negara Terpilih
# =====================================
st.markdown(f"### Perbandingan Total Emisi CO₂e Negara Terpilih ({tahun_min}–{tahun_max})")

emission_cols_selected = [
    f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
    for y in range(tahun_min, tahun_max + 1)
    if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in carbon_df.columns
]

carbon_df['total_emission_selected'] = carbon_df[emission_cols_selected].sum(axis=1)
top_emission_selected = carbon_df[carbon_df['country'].isin(selected_countries)].sort_values(
    'total_emission_selected', ascending=False
)

fig_bar_total = px.bar(
    top_emission_selected,
    x='country', y='total_emission_selected',
    labels={'country': 'Negara', 'total_emission_selected': 'Total Emisi (Mg CO₂e)'},
    color='country',
    color_discrete_map=warna_negara
)
fig_bar_total.update_layout(yaxis=dict(rangemode="tozero"))
st.plotly_chart(fig_bar_total, use_container_width=True)

st.markdown("---")

# =====================================
# 📌 Tren Emisi CO₂e
# =====================================
st.markdown(f"### Tren Emisi CO₂e ({tahun_min}–{tahun_max})")

emission_trend_data = []
insight_emissions = []
for c in selected_countries:
    df_carbon = carbon_df[carbon_df['country'] == c]
    if not df_carbon.empty:
        carbon_cols = [
            f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e'
            for y in mask_p if f'gfw_forest_carbon_gross_emissions_{y}__Mg_CO2e' in df_carbon.columns
        ]
        if carbon_cols:
            emissions = df_carbon.iloc[0][carbon_cols].values
            years_emission = [int(col.split('_')[5]) for col in carbon_cols]

            emission_trend_data.append(pd.DataFrame({
                'Tahun': [str(y) for y in years_emission],
                'Negara': c,
                'Emisi': emissions
            }))

            max_idx = emissions.argmax()
            min_idx = emissions.argmin()
            tahun_max_em = years_emission[max_idx]
            tahun_min_em = years_emission[min_idx]
            emisi_max = emissions[max_idx]
            emisi_min = emissions[min_idx]
            emisi_avg = emissions.mean()
            selisih = emisi_max - emisi_min

            insight_emissions.append(
                f"**{c}**\n"
                f"- Tahun tertinggi: {tahun_max_em} ({emisi_max:,.0f} Mg CO₂e). "
                f"Tahun terendah: {tahun_min_em} ({emisi_min:,.0f} Mg CO₂e). "
                f"Rata-rata per tahun: {emisi_avg:,.0f} Mg CO₂e. "
                f"Selisih tertinggi-terendah: {selisih:,.0f} Mg CO₂e."
            )

if emission_trend_data:
    df_emission_trend = pd.concat(emission_trend_data)
    fig_emission = px.line(
        df_emission_trend, x="Tahun", y="Emisi", color="Negara",
        markers=True,
        labels={'Emisi': 'Emisi (Mg CO₂e)', 'Tahun': 'Tahun'},
        color_discrete_map=warna_negara
    )
    fig_emission.update_layout(yaxis=dict(rangemode="tozero"))  # Mulai dari 0
    st.plotly_chart(fig_emission, use_container_width=True)
    st.info("\n\n".join(insight_emissions))
else:
    st.info("Data emisi tidak tersedia.")
