from commonModules.dbManage import DatabaseManager

# Kullanım örneği
if __name__ == "__main__":
    db_manager = DatabaseManager()
    
    db_manager.reset_daily()

    db_manager.close_connection()

    # """ Localdeki veritabanını günlük olarak sıfırlayan kod, bu işlev için bir cronjob oluşturulmalıdır.
    # """