from instabot import Bot
import schedule
import time
import requests
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

class InstagramBot:
    def __init__(self):
        self.bot = None
        self.logged_in = False
    
    def login(self, username, password):
        """Instagram hesabına giriş yapar"""
        try:
            self.bot = Bot()
            self.bot.login(username=username, password=password)
            self.logged_in = True
            return True
        except Exception as e:
            print(f"Giriş hatası: {e}")
            return False

    def share_post(self, image_path, caption):
        """Gönderi paylaşır"""
        if self.logged_in:
            try:
                self.bot.upload_photo(image_path, caption=caption)
                print(f"Gönderi paylaşıldı: {datetime.now()}")
            except Exception as e:
                print(f"Paylaşım hatası: {e}")

    def reply_to_messages(self):
        """Gelen DM'lere otomatik yanıt verir"""
        if self.logged_in:
            messages = self.bot.get_messages()
            for message in messages:
                if not message['answered']:
                    self.bot.send_message(
                        "Merhaba! Şu anda müsait değilim. En kısa sürede dönüş yapacağım.",
                        message['user_id']
                    )

class BotGUI:
    def __init__(self):
        self.bot = InstagramBot()
        self.window = tk.Tk()
        self.window.title("Instagram Bot")
        self.window.geometry("400x300")
        
        # Kullanıcı adı alanı
        tk.Label(self.window, text="Kullanıcı Adı:").pack(pady=5)
        self.username_entry = tk.Entry(self.window)
        self.username_entry.pack(pady=5)
        
        # Şifre alanı
        tk.Label(self.window, text="Şifre:").pack(pady=5)
        self.password_entry = tk.Entry(self.window, show="*")
        self.password_entry.pack(pady=5)
        
        # Giriş butonu
        self.login_button = tk.Button(
            self.window, 
            text="Giriş Yap",
            command=self.login
        )
        self.login_button.pack(pady=10)
        
        # Paylaşım butonu
        self.share_button = tk.Button(
            self.window,
            text="Gönderi Paylaş",
            command=self.share_post,
            state="disabled"
        )
        self.share_button.pack(pady=10)
        
        # Otomatik yanıtlama butonu
        self.auto_reply_button = tk.Button(
            self.window,
            text="Otomatik Yanıtlamayı Başlat",
            command=self.start_auto_reply,
            state="disabled"
        )
        self.auto_reply_button.pack(pady=10)

    def login(self):
        """Giriş işlemini gerçekleştirir"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if self.bot.login(username, password):
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            self.share_button["state"] = "normal"
            self.auto_reply_button["state"] = "normal"
        else:
            messagebox.showerror("Hata", "Giriş başarısız!")

    def share_post(self):
        """Gönderi paylaşım penceresini açar"""
        # Burada gönderi paylaşımı için yeni bir pencere açılabilir
        pass

    def start_auto_reply(self):
        """Otomatik yanıtlamayı başlatır"""
        schedule.every(10).minutes.do(self.bot.reply_to_messages)
        messagebox.showinfo("Bilgi", "Otomatik yanıtlama başlatıldı!")

    def run(self):
        """Uygulamayı başlatır"""
        self.window.mainloop()

if __name__ == "__main__":
    app = BotGUI()
    app.run()
