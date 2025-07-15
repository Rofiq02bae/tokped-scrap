# 🛒 Tokopedia Data Scraper & Analyzer - Streamlit App

Aplikasi web interaktif untuk scraping, analisis, dan visualisasi data produk dari Tokopedia menggunakan Streamlit.

## 🚀 Cara Menjalankan

1. **Install dependensi:**
```bash
pip install -r requirements_streamlit.txt
```

2. **Jalankan aplikasi:**
```bash
streamlit run streamlit_app.py
```

3. **Buka browser dan akses:**
```
http://localhost:8501
```

## ✨ Fitur Utama

### 1. 🔍 **Scraping Data Real-time**
- Input keyword pencarian yang fleksibel
- Filter pencarian lanjutan (harga, rating, bebas ongkir, dll)
- Kontrol jumlah hasil dan detail data yang diambil
- Progress tracking selama proses scraping

### 2. 🔧 **Filter Pencarian**
- **Harga**: Rentang harga minimum dan maksimum
- **Rating**: Rating minimum produk
- **Bebas Ongkir**: Filter produk dengan bebas ongkir extra
- **Diskon**: Hanya produk yang sedang diskon
- **Jumlah Hasil**: Kontrol jumlah produk yang diambil (10-200)

### 3. 📊 **Data Preprocessing**
- Pembersihan data otomatis
- Normalisasi format harga, rating, dan sold count
- Kategorisasi harga dan rating
- Ekstraksi informasi toko
- Deteksi dan penanganan missing values

### 4. 📈 **Exploratory Data Analysis (EDA)**
- **Statistik Deskriptif**: Mean, median, std, quartiles
- **Distribusi Data**: Histogram dan pie charts
- **Analisis Korelasi**: Heatmap korelasi antar variabel
- **Analisis Toko**: Top sellers dan distribusi toko official

### 5. 💡 **Insight Analysis**
- Insight otomatis tentang variasi harga
- Analisis kualitas produk berdasarkan rating
- Identifikasi produk bestseller
- Pola distribusi per toko
- Rekomendasi berdasarkan analisis data

### 6. 📊 **Visualisasi Interaktif**

#### Analisis Harga:
- Distribusi harga dengan histogram interaktif
- Kategorisasi harga (budget vs premium)
- Pie chart distribusi kategori harga

#### Analisis Rating:
- Distribusi rating produk
- Scatter plot hubungan harga vs rating
- Kategorisasi kualitas produk

#### Analisis Toko:
- Top 10 toko dengan produk terbanyak
- Perbandingan toko official vs regular
- Analisis performa toko

#### Visualisasi Lanjutan:
- **3D Scatter Plot**: Harga vs Rating vs Jumlah Terjual
- **Heatmap Korelasi**: Matriks korelasi semua variabel numerik
- **Word Cloud**: Analisis kata kunci dari review produk

### 7. 📝 **Analisis Review (Jika Tersedia)**
- **Sentiment Analysis**: Penghitungan sentimen positif/negatif
- **Word Cloud**: Visualisasi kata-kata yang sering muncul
- **Insight Review**: Pola dan tren dalam review pelanggan

### 8. 📋 **Kesimpulan Otomatis**
- Ringkasan market overview
- Insight distribusi harga
- Analisis kualitas produk
- Identifikasi peluang pasar
- Rekomendasi strategis

### 9. 📥 **Export Data**
- **CSV Format**: Data yang sudah diproses untuk analisis lanjutan
- **JSON Format**: Data raw untuk keperluan development
- Timestamp otomatis pada nama file

## 🎯 Panduan Penggunaan

### Langkah 1: Setup Pencarian
1. Buka sidebar di sebelah kiri
2. Masukkan keyword pencarian (contoh: "laptop gaming", "mouse wireless")
3. Atur jumlah maksimal hasil yang diinginkan
4. Aktifkan filter jika diperlukan

### Langkah 2: Konfigurasi Filter (Opsional)
1. Centang "Gunakan filter pencarian"
2. Set rentang harga sesuai budget
3. Pilih rating minimum
4. Aktifkan filter bebas ongkir atau diskon jika diperlukan

### Langkah 3: Pilih Data yang Diambil
1. Centang "Ambil detail produk" untuk data lengkap
2. Centang "Ambil review produk" untuk analisis sentiment
3. Atur jumlah review per produk (1-50)

### Langkah 4: Mulai Scraping
1. Klik tombol "🚀 Mulai Scraping"
2. Tunggu proses selesai (progress bar akan muncul)
3. Data akan otomatis dianalisis dan ditampilkan

### Langkah 5: Eksplorasi Hasil
1. Lihat overview data di bagian atas
2. Eksplorasi berbagai visualisasi
3. Baca insight dan kesimpulan otomatis
4. Download data jika diperlukan

## 🛠️ Troubleshooting

### Error saat Scraping:
- Periksa koneksi internet
- Reduce jumlah maksimal hasil
- Nonaktifkan filter yang terlalu ketat
- Coba keyword yang lebih umum

### Aplikasi Lambat:
- Kurangi jumlah hasil maksimal
- Nonaktifkan pengambilan review jika tidak diperlukan
- Gunakan browser yang lebih ringan

### Data Tidak Muncul:
- Refresh browser (Ctrl+F5)
- Restart aplikasi Streamlit
- Periksa console untuk error messages

## 📊 Contoh Use Cases

### 1. Market Research
- Analisis kompetitor dalam kategori tertentu
- Identifikasi gap harga di pasar
- Analisis strategi pricing kompetitor

### 2. Product Positioning
- Benchmark rating produk sejenis
- Analisis distribusi harga pasar
- Identifikasi sweet spot harga vs kualitas

### 3. Seller Analysis
- Identifikasi top performer di kategori
- Analisis strategi toko official vs regular
- Benchmark performa penjualan

### 4. Customer Insights
- Analisis sentiment dari review
- Identifikasi pain points pelanggan
- Trending keywords dalam review

## 🔧 Kustomisasi

### Menambah Filter Baru:
Edit bagian `SearchFilters` di sidebar untuk menambah parameter pencarian baru.

### Menambah Visualisasi:
Tambahkan chart baru di fungsi `display_analysis()` menggunakan Plotly atau Matplotlib.

### Menambah Insight:
Edit fungsi `generate_insights()` untuk menambah logika analisis baru.

### Custom Styling:
Modifikasi CSS di bagian `st.markdown()` untuk mengubah tampilan aplikasi.

## 📈 Tips untuk Analisis yang Efektif

1. **Start Small**: Mulai dengan jumlah hasil kecil (20-50) untuk testing
2. **Use Filters**: Manfaatkan filter untuk hasil yang lebih relevan
3. **Compare Categories**: Bandingkan berbagai kategori produk
4. **Track Trends**: Lakukan scraping berkala untuk melihat tren
5. **Export Data**: Simpan data untuk analisis lebih lanjut di tools lain

## 🤝 Contributing

Untuk menambah fitur atau melaporkan bug:
1. Fork repository ini
2. Buat branch baru untuk fitur/fix Anda
3. Submit pull request dengan deskripsi yang jelas

## 📄 License

Project ini menggunakan MIT License. Silakan gunakan dan modifikasi sesuai kebutuhan.
