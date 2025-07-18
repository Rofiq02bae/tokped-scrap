import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
import time
from datetime import datetime
import re
from collections import Counter

# Import tokopaedi library
from tokopaedi import search, SearchFilters, get_product, get_reviews, combine_data

# Page configuration
st.set_page_config(
    page_title="analisis penjualan produk mouse logitech",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 2rem;
        color: #4682B4;
        border-bottom: 2px solid #4682B4;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E8B57;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4682B4;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data
def preprocess_data(data):
    """Preprocess the scraped data"""
    df = pd.json_normalize(data)
    
    # Clean price data
    if 'real_price' in df.columns:
        df['real_price'] = pd.to_numeric(df['real_price'], errors='coerce')
    
    # Clean rating data
    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # Clean sold count
    if 'sold_count' in df.columns:
        df['sold_count'] = pd.to_numeric(df['sold_count'], errors='coerce')
    
    # Extract shop information
    if 'shop.name' in df.columns:
        df['shop_name'] = df['shop.name']
    if 'shop.city' in df.columns:
        df['shop_city'] = df['shop.city']
    if 'shop.is_official' in df.columns:
        df['is_official_shop'] = df['shop.is_official']
    
    # Create price categories
    if 'real_price' in df.columns:
        df['price_category'] = pd.cut(df['real_price'], 
                                    bins=[0, 50000, 100000, 200000, 500000, float('inf')],
                                    labels=['<50K', '50K-100K', '100K-200K', '200K-500K', '>500K'])
    
    # Create rating categories
    if 'rating' in df.columns:
        df['rating_category'] = pd.cut(df['rating'],
                                     bins=[0, 3, 4, 4.5, 5],
                                     labels=['Poor (0-3)', 'Good (3-4)', 'Very Good (4-4.5)', 'Excellent (4.5-5)'])
    
    return df

def extract_review_insights(data):
    """Extract insights from product reviews"""
    all_reviews = []
    for product in data:
        if 'product_reviews' in product and product['product_reviews']:
            for review in product['product_reviews']:
                if 'message' in review:
                    all_reviews.append(review['message'])
    
    if not all_reviews:
        return None, None, None
    
    # Combine all reviews
    all_text = ' '.join(all_reviews)
    
    # Simple sentiment analysis (basic keyword matching)
    positive_words = ['bagus', 'baik', 'mantap', 'recommended', 'puas', 'original', 'cepat', 'oke', 'sesuai']
    negative_words = ['buruk', 'jelek', 'lambat', 'rusak', 'mengecewakan', 'tidak sesuai', 'palsu']
    
    positive_count = sum(1 for word in positive_words if word in all_text.lower())
    negative_count = sum(1 for word in negative_words if word in all_text.lower())
    
    # Word frequency
    words = re.findall(r'\b\w+\b', all_text.lower())
    word_freq = Counter(words)
    common_words = dict(word_freq.most_common(20))
    
    return positive_count, negative_count, common_words

def main():
    # Header
    st.markdown('<h1 class="main-header">🛒analisis penjualan produk mouse logitech</h1>', unsafe_allow_html=True)
    st.markdown("Aplikasi untuk scraping, analisis, dan visualisasi data produk Tokopedia")
    
    # Sidebar - Filters and Controls
    st.sidebar.markdown("## 🔧 Configuration")
    
    # Search parameters
    st.sidebar.markdown("### Search Parameters")
    keyword = st.sidebar.text_input("Keyword pencarian", value="mouse logitech", help="Masukkan kata kunci produk yang ingin dicari")
    max_results = st.sidebar.slider("Jumlah maksimal hasil", min_value=10, max_value=200, value=50, step=10)
    
    # Search filters
    st.sidebar.markdown("### Search Filters")
    use_filters = st.sidebar.checkbox("Gunakan filter pencarian")
    
    filters = None
    if use_filters:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            pmin = st.number_input("Harga minimum", min_value=0, value=0, step=10000)
        with col2:
            pmax = st.number_input("Harga maksimum", min_value=0, value=1000000, step=10000)
        
        rt = st.sidebar.slider("Rating minimum", min_value=0.0, max_value=5.0, value=4.0, step=0.5)
        bebas_ongkir = st.sidebar.checkbox("Bebas ongkir extra")
        is_discount = st.sidebar.checkbox("Hanya produk diskon")
        
        if pmin > 0 or pmax < 1000000 or rt > 0 or bebas_ongkir or is_discount:
            filters = SearchFilters(
                pmin=pmin if pmin > 0 else None,
                pmax=pmax if pmax < 1000000 else None,
                rt=rt if rt > 0 else None,
                bebas_ongkir_extra=bebas_ongkir,
                is_discount=is_discount
            )
    
    # Scraping controls
    st.sidebar.markdown("### Scraping Options")
    include_details = st.sidebar.checkbox("Ambil detail produk", value=True)
    include_reviews = st.sidebar.checkbox("Ambil review produk", value=True)
    max_reviews = st.sidebar.slider("Maksimal review per produk", min_value=1, max_value=50, value=10)
    
    # Action buttons
    if st.sidebar.button("🚀 Mulai Scraping", type="primary"):
        st.session_state.scraping = True
    
    if st.sidebar.button("📄 Load Sample Data"):
        st.session_state.load_sample = True
    
    # Main content area
    if hasattr(st.session_state, 'scraping') and st.session_state.scraping:
        scrape_and_analyze(keyword, max_results, filters, include_details, include_reviews, max_reviews)
        st.session_state.scraping = False
    
    elif hasattr(st.session_state, 'load_sample') and st.session_state.load_sample:
        load_sample_data()
        st.session_state.load_sample = False
    
    elif hasattr(st.session_state, 'data'):
        display_analysis(st.session_state.data, st.session_state.df)
    
    else:
        show_welcome_page()

def scrape_and_analyze(keyword, max_results, filters, include_details, include_reviews, max_reviews):
    """Perform scraping and analysis"""
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Search products
        status_text.text("🔍 Mencari produk...")
        results = search(keyword, max_result=max_results, filters=filters, debug=False)
        progress_bar.progress(30)
        
        if not results:
            st.error("Tidak ada produk ditemukan dengan keyword tersebut.")
            return
        
        # Step 2: Get additional data if requested
        if include_details or include_reviews:
            status_text.text("📊 Mengambil data detail dan review...")
            for i, result in enumerate(results):
                product_data = None
                review_data = None
                
                if include_details:
                    try:
                        product_data = get_product(product_id=result.product_id, debug=False)
                    except Exception as e:
                        st.warning(f"Gagal mengambil detail produk {result.product_id}: {str(e)}")
                
                if include_reviews:
                    try:
                        review_data = get_reviews(product_id=result.product_id, max_result=max_reviews, debug=False)
                    except Exception as e:
                        st.warning(f"Gagal mengambil review produk {result.product_id}: {str(e)}")
                
                if product_data or review_data:
                    combine_data(result, product_data, review_data)
                
                # Update progress
                progress = 30 + (i + 1) / len(results) * 50
                progress_bar.progress(int(progress))
        
        # Step 3: Process data
        status_text.text("🔄 Memproses data...")
        data = results.json()
        df = preprocess_data(data)
        progress_bar.progress(90)
        
        # Store in session state
        st.session_state.data = data
        st.session_state.df = df
        st.session_state.keyword = keyword
        
        progress_bar.progress(100)
        status_text.text("✅ Scraping selesai!")
        time.sleep(1)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        display_analysis(data, df)
        
    except Exception as e:
        st.error(f"Error during scraping: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def load_sample_data():
    """Load sample data from output.json if available"""
    try:
        with open('output.json', 'r') as f:
            data = json.load(f)
        
        df = preprocess_data(data)
        st.session_state.data = data
        st.session_state.df = df
        st.session_state.keyword = "mouse logitech (sample)"
        
        st.success("Sample data berhasil dimuat!")
        display_analysis(data, df)
        
    except FileNotFoundError:
        st.error("File output.json tidak ditemukan. Silakan lakukan scraping terlebih dahulu.")
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")

def show_welcome_page():
    """Display welcome page with instructions"""
    st.markdown('<h2 class="section-header">Selamat Datang!</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        selamat datang
        """)
    
    with col2:
        st.image("https://images.tokopedia.net/img/tokopedia-logo.png", width=200)
        
        st.markdown("""
        <div class="metric-card">
        <h4>💡 Tips:</h4>
        <ul>
        <li>Gunakan keyword yang spesifik</li>
        <li>Batasi jumlah hasil untuk performa yang lebih baik</li>
        <li>Aktifkan filter untuk hasil yang lebih relevan</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

def display_analysis(data, df):
    """Display comprehensive analysis results"""
    
    # Overview section
    st.markdown('<h2 class="section-header">📊 Overview Data</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Produk", len(df))
    with col2:
        if 'real_price' in df.columns:
            avg_price = df['real_price'].mean()
            st.metric("Rata-rata Harga", f"Rp {avg_price:,.0f}")
    with col3:
        if 'rating' in df.columns:
            avg_rating = df['rating'].mean()
            st.metric("Rata-rata Rating", f"{avg_rating:.2f}")
    with col4:
        if 'sold_count' in df.columns:
            total_sold = df['sold_count'].sum()
            st.metric("Total Terjual", f"{total_sold:,.0f}")
    
    # Preprocessing section
    st.markdown('<h2 class="section-header">🔄 Data Preprocessing</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Info Dataset")
        st.write(f"**Jumlah baris**: {len(df)}")
        st.write(f"**Jumlah kolom**: {len(df.columns)}")
        
        # Missing values
        if st.checkbox("Tampilkan missing values"):
            missing_data = df.isnull().sum()
            missing_data = missing_data[missing_data > 0]
            if len(missing_data) > 0:
                st.write("**Missing values:**")
                for col, count in missing_data.items():
                    st.write(f"- {col}: {count} ({count/len(df)*100:.1f}%)")
            else:
                st.write("✅ Tidak ada missing values")
    
    with col2:
        st.subheader("Sample Data")
        st.dataframe(df.head())
    
    # EDA section
    st.markdown('<h2 class="section-header">📈 Exploratory Data Analysis (EDA)</h2>', unsafe_allow_html=True)
    
    # Statistical summary
    if st.checkbox("Tampilkan statistik deskriptif"):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            st.subheader("Statistik Deskriptif")
            st.dataframe(df[numeric_cols].describe())
    
    # Price analysis
    if 'real_price' in df.columns:
        st.subheader("📊 Analisis Harga")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price distribution
            fig = px.histogram(df, x='real_price', nbins=30, 
                             title="Distribusi Harga Produk",
                             labels={'real_price': 'Harga (Rp)', 'count': 'Jumlah Produk'})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price by category
            if 'price_category' in df.columns:
                price_cat_dist = df['price_category'].value_counts()
                fig = px.pie(values=price_cat_dist.values, names=price_cat_dist.index,
                           title="Distribusi Kategori Harga")
                st.plotly_chart(fig, use_container_width=True)
    
    # Rating analysis
    if 'rating' in df.columns:
        st.subheader("⭐ Analisis Rating")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Rating distribution
            fig = px.histogram(df, x='rating', nbins=20,
                             title="Distribusi Rating Produk",
                             labels={'rating': 'Rating', 'count': 'Jumlah Produk'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating vs Price scatter
            if 'real_price' in df.columns:
                fig = px.scatter(df, x='real_price', y='rating', 
                               title="Hubungan Harga vs Rating",
                               labels={'real_price': 'Harga (Rp)', 'rating': 'Rating'},
                               opacity=0.6)
                st.plotly_chart(fig, use_container_width=True)
    
    # Shop analysis
    if 'shop_name' in df.columns:
        st.subheader("🏪 Analisis Toko")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top shops by product count
            top_shops = df['shop_name'].value_counts().head(10)
            fig = px.bar(x=top_shops.values, y=top_shops.index, orientation='h',
                        title="Top 10 Toko dengan Produk Terbanyak",
                        labels={'x': 'Jumlah Produk', 'y': 'Nama Toko'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Official vs non-official shops
            if 'is_official_shop' in df.columns:
                official_dist = df['is_official_shop'].value_counts()
                fig = px.pie(values=official_dist.values, 
                           names=['Toko Biasa' if not x else 'Toko Official' for x in official_dist.index],
                           title="Distribusi Toko Official vs Biasa")
                st.plotly_chart(fig, use_container_width=True)
    
    # Insight Analysis
    st.markdown('<h2 class="section-header">💡 Insight Analysis</h2>', unsafe_allow_html=True)
    
    insights = generate_insights(df)
    for insight in insights:
        st.markdown(f'<div class="insight-box">💡 {insight}</div>', unsafe_allow_html=True)
    
    # Review analysis (if available)
    positive_count, negative_count, common_words = extract_review_insights(data)
    if positive_count is not None:
        st.subheader("📝 Analisis Review")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Sentiment Positif", positive_count)
        with col2:
            st.metric("Sentiment Negatif", negative_count)
        with col3:
            sentiment_ratio = positive_count / (positive_count + negative_count) if (positive_count + negative_count) > 0 else 0
            st.metric("Rasio Positif", f"{sentiment_ratio:.2%}")
        
        # Word cloud
        if common_words:
            st.subheader("☁️ Word Cloud Review")
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(common_words)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation='bilinear')
            ax.axis('off')
            st.pyplot(fig)
    
    # Interactive visualizations
    st.markdown('<h2 class="section-header">📊 Visualisasi Interaktif</h2>', unsafe_allow_html=True)
    
    # Multi-dimensional analysis
    if 'real_price' in df.columns and 'rating' in df.columns and 'sold_count' in df.columns:
        fig = px.scatter_3d(df, x='real_price', y='rating', z='sold_count',
                           color='rating', size='sold_count',
                           title="Analisis 3D: Harga vs Rating vs Jumlah Terjual",
                           labels={'real_price': 'Harga (Rp)', 'rating': 'Rating', 'sold_count': 'Terjual'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation heatmap
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        st.subheader("🔥 Heatmap Korelasi")
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(corr_matrix, 
                       labels=dict(color="Korelasi"),
                       title="Matriks Korelasi Variabel Numerik")
        st.plotly_chart(fig, use_container_width=True)
    
    # Conclusions
    st.markdown('<h2 class="section-header">📝 Kesimpulan</h2>', unsafe_allow_html=True)
    
    conclusions = generate_conclusions(df, data)
    for i, conclusion in enumerate(conclusions, 1):
        st.markdown(f"**{i}.** {conclusion}")
    
    # Download options
    st.markdown('<h2 class="section-header">📥 Download Data</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Download processed CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV",
            data=csv,
            file_name=f"tokopedia_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Download raw JSON
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"tokopedia_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def generate_insights(df):
    """Generate data insights"""
    insights = []
    
    if 'real_price' in df.columns:
        price_stats = df['real_price'].describe()
        insights.append(f"Rentang harga produk sangat bervariasi dari Rp {price_stats['min']:,.0f} hingga Rp {price_stats['max']:,.0f}")
        
        if price_stats['std'] > price_stats['mean']:
            insights.append("Variasi harga produk sangat tinggi, menunjukkan keragaman segmen pasar")
    
    if 'rating' in df.columns:
        high_rating_pct = (df['rating'] >= 4.5).mean() * 100
        insights.append(f"{high_rating_pct:.1f}% produk memiliki rating sangat baik (≥4.5)")
        
        if 'real_price' in df.columns:
            correlation = df['real_price'].corr(df['rating'])
            if abs(correlation) > 0.3:
                direction = "positif" if correlation > 0 else "negatif"
                insights.append(f"Terdapat korelasi {direction} antara harga dan rating (r={correlation:.2f})")
    
    if 'sold_count' in df.columns:
        bestseller_threshold = df['sold_count'].quantile(0.8)
        bestseller_pct = (df['sold_count'] >= bestseller_threshold).mean() * 100
        insights.append(f"{bestseller_pct:.1f}% produk dapat dikategorikan sebagai bestseller")
    
    if 'shop_name' in df.columns:
        unique_shops = df['shop_name'].nunique()
        total_products = len(df)
        avg_products_per_shop = total_products / unique_shops
        insights.append(f"Rata-rata setiap toko menjual {avg_products_per_shop:.1f} produk dalam kategori ini")
    
    return insights

def generate_conclusions(df, data):
    """Generate analysis conclusions"""
    conclusions = []
    
    # Market overview
    total_products = len(df)
    conclusions.append(f"Ditemukan {total_products} produk yang menunjukkan tingkat kompetisi yang {'tinggi' if total_products > 50 else 'sedang'} dalam kategori ini")
    
    # Price insights
    if 'real_price' in df.columns:
        price_median = df['real_price'].median()
        price_mean = df['real_price'].mean()
        
        if price_mean > price_median * 1.2:
            conclusions.append(f"Distribusi harga condong ke kiri dengan median Rp {price_median:,.0f}, menunjukkan banyak produk budget-friendly")
        else:
            conclusions.append(f"Distribusi harga relatif normal dengan harga tengah di Rp {price_median:,.0f}")
    
    # Quality insights
    if 'rating' in df.columns:
        avg_rating = df['rating'].mean()
        if avg_rating >= 4.5:
            conclusions.append("Kualitas produk secara keseluruhan sangat baik dengan rating rata-rata tinggi")
        elif avg_rating >= 4.0:
            conclusions.append("Kualitas produk secara keseluruhan baik dengan ruang untuk perbaikan")
        else:
            conclusions.append("Kualitas produk bervariasi dengan beberapa produk yang perlu perhatian khusus")
    
    # Market opportunity
    if 'sold_count' in df.columns and 'rating' in df.columns:
        low_sold_high_rating = df[(df['sold_count'] < df['sold_count'].median()) & (df['rating'] >= 4.5)]
        if len(low_sold_high_rating) > 0:
            conclusions.append(f"Terdapat {len(low_sold_high_rating)} produk berkualitas tinggi dengan penjualan rendah yang berpotensi untuk dioptimalkan")
    
    # Recommendation
    conclusions.append("Untuk masuk ke pasar ini, fokus pada kualitas produk dan strategi pricing yang kompetitif berdasarkan analisis distribusi harga")
    
    return conclusions

if __name__ == "__main__":
    main()
