
# 🌳 Dashboard Analisis Deforestasi & Emisi Karbon

## 👥 Penyusun

Disusun oleh **Kelompok Bekantan** untuk tugas **Data Analytics and Visualization**.

**Anggota:**
- 🐵 Ni Kadek Dwita Putri Suastini — 2205551074
- 🐵 Ni Komang Marsyani — 2205551052
- 🐵 Pande Komang Indah Triroshanti — 2205551053
- 🐵 Ni Putu Putri Maheswari Paramhansa — 2205551101

---

## 📌 Deskripsi Singkat

Halo! 👋  
Proyek ini adalah **dashboard interaktif** untuk menganalisis data deforestasi (kehilangan tutupan pohon & hutan primer) serta emisi karbon secara global.

Dashboard ini dikembangkan menggunakan **Streamlit**, **Pandas**, dan **Plotly** untuk memvisualisasikan data secara dinamis & mudah dipahami.

---

## 🎯 Tujuan Proyek

✅ Menyediakan insight tren deforestasi & emisi karbon berdasarkan data Global Forest Watch.  
✅ Membantu memantau dan membandingkan kondisi antar negara & wilayah subnasional.  
✅ Sarana belajar penerapan **Data Analytics and Visualization**.  
✅ Disusun untuk memenuhi tugas mata kuliah **Data Analytics and Visualization**.

---

## 🌍 Sumber Data

Data diambil dari [Global Forest Watch](https://www.globalforestwatch.org/)  
Data meliputi:
- Kehilangan tutupan pohon per tahun.
- Kehilangan hutan primer.
- Estimasi emisi karbon akibat deforestasi.

---

## 🗂️ Struktur Proyek

```plaintext
DEFORSTASI-EMISIKARBON-MAIN/
├── .devcontainer/
│   └── devcontainer.json
├── data/
│   └── global_05212025.xlsx
├── pages/
│   ├── 2_Negara.py
│   └── 3_Subnasional.py
├── utils/
│   └── data_loader.py
├── 1_Global.py
└── requirements.txt
```

---

## 📄 Deskripsi File

### 📄 `requirements.txt`
Daftar library Python yang dibutuhkan:
- **streamlit** : framework web interaktif
- **pandas** : manipulasi & analisis data
- **plotly** : visualisasi interaktif
- **openpyxl** : membaca file Excel

Cara install:
```bash
pip install -r requirements.txt
```

---

### 📁 `.devcontainer/devcontainer.json`
(Opsi) Setup Development Container di VS Code:
- Menjamin lingkungan pengembangan konsisten.
- Sudah memuat image Docker & ekstensi yang direkomendasikan.

---

### 📁 `data/global_05212025.xlsx`
Dataset utama:
- Data kehilangan tutupan pohon, hutan primer, & emisi karbon global.

---

### 📄 `1_Global.py`
**Halaman Analisis Global:**
- Menampilkan KPI total kehilangan tutupan pohon, hutan primer, & emisi karbon.
- Peta interaktif sebaran deforestasi global.
- Tren kehilangan hutan & emisi karbon tahunan.
- Top 5 negara dengan kehilangan hutan primer terbesar.

---

### 📁 `pages/2_Negara.py`
**Halaman Perbandingan Negara:**
- Filter: pilih negara, rentang tahun, kepadatan hutan.
- KPI deforestasi & emisi tiap negara.
- Donut chart, tren kehilangan pohon & hutan primer.
- Stacked bar chart & tren emisi karbon.

---

### 📁 `pages/3_Subnasional.py`
**Halaman Analisis Subnasional:**
- Fokus analisis wilayah **subnasional** (misalnya provinsi atau region).
- Filter: negara, subnasional, rentang tahun.
- KPI per wilayah.
- Grafik pie, tren kehilangan tutupan pohon & tren emisi karbon.

---

### 📁 `utils/data_loader.py`
Modul fungsi:
- `load_excel_data` untuk membaca file Excel.
- Menggunakan `@st.cache_data` agar pemrosesan data lebih efisien.

---

## 🔍 Bagaimana Dashboard Ini Bekerja

1️⃣ **Load Dataset**  
- Dataset `global_05212025.xlsx` dimuat melalui `utils/data_loader.py`.
- Data di-cache agar loading lebih cepat.

2️⃣ **Filter Sidebar**  
- Sidebar ➜ filter tahun, negara, subnasional.
- Filter diterapkan ke DataFrame.

3️⃣ **Hitung KPI**  
- Hitung total kehilangan tutupan pohon, hutan primer, & emisi karbon.

4️⃣ **Visualisasi Dinamis**  
- Peta ➜ choropleth.
- Grafik ➜ tren line chart, pie/donut chart, stacked bar.

5️⃣ **Halaman Modular**  
- `1_Global.py`: Global overview.
- `2_Negara.py`: Perbandingan negara.
- `3_Subnasional.py`: Detail wilayah subnasional.

6️⃣ **Interaktif & Otomatis**  
- Semua chart & KPI otomatis menyesuaikan filter.

---

## ⚙️ Cara Menjalankan Dashboard

1️⃣ **Clone repo**
```bash
git clone https://github.com/username/deforestasi-emisiKarbon.git
cd deforestasi-emisiKarbon
```

2️⃣ **(Opsional) Buat virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

3️⃣ **Install dependencies**
```bash
pip install -r requirements.txt
```

4️⃣ **Jalankan dashboard**
```bash
streamlit run 1_Global.py
```
Atau:
```bash
streamlit run pages/2_Negara.py
streamlit run pages/3_Subnasional.py
```

---

## 🛠️ Tools & Teknologi

* **Streamlit** — Dashboard web interaktif
* **Pandas** — Manipulasi & analisis data
* **Plotly** — Visualisasi dinamis
* **Openpyxl** — Membaca file Excel (.xlsx)

---
