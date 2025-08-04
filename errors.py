
class RaiseError:
    def __init__(self,index):
        self.index = index
        self.messages = {
            0: "Error opening cam",
            1: "İndeks hatası: Listedeki eleman sayısından büyük bir indeks geçersizdir.",
            2: "Frame return value is false (cam 28. satır) ",
            3: "response.status_code != 200 (database 66. satır)",
            4: "Hata veri alınamadı ( database 158. satır )",
            5 : "Başarısız postLog işlemi (database 206. satır)",
            6: "Camera is not open ( cam 21. satır)" , 
	        7: "Başarısız , output.decode('utf-8')  (database 57. satır)"
	    }

    def __str__(self):
        return self.messages.get(self.index)  
