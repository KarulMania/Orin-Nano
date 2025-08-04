import fcntl
import time
from datetime import datetime
import os
import json

def reset_daily_count(file_path):
    with open(file_path, 'r+') as file:
        fcntl.flock(file, fcntl.LOCK_EX)  # Dosyayı kilitle (exclusive lock)

        # Mevcut değerleri al
        lines = file.readlines()
        totalCount = int(lines[1].strip())

        # İlk satırı sıfırla ve dosyaya yaz
        file.seek(0)
        file.write("0\n")
        file.write(f"{totalCount}\n")
        file.truncate()  # Dosyanın geri kalanını temizle
        fcntl.flock(file, fcntl.LOCK_UN)  # Kilidi serbest bırak


def update_counts(file_path):
        try:
            # Dosyayı aç ve kilitle
            with open(file_path, 'r+') as file:
                fcntl.flock(file, fcntl.LOCK_EX)  # Dosyayı kilitle (exclusive lock)

                # Dosyayı okuyarak mevcut değerleri al
                lines = file.readlines()
                daily_count = int(lines[0].strip())
                totalCount = int(lines[1].strip())

                # Değerleri birer artır
                daily_count += 1
                totalCount += 1

                # Dosyanın başına dön ve güncellenmiş değerleri yaz
                file.seek(0)
                file.write(f"{daily_count}\n")
                file.write(f"{totalCount}\n")
                file.truncate()  # Dosyanın geri kalanını temizle

                # Dosya kilidini bırak
                fcntl.flock(file, fcntl.LOCK_UN)  # Kilidi serbest bırak
        except BlockingIOError:
            time.sleep(0.1)

def read_from_file(file_path):
        try:
            with open(file_path, 'r') as f:
                # Dosyayı kilitle
                fcntl.flock(f, fcntl.LOCK_SH)
                data = f.readlines()
                # Dosyanın kilidini aç
                fcntl.flock(f, fcntl.LOCK_UN)
                for i in range(len(data)):
                    data[i] = int(data[i].strip())
            return data
        except BlockingIOError:
            time.sleep(0.1)

def saveDataToTxt(jsonVeri, tms):
        directory = 'text/database'
        filename = f'{tms}.txt'
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'a') as file:
                fcntl.flock(file, fcntl.LOCK_EX)  # Dosyayı kilitle (exclusive lock)
                file.write(jsonVeri + '\n')
                fcntl.flock(file, fcntl.LOCK_UN)  # Kilidi serbest bırak
        except BlockingIOError:
            time.sleep(0.1)

def packageJsonUp(identity, counted, type):
            
            tms = int(time() * 1000)
            dataJ = {
                "clientId": identity.data['clientId'], 
                "clientSecret": identity.data['clientSecret'], 
                "deviceId": identity.data['deviceId'],
                "count": counted,
                "date": tms,
                "type": type
            }
            return json.dumps(dataJ)

        # def logError(jsonVeri):
        #     with open("text/localData.txt", "a") as file:
        #         file.write(jsonVeri + '\n')
        #     file.close()