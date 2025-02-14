import tkinter as tk
from tkinter import ttk, messagebox
from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

class SahteVeriUretici:
    def __init__(self):
        # Faker kütüphanesi için Türkçe dil ayarı
        self.fake = Faker('tr_TR')
        
        # Ana pencere oluşturma
        self.pencere = tk.Tk()
        self.pencere.title("Sahte Veri Üretici")
        self.pencere.geometry("800x600")
        
        # Veri seti adı girişi
        self.dataset_frame = ttk.LabelFrame(self.pencere, text="Veri Seti Bilgileri")
        self.dataset_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(self.dataset_frame, text="Veri Seti Adı:").pack(pady=5)
        self.dataset_adi_entry = ttk.Entry(self.dataset_frame)
        self.dataset_adi_entry.pack(pady=5)

        # Sütun sayısı girişi
        ttk.Label(self.dataset_frame, text="Sütun Sayısı:").pack(pady=5)
        self.sutun_sayisi_entry = ttk.Entry(self.dataset_frame)
        self.sutun_sayisi_entry.pack(pady=5)

        # Sütun bilgileri için buton
        self.sutun_button = ttk.Button(self.dataset_frame, text="Sütunları Ayarla", command=self.sutun_ayarla)
        self.sutun_button.pack(pady=10)

        # Sütun bilgileri için frame
        self.sutunlar_frame = ttk.LabelFrame(self.pencere, text="Sütun Bilgileri")
        self.sutunlar_frame.pack(pady=10, padx=10, fill="x", expand=True)

        # Kayıt sayısı girişi
        self.kayit_frame = ttk.LabelFrame(self.pencere, text="Kayıt Bilgileri")
        self.kayit_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(self.kayit_frame, text="Kayıt Sayısı:").pack(pady=5)
        self.kayit_entry = ttk.Entry(self.kayit_frame)
        self.kayit_entry.pack(pady=5)
        self.kayit_entry.insert(0, "100")

        # Üret butonu
        self.uret_button = ttk.Button(self.pencere, text="Veri Üret", command=self.ozel_veri_uret)
        self.uret_button.pack(pady=10)

        # Sonuç alanı
        self.sonuc_text = tk.Text(self.pencere, height=10, width=80)
        self.sonuc_text.pack(pady=10, padx=10)

        self.sutun_bilgileri = []
        self.veri_tipleri = [
            "İsim", "Soyisim", "Email", "Telefon", "Adres", "Şehir",
            "Tarih", "Sayı", "Şirket", "Meslek", "Metin"
        ]

    def sutun_ayarla(self):
        """Sütun bilgilerini girmek için alanlar oluşturur"""
        try:
            # Mevcut sütun alanlarını temizle
            for widget in self.sutunlar_frame.winfo_children():
                widget.destroy()

            sutun_sayisi = int(self.sutun_sayisi_entry.get())
            self.sutun_bilgileri = []

            for i in range(sutun_sayisi):
                sutun_frame = ttk.Frame(self.sutunlar_frame)
                sutun_frame.pack(pady=5, fill="x")

                # Sütun adı girişi
                ttk.Label(sutun_frame, text=f"Sütun {i+1} Adı:").pack(side="left", padx=5)
                sutun_adi = ttk.Entry(sutun_frame, width=20)
                sutun_adi.pack(side="left", padx=5)

                # Veri tipi seçimi
                ttk.Label(sutun_frame, text="Veri Tipi:").pack(side="left", padx=5)
                veri_tipi = ttk.Combobox(sutun_frame, values=self.veri_tipleri, width=15)
                veri_tipi.pack(side="left", padx=5)

                self.sutun_bilgileri.append((sutun_adi, veri_tipi))

        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sütun sayısı giriniz!")

    def ozel_veri_uret(self):
        """Kullanıcının belirlediği formatta veri üretir"""
        try:
            sayi = int(self.kayit_entry.get())
            if sayi <= 0:
                messagebox.showerror("Hata", "Kayıt sayısı 0'dan büyük olmalıdır!")
                return

            veriler = []
            for _ in range(sayi):
                kayit = {}
                for sutun_adi, veri_tipi in self.sutun_bilgileri:
                    ad = sutun_adi.get()
                    tip = veri_tipi.get()
                    
                    # Veri tipine göre değer üret
                    if tip == "İsim":
                        deger = self.fake.first_name()
                    elif tip == "Soyisim":
                        deger = self.fake.last_name()
                    elif tip == "Email":
                        deger = self.fake.email()
                    elif tip == "Telefon":
                        deger = self.fake.phone_number()
                    elif tip == "Adres":
                        deger = self.fake.address()
                    elif tip == "Şehir":
                        deger = self.fake.city()
                    elif tip == "Tarih":
                        deger = self.fake.date()
                    elif tip == "Sayı":
                        deger = random.randint(1, 1000)
                    elif tip == "Şirket":
                        deger = self.fake.company()
                    elif tip == "Meslek":
                        deger = self.fake.job()
                    elif tip == "Metin":
                        deger = self.fake.text(max_nb_chars=50)
                    else:
                        deger = "Belirsiz"
                    
                    kayit[ad] = deger
                veriler.append(kayit)

            df = pd.DataFrame(veriler)
            
            # Sonuçları göster ve CSV olarak kaydet
            self.sonuc_text.delete(1.0, tk.END)
            self.sonuc_text.insert(tk.END, df.head().to_string())
            
            dataset_adi = self.dataset_adi_entry.get() or "veri_seti"
            dosya_adi = f"{dataset_adi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(dosya_adi, index=False, encoding='utf-8-sig')
            messagebox.showinfo("Başarılı", f"Veriler {dosya_adi} dosyasına kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Bir hata oluştu: {str(e)}")

    def baslat(self):
        """Uygulamayı başlatır"""
        self.pencere.mainloop()

if __name__ == "__main__":
    uygulama = SahteVeriUretici()
    uygulama.baslat()
