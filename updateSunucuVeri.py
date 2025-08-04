# main_app_script_with_user_weather_function.py

import socket
import time
import threading
import logging
from datetime import datetime
import requests # Hava durumu API'si için

# Orijinal DatabaseManager'ı import et
from commonModules.dbManage import DatabaseManager # Bu dosyanın var olduğunu varsayıyoruz

# psycopg2.OperationalError'ı yakalamak için import edelim
try:
    from psycopg2 import OperationalError as Psycopg2OperationalError
except ImportError:
    class Psycopg2OperationalError(Exception): # Mock için
        pass

# --- Yapılandırma ---
SOCKET_HOST = '0.0.0.0'
SOCKET_PORT = 4141
DB_UPDATE_INTERVAL_SECONDS = 10

# Hava Durumu için yapılandırma
API_CITY_NAME = "Konya"  # Hava durumu verisi çekilecek şehir (kullanıcının fonksiyonu için)
DEFAULT_WEATHER_FALLBACK = 0    # Socket ve API'den hava durumu gelmezse kullanılacak varsayılan değer
                                # (Kullanıcının fonksiyonu hata durumunda 0 dönüyor)
DB_PARAMS = {
    'dbname': 'bsc',
    'user': 'postgres',
    'password': '2580',
    'host': 'localhost'
}

# Logger yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(module)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Global Değişkenler ---
g_received_socket_data = {
    "timestamp_ms": None,
    "weather": None,
    "is_new": False
}
g_socket_data_lock = threading.Lock()
g_stop_event = threading.Event()

def get_system_timestamp_ms():
    """Şu anki sistem zaman damgasını milisaniye cinsinden döndürür."""
    return int(datetime.now().timestamp() * 1000)

# --- Kullanıcının Sağladığı Hava Durumu Fonksiyonu (Uyarlanmış Hali) ---
def get_weather_from_user_function(city_name_param: str) -> int:
    """
    Belirtilen şehire göre OpenWeatherMap API'sinden hava durumu çeker.
    Kullanıcının sağladığı fonksiyon temel alınarak uyarlanmıştır.
    """
    # API anahtarı ve URL doğrudan fonksiyon içinde tanımlanmış (kullanıcının kodundaki gibi)
    API = "51018b60257b50207fc63de7c53af5e1" # Kullanıcının verdiği API key
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
    URL = BASE_URL + "appid=" + API + "&q=" + city_name_param
    
    weather_celcius = DEFAULT_WEATHER_FALLBACK # Hata durumunda varsayılan

    try:
        response = requests.get(URL, timeout=10) # 10 saniye timeout
        response.raise_for_status() # HTTP hataları için exception fırlatır (4xx, 5xx)
        
        weather_condition = response.json()
        
        # Kullanıcının kodundaki "cod" != "404" kontrolü raise_for_status() ile zaten sağlanmış olur.
        # Eğer "cod" alanı JSON içinde yine de kontrol edilmek isteniyorsa:
        # if "cod" in weather_condition and str(weather_condition["cod"]) == "200":
        if "main" in weather_condition and "temp" in weather_condition["main"]:
            temperature_kelvin = weather_condition["main"]["temp"]
            # Diğer bilgiler (description, pressure, country) loglanabilir veya kullanılabilir.
            # description = weather_condition.get("weather", [{}])[0].get("description", "N/A")
            # logging.info(f"API'den {city_name_param} için ham veri: Sıcaklık={temperature_kelvin}K, Açıklama={description}")

            weather_celcius = float(temperature_kelvin) - 273.15
            logging.info(f"API'den {city_name_param} için hava durumu alındı: {int(weather_celcius)}°C")
        else:
            logging.warning(f"API yanıtında ({city_name_param}) beklenen 'main' veya 'temp' alanı bulunamadı. Yanıt: {weather_condition}")
            # weather_celcius varsayılan değerde kalır (DEFAULT_WEATHER_FALLBACK)

    except requests.exceptions.HTTPError as http_err:
        logging.error(f"API isteğinde HTTP hatası ({city_name_param}): {http_err} - Yanıt: {response.text if 'response' in locals() else 'Yanıt yok'}")
    except requests.exceptions.RequestException as req_err:
        # Bağlantı hatası, timeout vb. genel hatalar
        logging.error(f"API isteğinde genel bir hata ({city_name_param}): {req_err}")
    except ValueError as json_err: # JSON parse hatası
        logging.error(f"API yanıtı JSON parse edilemedi ({city_name_param}): {json_err}")
    except Exception as ex:
        # Kullanıcının orijinal fonksiyonundaki genel hata yakalama
        logging.error(f"get_weather_from_user_function içinde beklenmedik hata ({city_name_param}): {ex}")
        # weather_celcius zaten DEFAULT_WEATHER_FALLBACK olarak ayarlı

    return int(weather_celcius)


def socket_listener_thread_function():
    """
    4141 portunu dinler, "timestamp,weather" formatında veri bekler.
    Gelen veriyi işleyip global bir değişkende saklar.
    """
    global g_received_socket_data
    server_socket = None
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((SOCKET_HOST, SOCKET_PORT))
        server_socket.listen(1)
        logging.info(f"Socket sunucusu {SOCKET_HOST}:{SOCKET_PORT} üzerinde dinlemede.")
        server_socket.settimeout(1.0)

        while not g_stop_event.is_set():
            try:
                conn, addr = server_socket.accept()
                logging.info(f"Socket bağlantısı kabul edildi: {addr}")
                with conn:
                    data_bytes = conn.recv(1024)
                    if data_bytes:
                        received_str = data_bytes.decode('utf-8').strip()
                        logging.info(f"Socket'tan ham veri alındı: '{received_str}'")
                        parts = received_str.split(',')
                        if len(parts) == 2:
                            try:
                                ts_from_socket_str = parts[0].strip()
                                weather_from_socket_str = parts[1].strip()

                                ts_value = float(ts_from_socket_str)
                                # Zaman damgasının saniye mi milisaniye mi olduğunu anlamak için basit kontrol
                                parsed_timestamp_ms = int(ts_value * 1000) if ts_value < 10**11 else int(ts_value)
                                parsed_weather = int(weather_from_socket_str) # Hava durumu int olmalı

                                with g_socket_data_lock:
                                    g_received_socket_data["timestamp_ms"] = parsed_timestamp_ms
                                    g_received_socket_data["weather"] = parsed_weather
                                    g_received_socket_data["is_new"] = True
                                logging.info(f"Socket verisi başarıyla işlendi: ZamanDamgası={parsed_timestamp_ms}ms, HavaDurumu={parsed_weather}")
                                conn.sendall(b"VERI_ALINDI_ISLENDI\n")
                            except ValueError:
                                logging.error(f"Socket verisi '{received_str}' sayısal değere çevrilemedi.")
                                conn.sendall(b"HATA_VERI_FORMATI_SAYISAL_DEGIL\n")
                            except Exception as e_parse:
                                logging.error(f"Socket verisi parse edilirken genel hata: {e_parse}")
                                conn.sendall(b"HATA_VERI_ISLENEMEDI\n")
                        else:
                            logging.warning(f"Socket'tan beklenmedik formatta veri: '{received_str}'. 'timestamp,weather' bekleniyordu.")
                            conn.sendall(b"HATA_BEKLENMEDIK_FORMAT\n")
            except socket.timeout:
                continue # g_stop_event kontrolü için normal
            except Exception as e_conn:
                if not g_stop_event.is_set():
                    logging.error(f"Socket bağlantı/veri alma hatası: {e_conn}")
                time.sleep(0.1) # Hata sonrası kısa bekleme
    except OSError as e_bind: # Adres zaten kullanılıyor gibi hatalar için
        logging.critical(f"Socket {SOCKET_HOST}:{SOCKET_PORT} adresine bağlanamadı: {e_bind}.")
    except Exception as e_server:
        if not g_stop_event.is_set():
            logging.error(f"Socket sunucu ana döngü hatası: {e_server}")
    finally:
        if server_socket:
            server_socket.close()
        logging.info("Socket sunucusu kapatıldı.")


def database_updater_thread_function():
    """
    Periyodik olarak zaman damgası ve hava durumu ile veritabanını günceller.
    Veri kaynağı: Socket -> API (kullanıcının fonksiyonu) -> Varsayılan.
    Orijinal DatabaseManager kullanılır.
    """
    global g_received_socket_data

    while not g_stop_event.is_set():
        timestamp_to_use = None
        weather_to_use = None
        source_timestamp = "bilinmiyor"
        source_weather = "bilinmiyor"
        
        socket_data_processed = False
        with g_socket_data_lock:
            if g_received_socket_data["is_new"]:
                timestamp_to_use = g_received_socket_data["timestamp_ms"]
                weather_to_use = g_received_socket_data["weather"]
                g_received_socket_data["is_new"] = False # Veriyi tüket
                source_timestamp = "socket"
                source_weather = "socket"
                socket_data_processed = True
        
        if not socket_data_processed:
            # Socket'tan yeni veri gelmedi, sistem saatini kullan
            timestamp_to_use = get_system_timestamp_ms()
            source_timestamp = "sistem"
            
            # Hava durumu için kullanıcının sağladığı fonksiyonu dene
            logging.info(f"Socket'tan hava durumu verisi yok. {API_CITY_NAME} için API'den (kullanıcı fonksiyonu) çekilecek.")
            api_weather = get_weather_from_user_function(API_CITY_NAME)
            
            # Kullanıcının fonksiyonu hata durumunda zaten DEFAULT_WEATHER_FALLBACK (0) dönecek şekilde ayarlandı.
            weather_to_use = api_weather 
            if weather_to_use != DEFAULT_WEATHER_FALLBACK: # Eğer varsayılan değilse, API'den gelmiştir.
                 source_weather = f"API ({API_CITY_NAME} - kullanıcı fonksiyonu)"
            else:
                 # Bu durum, API'den 0 gelmiş olabileceği gibi, bir hata sonucu da 0 dönmüş olabilir.
                 # Fonksiyon içindeki loglar daha detaylı bilgi verecektir.
                 source_weather = f"varsayılan veya API hatası ({API_CITY_NAME} - kullanıcı fonksiyonu)"
                 logging.warning(f"Kullanıcının hava durumu fonksiyonu ({API_CITY_NAME}) {weather_to_use} değerini döndürdü.")

        logging.info(f"Veritabanı güncellenecek: ZamanDamgası={timestamp_to_use}ms (Kaynak: {source_timestamp}), HavaDurumu={weather_to_use} (Kaynak: {source_weather})")

        try:
            # Orijinal DatabaseManager kullanılıyor.
            with DatabaseManager(dbname=DB_PARAMS['dbname'],
                                 user=DB_PARAMS['user'],
                                 password=DB_PARAMS['password'],
                                 host=DB_PARAMS['host']) as db_manager:
                db_manager.updateSunucuVeri(timestamp_value=timestamp_to_use,
                                            weather=weather_to_use)
        except Psycopg2OperationalError as e_db_conn:
            logging.error(f"Veritabanı BAĞLANTI HATASI: {e_db_conn}. Güncelleme yapılamadı.")
        except Exception as e_db_update:
            logging.error(f"Veritabanı güncelleme sırasında genel bir HATA: {e_db_update}")
        
        # Bir sonraki döngü için bekle veya durdurma sinyalini kontrol et
        if g_stop_event.wait(DB_UPDATE_INTERVAL_SECONDS):
            break # Durdurma sinyali geldiyse döngüden çık

if __name__ == "__main__":
    logging.info("Ana Uygulama Başlatılıyor...")
    print(f"Hava durumu API'si (kullanıcı fonksiyonu) için şehir: {API_CITY_NAME}")
    print(f"Eğer 'requests' kütüphanesi kurulu değilse, 'pip install requests' ile kurun.")
    print(f"Kullanılan API Anahtarı (fonksiyon içinde): ...{('51018b60257b50207fc63de7c53af5e1')[-6:]}") # API key'in son 6 hanesi

    socket_thread = threading.Thread(target=socket_listener_thread_function, name="SocketDinleyiciThread", daemon=True)
    db_updater_thread = threading.Thread(target=database_updater_thread_function, name="VeritabaniGuncelleyiciThread", daemon=True)

    socket_thread.start()
    db_updater_thread.start()

    logging.info("Socket dinleyici ve veritabanı güncelleyici thread'leri başlatıldı.")
    print("Uygulama çalışıyor. Çıkmak için Ctrl+C tuşlarına basın.")

    try:
        while not g_stop_event.is_set():
            if not socket_thread.is_alive() and not g_stop_event.is_set():
                logging.critical("SocketDinleyiciThread beklenmedik şekilde sonlandı!")
                g_stop_event.set()
            if not db_updater_thread.is_alive() and not g_stop_event.is_set():
                logging.critical("VeritabaniGuncelleyiciThread beklenmedik şekilde sonlandı!")
                g_stop_event.set()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Ctrl+C algılandı. Uygulama durduruluyor...")
    finally:
        g_stop_event.set()
        
        logging.info("Thread'lerin sonlanması bekleniyor (en fazla 5 saniye)...")
        if socket_thread.is_alive():
            socket_thread.join(timeout=5)
        if db_updater_thread.is_alive():
            db_updater_thread.join(timeout=5)
        
        logging.info("Uygulama başarıyla kapatıldı.")
