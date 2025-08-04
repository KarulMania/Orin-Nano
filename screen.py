
import serial


class Ekran:
    """Sınıf oluştururken ekranın hangi porta bağlı olduğu ve hava durumu çekme için şehir bilgisini alır."""
    def __init__(self,port:str):
        self.port = port
        self.baudrate = 9600
        self.connection = None
        self.connect()
        print('**************************************')
    def __del__(self):
        self.close()
        print(f"{self.port} port destructor called, connection closed if it was open.")

    def connect(self):
        try:
            self.__con= serial.Serial(self.port, self.baudrate, timeout=0.1)
            print(f"{self.port} port opened successfully.")
            self.__con.write(bytes('*'.encode())) 
            
        except serial.SerialException as e:
            print(f"Error opening port: {e}")
            

    def close(self):
        if self.__con and self.__con.is_open:
            self.__con.close()
            print(f"{self.port} port closed successfully.")

    def message(self, count:int, countYear:int, typeFlag:int, _weather:int, _hour:int, _minute:int):
        """typeFlag 0 ise saati , 1 ise dereceyi yazdırır"""

        def splitCount(count):
            resultList = []
            length = len(str(count))
            operation = divmod(count, 10)

            for i in range(length):
                resultList.append(f"{operation[1]}")
                operation = divmod(operation[0], 10)
            resultList.reverse()
            listLen = 6 - len(resultList)
            if listLen >= 0:
                for i in range(listLen):
                    resultList.insert(0, "0")
            else:
                for i in range(len(resultList)):
                    resultList[i] = "9"
            for i in range(len(resultList)):
                resultList[i] = "3" + resultList[i]
            #print(sonucList)
            return resultList

        def splitDigits(number):
            quotient,remainder = divmod(number,10)
            return '3'+str(quotient),'3'+str(remainder)

        try:
            self.__con.write(bytes('*'.encode()))
        except Exception as e:
            print(f"Error writing to port: {e}")
            return
            
        character = '3'
        start = '2A'
        final = '0D'
        
        if (_weather and _hour and _minute) is not None:
            hour = _hour
            minute = _minute
            derece = _weather
            weather = derece if derece >= 0 else 0
        else:
            hour = 0
            minute = 0
            weather = 0

        countList = []
        countYearList = []

        countList = splitCount(count)
        countYearList = splitCount(countYear)

        hour1, hour2 = map(str, splitDigits(hour))
        minute1, minute2 = map(str, splitDigits(minute))
        degree1, degree2 = map(str, splitDigits(weather))

        if typeFlag == 0:  # saat yazdırılacak
            msg = start + " " + "31" + " " + "31" + " " + hour1 + " " + hour2 + " " + minute1 + " " + minute2 + " " + "31" + " " + "31" + " " \
                  + countList[2] + " " + countList[3] + " " + countList[4] + " " + countList[5] + " " + countYearList[0] + " " + countYearList[1] + " " + \
                  countYearList[2] + " " + countYearList[3] + " " \
                  + countYearList[4] + " " + countYearList[5] + " " + final
            sMsg = f"{hour}-{minute}-{count}-{countYear}"
        else:  # derece
            msg = start + " " + "33" + " " + "31" + " " + degree1 + " " + degree2 + " " + "3B" + " " + "3C" + " " + "31" + " " + "31" + " " \
                  + countList[2] + " " + countList[3] + " " + countList[4] + " " + countList[5] + " " + countYearList[0] + " " + countYearList[1] + " " + \
                  countYearList[2] + " " + countYearList[3] + " " \
                  + countYearList[4] + " " + countYearList[5] + " " + final
            sMsg = f"{weather}-C-{count}-{countYear}"

        #print(msg)
        hexValue = bytes.fromhex(msg)
        hexValue = bytes(hexValue)
        try :
            for i in range(2):
                self.__con.write(hexValue)
                self.__con.write('\r'.encode())
            print("Mesaj gönderildi -->",sMsg, flush=True)

        except Exception as exScreen:
            print("Mesaj ekrana gönderilemedi ->",exScreen, flush=True)
         


if __name__ == "__main__":

    sc1 = Ekran('/dev/ttyUSB0')
    sc2 = Ekran('/dev/ttyUSB1')
    for i in range(3000):
        sc1.message(11, 1111, 1, 2, 3, 4)
        sc2.message(11, 1111, 1, 2, 3, 4)





