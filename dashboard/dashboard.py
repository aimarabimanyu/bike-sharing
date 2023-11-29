import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import streamlit as st
from datetime import datetime, time
sns.set(style='dark')

def hour_df_workday(df):
    # Membuat dataframe baru yang berisi data day_df pada hari kerja
    hour_df_workday = df[df['is_workingday'] == 'yes']

    return hour_df_workday

def hour_df_holiday(df):
    # Membuat dataframe baru yang berisi data day_df pada hari libur
    hour_df_holiday = df[df['is_workingday'] == 'no']

    return hour_df_holiday

def season_df(df):
    # Membuat dataframe baru yang berisi total user pada data day_df berdasarkan season
    season_df = df.groupby(['season']).agg({
        'total_user': 'sum'
    }).sort_values(by='total_user', ascending=False).reset_index()

    return season_df

def temp_total_user(df):
    # Membuat dataframe baru yang berisi data dari day_df kolom temp dan total_user
    temp_total_user = df[['temp', 'total_user']]

    return temp_total_user

def year_month_df(df):
    # Mengganti tipe data kolom date menjadi datetime
    df['month'] = pd.to_datetime(df['date']).dt.month

    # Membuat dataframe baru yang berisi total user pada data day_df berdasarkan tahun dan bulan
    year_month_df = day_df.groupby(['year', 'month']).agg({
        'total_user': 'sum'
    }).reset_index()

    return year_month_df

def cluster_df(df):
    # Menentukan jumlah cluster
    kmeans = KMeans(n_clusters=3)

    # Menentukan feature yang akan digunakan
    X = df[['atemp', 'humidity']]

    # Melakukan clustering
    day_df_atemp_hum_class = kmeans.fit_predict(X)

    # Buat dataframe baru yang berisi atemp, humidity, total user, dan hasil clustering
    day_cluster_df = df[['atemp', 'humidity', 'total_user']]
    day_cluster_df['cluster'] = day_df_atemp_hum_class

    # Buat dataframe baru yang berisi total user berdasarkan hasil clustering
    cluster_df = day_cluster_df.groupby(['cluster']).agg({
        'total_user': 'sum'
    }).reset_index()

    return cluster_df

def time_casual_user(df):
    # Mencari waktu ketika penggunaan sepeda paling tinggi
    time_total_user_df = df.groupby(['hour']).agg({
        'casual_user': 'sum'
    }).reset_index()

    # Mencari waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    max_time = datetime.strptime(str(time_total_user_df.loc[time_total_user_df['casual_user'].idxmax(), 'hour']), '%H').strftime('%H:%M')
    min_time = datetime.strptime(str(time_total_user_df.loc[time_total_user_df['casual_user'].idxmin(), 'hour']), '%H').strftime('%H:%M')

    return max_time, min_time

def time_registered_user(df):
    # Mencari waktu ketika penggunaan sepeda paling tinggi
    time_total_user_df = df.groupby(['hour']).agg({
        'registered_user': 'sum'
    }).reset_index()

    # Mencari waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    max_time = datetime.strptime(str(time_total_user_df.loc[time_total_user_df['registered_user'].idxmax(), 'hour']), '%H').strftime('%H:%M')
    min_time = datetime.strptime(str(time_total_user_df.loc[time_total_user_df['registered_user'].idxmin(), 'hour']), '%H').strftime('%H:%M')

    return max_time, min_time

if __name__ == '__main__':
    # Load data
    day_df = pd.read_csv('day_clean.csv')
    hour_df = pd.read_csv('hour_clean.csv')

    # Convert date column ke datetime
    day_df['date'] = pd.to_datetime(day_df['date'])

    # Mencari tanggal minimum dan maksimum
    min_date_days = day_df['date'].min()
    max_date_days = day_df['date'].max()

    # Buat sidebar
    with st.sidebar:
        # Menambahkan logo perusahaan
        st.image("bike-share.png")

        # Mengambil start_date & end_date dari date_input
        start_datetime, end_datetime = st.date_input(
            label='Rentang Waktu', min_value=min_date_days, max_value=max_date_days, value=[min_date_days, max_date_days]
        )

        # Menambahkan input jam menggunakan widget st.time_input()
        start_time = st.time_input(label='Waktu Mulai', value=time(0, 0))
        end_time = st.time_input(label='Waktu Selesai', value=time(23, 0))

    # Ambil data berdasarkan rentang waktu
    day_df = day_df[(day_df['date'] >= str(start_datetime)) & (day_df['date'] <= str(end_datetime))]
    hour_df = hour_df[(hour_df['date'] >= str(start_datetime)) & (hour_df['date'] <= str(end_datetime)) & (hour_df['hour'] >= start_time.hour) & (hour_df['hour'] <= end_time.hour)]

    # Membuat dataframe yang dibutuhkan untuk visualisasi
    hour_df_workday = hour_df_workday(hour_df)
    hour_df_holiday = hour_df_holiday(hour_df)
    season_df = season_df(day_df)
    temp_total_user = temp_total_user(day_df)
    year_month_df = year_month_df(day_df)
    cluster_df = cluster_df(day_df)

    # Membuat judul dashboard
    st.header('Bike Sharing Dashboard', divider='orange')

    # Membuat membuat judul untuk total peminjaman sepeda
    st.subheader('Daily Sharing')

    # Membuat kolom untuk total peminjaman sepeda
    col1, col2, col3 = st.columns(3)

    # Memunculkan nilai total peminjaman sepeda
    with col1:
        total_bike_shared = day_df['total_user'].sum()
        st.metric(label='Total Bike Shared', value=total_bike_shared)

    # Memunculkan nilai total peminjaman sepeda oleh casual user
    with col2:
        total_casual_user_shared = day_df['casual_user'].sum()
        st.metric(label='Total Casual User Use Shared Bike', value=total_casual_user_shared)

    # Memunculkan nilai total peminjaman sepeda oleh registered user
    with col3:
        total_registered_user_shared = day_df['registered_user'].sum()
        st.metric(label='Total Registered User Use Shared Bike', value=total_registered_user_shared)

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Pada hari kerja (workingday), Pada jam berapa peminjaman sepeda paling banyak dan paling sedikit untuk pengguna casual dan registered?'
    st.subheader('Pada jam berapa peminjaman sepeda paling banyak dan paling sedikit untuk pengguna casual dan registered? (Hari Kerja)')

    # Visualisasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
    sns.barplot(x='hour', y='casual_user', data=hour_df_workday, ax=ax[0])
    ax[0].set_title('Casual User')
    ax[0].set_xlabel('Hour')
    ax[0].set_ylabel('Total User')
    ax[0].tick_params(axis='x', labelsize=12)

    sns.barplot(x='hour', y='registered_user', data=hour_df_workday, ax=ax[1])
    ax[1].set_title('Registered User')
    ax[1].set_xlabel('Hour')
    ax[1].set_ylabel('Total User')
    ax[1].tick_params(axis='x', labelsize=12)
    st.pyplot(fig)

    # Mencari waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    max_time_casual, min_time_casual = time_casual_user(hour_df_workday)
    max_time_registered, min_time_registered = time_registered_user(hour_df_workday)

    # Memunculkan waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    st.text('Jam dengan peminjaman paling banyak (Casual): {}'.format(max_time_casual))
    st.text('Jam dengan peminjaman paling sedikit (Casual): {}'.format(min_time_casual))
    st.text('Jam dengan peminjaman paling banyak (Registered): {}'.format(max_time_registered))
    st.text('Jam dengan peminjaman paling sedikit (Registered): {}'.format(min_time_registered))

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Pada hari libur (weekend + libur nasional), Pada jam berapa peminjaman sepeda paling banyak dan paling sedikit untuk pengguna casual dan registered?'
    st.subheader('Pada jam berapa peminjaman sepeda paling banyak dan paling sedikit untuk pengguna casual dan registered? (Hari Libur)')

    # Visualisasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 8))
    sns.barplot(x='hour', y='casual_user', data=hour_df_holiday, ax=ax[0])
    ax[0].set_title('Casual User')
    ax[0].set_xlabel('Hour')
    ax[0].set_ylabel('Total User')
    ax[0].tick_params(axis='x', labelsize=12)

    sns.barplot(x='hour', y='registered_user', data=hour_df_holiday, ax=ax[1])
    ax[1].set_title('Registered User')
    ax[1].set_xlabel('Hour')
    ax[1].set_ylabel('Total User')
    ax[1].tick_params(axis='x', labelsize=12)
    st.pyplot(fig)

    # Mencari waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    max_time_casual, min_time_casual = time_casual_user(hour_df_holiday)
    max_time_registered, min_time_registered = time_registered_user(hour_df_holiday)

    # Memunculkan waktu ketika penggunaan sepeda paling tinggi dan paling rendah
    st.text('Jam dengan peminjaman paling banyak (Casual): {}'.format(max_time_casual))
    st.text('Jam dengan peminjaman paling sedikit (Casual): {}'.format(min_time_casual))
    st.text('Jam dengan peminjaman paling banyak (Registered): {}'.format(max_time_registered))
    st.text('Jam dengan peminjaman paling sedikit (Registered): {}'.format(min_time_registered))

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Pada musim (season) apa peminjaman sepeda paling banyak dan paling sedikit?'
    st.subheader('Pada musim (season) apa peminjaman sepeda paling banyak dan paling sedikit?')

    # Visualisasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#72BCD4"]
    sns.barplot(x='season', y='total_user', data=season_df, palette=colors)
    ax.set_title('Total User Based on Season')
    ax.set_xlabel('Season')
    ax.set_ylabel('Total User')
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Seberapa pengaruh suhu (temp) terhadap jumlah peminjaman sepeda?'
    st.subheader('Seberapa pengaruh suhu (temp) terhadap jumlah peminjaman sepeda?')

    # Visualisasi korelasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(day_df[['temp', 'total_user']].corr(), annot=True, cmap='coolwarm', linewidths=0.5, ax=ax)
    st.pyplot(fig)

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Bagaimana tren peminjaman sepeda setiap bulan?'
    st.subheader('Bagaimana tren peminjaman sepeda setiap bulan?')

    # Visualisasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(figsize=(12, 12))
    sns.lineplot(x='month', y='total_user', hue='year', data=year_month_df, marker='o', markersize=10, linewidth=2.5, palette='colorblind', ax=ax, sort=False)
    ax.set_title('Total User Based on Month')
    ax.set_ylabel('Total User')
    ax.set_xlabel('Month')
    ax.tick_params(axis='x', labelsize=13, labelrotation=45)
    st.pyplot(fig)

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    # Membuat judul untuk pertanyaan 'Berapa total pengguna berdasarkan hasil clustering pada feeling temperature (atemp) dan humidity perhari?'
    st.subheader('Berapa total pengguna berdasarkan hasil clustering pada feeling temperature (atemp) dan humidity perhari?')

    # Visualisasi untuk menjawab pertanyaan tersebut
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(x='cluster', y='total_user', data=cluster_df, ax=ax)
    ax.set_title('Total User Based on Clustering on Atemp and Humidity')
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Total User')
    ax.tick_params(axis='y', labelsize=12)
    st.pyplot(fig)

    # Pemisah antar section
    st.subheader(' ', divider='orange')

    st.caption('Copyright (c) Bike 2023')