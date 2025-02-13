import folium
import random
import tkinter as tk
from tkinter import messagebox
import requests
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import os
import webbrowser

class SehirTahminOyunu:
    def __init__(self):
        # Ana pencere oluşturma
        self.pencere = tk.Tk()
        self.pencere.title("Şehir Tahmin Oyunu 🗺")
        self.pencere.geometry("1024x768")  # Pencere boyutunu büyüttük
        
        # Oyun değişkenleri
        self.puan = 0
        self.kalan_sure = 120  # Süreyi 120 saniyeye çıkardık
        self.kalan_tahmin = 3  # Her şehir için 3 tahmin hakkı
        self.hedef_sehir = None
        self.hedef_koordinatlar = None
        
        # Webview için
        self.webview = None
        
        # Türkiye'deki büyük şehirler ve koordinatları
        self.sehirler = {
            "İstanbul": (41.0082, 28.9784),
            "Ankara": (39.9334, 32.8597),
            "İzmir": (38.4189, 27.1287),
            "Antalya": (36.8841, 30.7056),
            "Bursa": (40.1885, 29.0610),
            "Adana": (37.0000, 35.3213),
            "Konya": (37.8714, 32.4846),
            "Gaziantep": (37.0662, 37.3833),
            "Mersin": (36.8121, 34.6339),
            "Diyarbakır": (37.9144, 40.2306)
        }
        
        self.arayuz_olustur()
        
    def arayuz_olustur(self):
        # Üst bilgi paneli
        self.bilgi_panel = tk.Frame(self.pencere)
        self.bilgi_panel.pack(fill=tk.X, padx=10, pady=5)
        
        # Puan, süre ve kalan tahmin göstergeleri
        self.puan_label = tk.Label(self.bilgi_panel, text=f"Puan: {self.puan}", font=("Arial", 12, "bold"))
        self.puan_label.pack(side=tk.LEFT, padx=5)
        
        self.tahmin_label = tk.Label(self.bilgi_panel, text=f"Kalan Tahmin: {self.kalan_tahmin}", font=("Arial", 12))
        self.tahmin_label.pack(side=tk.LEFT, padx=5)
        
        self.sure_label = tk.Label(self.bilgi_panel, text=f"Süre: {self.kalan_sure}", font=("Arial", 12, "bold"))
        self.sure_label.pack(side=tk.RIGHT, padx=5)
        
        # Harita gösterimi için frame
        self.harita_frame = tk.Frame(self.pencere)
        self.harita_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # HTML görüntüleyici
        self.harita_label = tk.Label(self.harita_frame, 
                                   text="Harita yükleniyor...", 
                                   font=("Arial", 14))
        self.harita_label.pack(pady=20)
        
        # Haritayı tarayıcıda aç butonu
        self.harita_btn = tk.Button(self.harita_frame, 
                                  text="Haritayı Göster", 
                                  command=self.harita_ac,
                                  font=("Arial", 12))
        self.harita_btn.pack(pady=10)
        
        # İpucu butonu
        self.ipucu_btn = tk.Button(self.harita_frame, 
                                 text="İpucu Al (-50 puan)", 
                                 command=self.ipucu_goster, 
                                 font=("Arial", 10))
        self.ipucu_btn.pack(pady=5)
        
        # Tahmin girişi
        self.tahmin_frame = tk.Frame(self.pencere)
        self.tahmin_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.tahmin_entry = tk.Entry(self.tahmin_frame, font=("Arial", 12))
        self.tahmin_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.tahmin_btn = tk.Button(self.tahmin_frame, 
                                  text="Tahmin Et", 
                                  command=self.tahmin_kontrol, 
                                  font=("Arial", 12, "bold"))
        self.tahmin_btn.pack(side=tk.RIGHT, padx=5)
        
        # Enter tuşu ile tahmin yapma
        self.tahmin_entry.bind('<Return>', lambda event: self.tahmin_kontrol())
        
        # Oyunu başlat
        self.oyun_baslat()
        
    def oyun_baslat(self):
        """Yeni oyun başlatır"""
        self.puan = 0
        self.kalan_sure = 120
        self.kalan_tahmin = 3
        self.yeni_sehir_sec()
        self.sure_guncelle()
        
    def yeni_sehir_sec(self):
        """Rastgele yeni bir hedef şehir seçer"""
        self.hedef_sehir = random.choice(list(self.sehirler.keys()))
        self.hedef_koordinatlar = self.sehirler[self.hedef_sehir]
        self.kalan_tahmin = 3
        self.tahmin_label.config(text=f"Kalan Tahmin: {self.kalan_tahmin}")
        self.harita_goster()
        
    def harita_goster(self):
        """Seçilen şehrin haritasını gösterir"""
        m = folium.Map(location=self.hedef_koordinatlar, zoom_start=12)
        self.harita_html = f"harita_{random.randint(1000,9999)}.html"
        m.save(self.harita_html)
        self.harita_label.config(text="Harita hazır! 'Haritayı Göster' butonuna tıklayın.")
        
    def harita_ac(self):
        """Haritayı varsayılan tarayıcıda açar"""
        webbrowser.open(f"file://{os.path.abspath(self.harita_html)}")
        
    def ipucu_goster(self):
        """İpucu gösterir ve puan düşer"""
        if self.puan >= 50:
            self.puan -= 50
            self.puan_label.config(text=f"Puan: {self.puan}")
            ipucu = f"Bu şehir {self.hedef_sehir[0]} harfi ile başlıyor."
            messagebox.showinfo("İpucu", ipucu)
        else:
            messagebox.showwarning("Yetersiz Puan", "İpucu almak için en az 50 puana ihtiyacınız var!")
        
    def tahmin_kontrol(self):
        """Kullanıcının tahminini kontrol eder"""
        if self.kalan_tahmin <= 0:
            messagebox.showinfo("Uyarı", "Tahmin hakkınız kalmadı! Yeni şehir seçiliyor...")
            self.yeni_sehir_sec()
            return
            
        tahmin = self.tahmin_entry.get().strip().lower()
        dogru_cevap = self.hedef_sehir.lower()
        
        if tahmin == dogru_cevap:
            bonus = self.kalan_tahmin * 50  # Kalan tahmin hakkına göre bonus
            kazanilan_puan = 100 + bonus
            self.puan += kazanilan_puan
            messagebox.showinfo("Tebrikler!", 
                              f"Doğru tahmin! +{kazanilan_puan} puan kazandınız!\n"
                              f"(100 + {bonus} bonus puan)")
            self.yeni_sehir_sec()
        else:
            self.kalan_tahmin -= 1
            uzaklik = geodesic(self.hedef_koordinatlar, 
                             self.sehirler[self.hedef_sehir]).kilometers
            self.puan -= int(uzaklik / 20)  # Uzaklığa göre puan kesintisini azalttık
            
            if self.kalan_tahmin > 0:
                messagebox.showwarning("Yanlış!", 
                                     f"Yanlış tahmin! {self.kalan_tahmin} hakkınız kaldı.")
            else:
                messagebox.showwarning("Yanlış!", 
                                     f"Yanlış tahmin! Doğru cevap: {self.hedef_sehir}")
                self.yeni_sehir_sec()
        
        self.puan_label.config(text=f"Puan: {self.puan}")
        self.tahmin_label.config(text=f"Kalan Tahmin: {self.kalan_tahmin}")
        self.tahmin_entry.delete(0, tk.END)
        
    def sure_guncelle(self):
        """Süreyi günceller ve kontrol eder"""
        if self.kalan_sure > 0:
            self.kalan_sure -= 1
            self.sure_label.config(text=f"Süre: {self.kalan_sure}")
            self.pencere.after(1000, self.sure_guncelle)
        else:
            messagebox.showinfo("Oyun Bitti!", f"Süre doldu! Toplam puanınız: {self.puan}")
            self.oyun_baslat()

if __name__ == "__main__":
    oyun = SehirTahminOyunu()
    oyun.pencere.mainloop()
