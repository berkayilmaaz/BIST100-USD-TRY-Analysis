"""
Created on Sun Mar 24 16:52:40 2024

@author: berkayyilmaz
"""

import pandas as pd
import matplotlib.pyplot as plt

#
bist100_df = pd.read_csv('/Users/berkayyilmaz/Desktop/Bist100_dollar_valuation/data/BİST 100 Geçmiş Verileri (2000.csv')
usd_try_df = pd.read_csv('/Users/berkayyilmaz/Desktop/Bist100_dollar_valuation/data/USD_TRY Geçmiş Verileri 2000.csv')

# Veri tiplerini düzenler
bist100_df['Tarih'] = pd.to_datetime(bist100_df['Tarih'], format='%d.%m.%Y')
usd_try_df['Tarih'] = pd.to_datetime(usd_try_df['Tarih'], format='%d.%m.%Y')
bist100_df['Şimdi'] = bist100_df['Şimdi'].str.replace('.', '').str.replace(',', '.').astype(float)
usd_try_df['Şimdi'] = usd_try_df['Şimdi'].str.replace('.', '').str.replace(',', '.').astype(float)

# BIST 100'ün dolar cinsinden değerini hesaplama
merged_df = pd.merge(bist100_df, usd_try_df, on='Tarih', how='inner', suffixes=('_BIST100', '_USDTRY'))
merged_df['BIST100_USD'] = merged_df['Şimdi_BIST100'] / merged_df['Şimdi_USDTRY']
merged_monthly_df = merged_df.resample('M', on='Tarih').last()

# Yıllık yüzde değişim hesaplamaları
yillik_yuzde_degisimler = []
yillar = []

for i in range(12, len(merged_monthly_df), 12):
    baslangic_degeri = merged_monthly_df['BIST100_USD'].iloc[i-12]
    bitis_degeri = merged_monthly_df['BIST100_USD'].iloc[i]
    yuzde_degisim = ((bitis_degeri - baslangic_degeri) / baslangic_degeri) * 100
    yillik_yuzde_degisimler.append(yuzde_degisim)
    yillar.append(merged_monthly_df.index[i])


fig, axs = plt.subplots(5, 1, figsize=(24, 30))

# Yıllık yüzde değişim grafiği
axs[0].scatter(yillar, yillik_yuzde_degisimler, color='blue', label='Yıllık Yüzde Değişim')
axs[0].plot(yillar, yillik_yuzde_degisimler, color='red', label='Yıllık Yüzde Değişim Eğrisi')
for i in range(len(yillar)):
    axs[0].text(yillar[i], yillik_yuzde_degisimler[i], f"{yillik_yuzde_degisimler[i]:.2f}%", ha='center', va='bottom')
axs[0].set_title('BIST 100 Dolar Cinsinden Yıllık Yüzde Değişim')
axs[0].set_xlabel('Tarih')
axs[0].set_ylabel('Yüzde Değişim')
axs[0].grid(True)

# Dolar Kuru ve BIST 100 İlişkisi
axs[1].scatter(merged_df['Şimdi_USDTRY'], merged_df['BIST100_USD'], color='purple', alpha=0.5)
axs[1].set_title('Dolar Kuru ve BIST 100 İlişkisi')
axs[1].set_xlabel('Dolar Kuru (USD/TRY)')
axs[1].set_ylabel('BIST 100 (USD)')
axs[1].grid(True)

# Hareketli Ortalama
axs[2].plot(merged_monthly_df.index, merged_monthly_df['BIST100_USD'], label='BIST 100 (USD)', color='blue')
axs[2].plot(merged_monthly_df.index, merged_monthly_df['BIST100_USD'].rolling(window=12).mean(), label='12 Aylık Hareketli Ortalama', color='red')
axs[2].set_title('BIST 100 Dolar Cinsinden Değer ve Hareketli Ortalama')
axs[2].set_xlabel('Tarih')
axs[2].set_ylabel('Değer (USD)')
axs[2].legend()
axs[2].grid(True)


# Aylık En Yüksek ve En Düşük BIST 100 Değerleri ve En Yüksek Farkın Vurgulandığı Grafik
monthly_usd_try_high = usd_try_df.groupby(usd_try_df['Tarih'].dt.to_period('M'))['Şimdi'].max()
monthly_usd_try_low = usd_try_df.groupby(usd_try_df['Tarih'].dt.to_period('M'))['Şimdi'].min()

bist100_monthly_high = merged_df.groupby(merged_df['Tarih'].dt.to_period('M'))['Şimdi_BIST100'].max()
bist100_monthly_low = merged_df.groupby(merged_df['Tarih'].dt.to_period('M'))['Şimdi_BIST100'].min()

monthly_bist_high_usd = bist100_monthly_high / monthly_usd_try_low
monthly_bist_low_usd = bist100_monthly_low / monthly_usd_try_high

monthly_diff_usd = monthly_bist_high_usd - monthly_bist_low_usd
monthly_diff_percent = (monthly_diff_usd / monthly_bist_low_usd) * 100
max_diff_per_year = monthly_diff_percent.groupby(monthly_diff_percent.index.year).nlargest(1).reset_index(level=0, drop=True)

axs[3].plot(monthly_bist_high_usd.index.to_timestamp(), monthly_bist_high_usd, label='Aylık En Yüksek BIST 100 (USD)', color='green')
axs[3].plot(monthly_bist_low_usd.index.to_timestamp(), monthly_bist_low_usd, label='Aylık En Düşük BIST 100 (USD)', color='red')
axs[3].fill_between(monthly_bist_high_usd.index.to_timestamp(), monthly_bist_low_usd, monthly_bist_high_usd, color='grey', alpha=0.3)

for date in max_diff_per_year.index.to_timestamp():
    axs[3].scatter(date, monthly_bist_high_usd[date], color='orange', zorder=5)
    axs[3].scatter(date, monthly_bist_low_usd[date], color='orange', zorder=5)
    axs[3].text(date, monthly_bist_high_usd[date], f"{monthly_diff_percent[date]:.2f}%", ha='center', va='bottom', color='black')

axs[3].set_title('Aylık En Yüksek ve En Düşük BIST 100 Değerleri ve En Yüksek Farkın Vurgulandığı Grafik')
axs[3].set_xlabel('Tarih')
axs[3].set_ylabel('BIST 100 Değeri (USD)')
axs[3].legend()
axs[3].grid(True)
axs[3].xaxis.set_major_locator(plt.MultipleLocator(365))
axs[3].xaxis.set_minor_locator(plt.MultipleLocator(30))
fig.autofmt_xdate()

# Yıllık Ortalama En Yüksek 3 BIST 100 USD Farkı grafiği
max_3_diffs_per_year = monthly_diff_percent.groupby(monthly_diff_percent.index.year).nlargest(3)
yearly_avg_diffs = max_3_diffs_per_year.groupby(level=0).mean()

axs[4].bar(yearly_avg_diffs.index, yearly_avg_diffs.values, color='purple')
axs[4].set_title('Yıllık Ortalama En Yüksek 3 BIST 100 USD Farkı')
axs[4].set_xlabel('Yıl')
axs[4].set_ylabel('Ortalama Yüzde Farkı (%)')
axs[4].grid(True)

plt.tight_layout()
plt.show()

