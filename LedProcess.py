from screen import Ekran

import time

def sendDataToWrite(ekran_bisiklet, dbManager, sleepTime):
    while True:
        try:
            dataToWrite = dbManager.fetch_counts_and_timestamp()
            print('✔️ Veriler veritabanından alındı', flush=True)
            if dataToWrite is not None:
                ekran_bisiklet.message(
                    dataToWrite[2],  # örnek: count2
                    dataToWrite[3],  # örnek: timestamp
                    1,
                    dataToWrite[1],  # örnek: count1
                    dataToWrite[0],  # örnek: count0
                    dataToWrite[0]   # neden tekrar count0?
                )
            else:
                time.sleep(1)
                continue
        except Exception as e:
            print(f'❌ Veriler veritabanından alınamadı: {e}', flush=True)
        
        time.sleep(sleepTime)



if __name__ == "__main__":
    _ekran2 = Ekran('/dev/ttyUSB1')
    while True:
        _ekran2.message(1111, 111111, 1, 20, 19, 0)
        time.sleep(10)

