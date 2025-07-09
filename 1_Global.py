import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Deforestasi dan Emisi Karbon", layout="wide")
st.title("Deforestasi dan Emisi Karbon Global")


# === Load Data ===
tree_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country tree cover loss")
primary_loss_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country primary loss")
carbon_df = pd.read_excel("data/global_05212025.xlsx", sheet_name="Country carbon data")

# === Filter Threshold 30% ===
tree_loss_df = tree_loss_df[tree_loss_df["threshold"] == 30]
primary_loss_df = primary_loss_df[primary_loss_df["threshold"] == 30]
carbon_df = carbon_df[carbon_df["umd_tree_cover_density_2000__threshold"] == 30]

# === Kolom Tahun ===
tree_loss_cols = [col for col in tree_loss_df.columns if "tc_loss_ha_" in col]
primary_loss_cols = [col for col in primary_loss_df.columns if "tc_loss_ha_" in col]
available_years = sorted([int(col.split("_")[-1]) for col in primary_loss_cols])

# === Sidebar Filter Tahun ===
with st.sidebar:
    st.markdown("### Filter Tahun")
    selected_years = st.slider("Rentang Tahun", min(available_years), max(available_years), (2002, 2024), step=1)

year_cols_selected = [f"tc_loss_ha_{y}" for y in range(selected_years[0], selected_years[1] + 1)]

# === KPI ===
total_tree_loss = tree_loss_df[year_cols_selected].sum().sum()
total_primary_loss = primary_loss_df[year_cols_selected].sum().sum()
gain_total = tree_loss_df["gain_2000-2012_ha"].sum()
carbon_years = len(year_cols_selected)
total_years_available = len(available_years)
net_flux = carbon_df["gfw_forest_carbon_net_flux__Mg_CO2e_yr-1"].sum() * (carbon_years / total_years_available)

# === KPI Cards ===
st.markdown(f"#### Ringkasan Indikator Utama ({selected_years[0]}–{selected_years[1]})")
k1, k2, k3, k4 = st.columns([1, 1, 1, 1.6])
k1.metric("Kehilangan Area Berpohon", f"{total_tree_loss:,.0f} ha")
k2.metric("Kehilangan Hutan Primer", f"{total_primary_loss:,.0f} ha")
k3.metric("Pertumbuhan Area Berpohon", f"{gain_total:,.0f} ha")
k4.metric("Net Emisi Karbon", f"{net_flux:,.0f} t CO2e")

st.markdown("---")

# === Peta Global ===
tree_loss_df["total_loss"] = tree_loss_df[year_cols_selected].sum(axis=1)
carbon_avg_emission = carbon_df["gfw_forest_carbon_gross_emissions__Mg_CO2e_yr-1"] * (carbon_years / total_years_available)

fig_loss_map = px.choropleth(
    tree_loss_df,
    locations="country",
    locationmode="country names",
    color="total_loss",
    hover_name="country",
    color_continuous_scale="YlGn_r",
    title=f"Peta Total Kehilangan Area Berpohon ({selected_years[0]}–{selected_years[1]})",
    labels={"total_loss": "Total Kehilangan (ha)"}
)

fig_emission_map = px.choropleth(
    carbon_df.assign(avg_emission=carbon_avg_emission),
    locations="country",
    locationmode="country names",
    color="avg_emission",
    hover_name="country",
    color_continuous_scale="Reds",
    title=f"Peta Rata-rata Emisi Karbon Tahunan ({selected_years[0]}–{selected_years[1]})",
    labels={"avg_emission": "Emisi CO2e (t)"}
)

st.markdown("#### Peta Global")
col_map1, col_map2 = st.columns(2)
col_map1.plotly_chart(fig_loss_map, use_container_width=True)
col_map2.plotly_chart(fig_emission_map, use_container_width=True)

st.markdown("---")

# === Kehilangan Hutan Primer Global ===
st.markdown(f"#### Kehilangan Hutan Primer Global ({selected_years[0]}–{selected_years[1]})")

total_loss_selected = primary_loss_df[year_cols_selected].sum().sum()
total_forest_area_2000 = primary_loss_df["area__ha"].sum()
percentage_loss = round((total_loss_selected / total_forest_area_2000) * 100, 2)
emissions_total = carbon_df["gfw_forest_carbon_gross_emissions__Mg_CO2e_yr-1"].sum() * (carbon_years / total_years_available)

st.info(f"""
Dari tahun **{selected_years[0]} hingga {selected_years[1]}**, dunia kehilangan sekitar **{round(total_loss_selected/1e6, 1)} juta hektar** hutan primer dengan kerapatan tajuk minimal 30%. Kehilangan ini setara dengan **{percentage_loss}% dari total luas hutan global pada tahun 2000**, yaitu sekitar **{round(total_forest_area_2000/1e9, 2)} miliar hektar**. Selama periode tersebut, estimasi total emisi karbon akibat kehilangan hutan mencapai sekitar **{round(emissions_total/1e9, 2)} miliar ton CO₂e**.
""")

# === Stacked Bar: Top 5 Negara per Tahun ===
df_long = primary_loss_df.melt(
    id_vars=["country"],
    value_vars=year_cols_selected,
    var_name="Tahun",
    value_name="Kehilangan (ha)"
)
df_long["Tahun"] = df_long["Tahun"].str.extract(r"(\d+)$")[0].astype(int)

def group_top5_per_year(df):
    result = []
    for year in df["Tahun"].unique():
        top5 = df[df["Tahun"] == year].groupby("country")["Kehilangan (ha)"].sum().nlargest(5).index.tolist()
        for _, row in df[df["Tahun"] == year].iterrows():
            row["Negara"] = row["country"] if row["country"] in top5 else "Other"
            result.append(row)
    return pd.DataFrame(result)

df_grouped = group_top5_per_year(df_long)
agg = df_grouped.groupby(["Tahun", "Negara"])["Kehilangan (ha)"].sum().reset_index()

tooltip_map = {}
for year in agg["Tahun"].unique():
    sub = agg[agg["Tahun"] == year]
    tooltip = f"<b>{year}</b><br>Total: {round(sub['Kehilangan (ha)'].sum()/1e6,2)} Mha<br>"
    for _, row in sub.sort_values("Kehilangan (ha)", ascending=False).iterrows():
        tooltip += f"{row['Negara']}: {round(row['Kehilangan (ha)']/1e3, 1)} kha<br>"
    tooltip_map[year] = tooltip

fig = go.Figure()
negara_unique = agg["Negara"].unique()
for negara in negara_unique:
    sub = agg[agg["Negara"] == negara]
    fig.add_trace(go.Bar(
        x=sub["Tahun"].astype(str),
        y=sub["Kehilangan (ha)"],
        name=negara,
        hovertext=[tooltip_map[t] for t in sub["Tahun"]],
        hovertemplate="%{hovertext}<extra></extra>"
    ))

fig.update_layout(
    barmode="stack",
    xaxis_title="Tahun",
    yaxis_title="Kehilangan Hutan Primer (ha)",
    xaxis=dict(tickmode='linear', dtick=1),
    hoverlabel=dict(bgcolor="black", font_size=14, font_color="white"),
    legend_title="Negara",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# === Tren Global ===
st.markdown(f"#### Tren Global ({selected_years[0]}–{selected_years[1]})")

tree_loss_by_year = pd.DataFrame({
    "Tahun": [int(col.split("_")[-1]) for col in tree_loss_cols],
    "Kehilangan Area Berpohon (juta ha)": tree_loss_df[tree_loss_cols].sum().values / 1e6
})
tree_loss_by_year = tree_loss_by_year[
    (tree_loss_by_year["Tahun"] >= selected_years[0]) & 
    (tree_loss_by_year["Tahun"] <= selected_years[1])
]

fig_loss_line = px.line(
    tree_loss_by_year,
    x="Tahun",
    y="Kehilangan Area Berpohon (juta ha)",
    title=f"Tren Kehilangan Area Berpohon Global per Tahun ({selected_years[0]}–{selected_years[1]})",
    markers=True
)
fig_loss_line.update_traces(line_color="#ff7f0e", marker_color="#ff7f0e")
fig_loss_line.update_layout(xaxis=dict(tickmode="linear", dtick=1))

total_emissions = carbon_df["gfw_forest_carbon_gross_emissions__Mg_CO2e_yr-1"].sum() * (carbon_years / total_years_available)
total_removals = carbon_df["gfw_forest_carbon_gross_removals__Mg_CO2_yr-1"].sum() * (carbon_years / total_years_available)

fig_emission_bar = px.bar(
    pd.DataFrame({
        "Kategori": ["Emisi", "Penyerapan"],
        "Nilai (Gt CO₂e)": [total_emissions / 1e9, total_removals / 1e9]
    }),
    x="Kategori",
    y="Nilai (Gt CO₂e)",
    text="Nilai (Gt CO₂e)",
    color="Kategori",
    color_discrete_map={"Emisi": "#ff7f0e", "Penyerapan": "#1f77b4"},
    title=f"Total Emisi vs Penyerapan Karbon Tahunan Global ({selected_years[0]}–{selected_years[1]})"
)
fig_emission_bar.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig_emission_bar.update_layout(yaxis_title="Jumlah Karbon (miliar ton CO₂e)")

col_trend1, col_trend2 = st.columns(2)
col_trend1.plotly_chart(fig_loss_line, use_container_width=True)
col_trend2.plotly_chart(fig_emission_bar, use_container_width=True)

st.markdown("---")

# === Insight Akhir ===
st.info("""
Kehilangan area berpohon pada tingkat global terus menunjukkan pola fluktuatif dengan lonjakan signifikan pada tahun-tahun tertentu. Hal ini mencerminkan tekanan konversi lahan yang belum terkendali. Meskipun demikian, sistem hutan dunia secara keseluruhan masih berfungsi sebagai penyerap karbon bersih, dengan penyerapan karbon tahunan melampaui total emisi akibat gangguan hutan.
""")

st.info("""
**Apa yang Bisa Kita Lakukan?**

Memperkuat moratorium deforestasi, memperluas kawasan lindung, dan mendorong restorasi lanskap berbasis komunitas menjadi langkah krusial untuk menjaga fungsi ekologis hutan.
""")
