import socket
from datetime import datetime
from yamlParser import YamlHandler

class ListenerServer:
    def __init__(self):
        self.identity = YamlHandler('configs/identity.yaml')
        self.host = self.identity.data['ip']
        self.port = self.identity.data['weatherPort']
        self.weather = 30
        now = datetime.now()
        self.hour =  now.hour
        self.minute = now.minute
        self.setConnection()

    def setConnection(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)  # Maksimum 5 istemciyi sıraya alabilir
            print(f"Sunucu {self.host}:{self.port} üzerinde dinliyor...")
        except Exception as e:
            print(f'Hata: {e}')
            if self.server_socket is not None:
                self.close()
            


    def handle_client(self, conn, addr):
        print(f"Bağlantı sağlandı: {addr}")
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:  # Bağlantı kesildiğinde döngüden çık
                    print("Bağlantı kapatıldı.")
                    break
                print(f"Alınan veri: {data}")
                splittedData = data.split(',')
                for i in range(len(splittedData)):
                    splittedData[i] = int(splittedData[i].strip())
                self.weather = splittedData[0]
                self.hour = splittedData[1]
                self.minute = splittedData[2]
        except socket.error as e:
            print(f"Veri alımı sırasında hata oluştu: {e}")
        finally:
            conn.close()

    def start(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                self.handle_client(conn, addr)
        except KeyboardInterrupt:
            print("Sunucu kapatılıyor...")
            self.close()

    def close(self):
        self.server_socket.close()
        print("Sunucu kapatıldı.")

if __name__ == '__main__':
    srv = ListenerServer()
    srv.start()