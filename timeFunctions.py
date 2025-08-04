import time
import datetime
from commonModules.dbManage import DatabaseManager
from datetime import datetime
import os

class Time_R:  
    def __init__(self, db):
        self.db = db
        self.connection = False
        self.localTime = False
        self.timeBuffer = self.getDbTime()
        self.checkLocalTime()
        self.checkConnection()
        
    getDbTime = lambda self: db.fetch_counts_and_timestamp()[0]
    getLocalTime = lambda self: time.time()
    timestampToDatetime = lambda self, tmstp: datetime.fromtimestamp(tmstp).strftime('%Y-%m-%d %H:%M:%S')

    def log_message(self, message):
        """Hata veya bilgi mesajını log dosyasına yazdırır."""
        log_dir = "configs"
        os.makedirs(log_dir, exist_ok=True)  # /logs/ klasörünü oluştur (eğer yoksa)
        log_file = os.path.join(log_dir, "time_r_logs.log")  # .log uzantısı kullanıyoruz
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def checkConnection(self):
        time.sleep(180)  # 3 dakika bekle
        if self.getDbTime() - self.timeBuffer == 0:
            message = "Db bağlantısı yok: Veritabanı saati güncellenmedi."
            print(message)
            self.log_message(message)
            self.connection = False
            return False
        else: 
            message = "Db bağlantısı doğru: Veritabanı saati güncelleniyor."
            print(message)
            self.log_message(message)
            self.connection = True
            return True
                    
    def checkLocalTime(self):
        if int(self.getLocalTime()) - int(self.timeBuffer) > 9999999:
            message = "Yerel zaman hatası: Yerel saat ile veritabanı saatinde büyük bir uyumsuzluk var."
            print(message)
            self.log_message(message)
            self.localTime = False
            return False
        else:
            message = "Yerel zaman doğru: Saatler senkronize."
            print(message)
            self.log_message(message)
            self.localTime = True
            return True

db = DatabaseManager()
timer = Time_R(db)

# Eğer her iki kontrol de başarılıysa "Her şey yolunda" mesajı yazdırılır.
if timer.connection and timer.localTime:
    timer.log_message("Her şey yolunda: Veritabanı bağlantısı ve yerel zaman doğru.")
