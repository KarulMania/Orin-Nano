from commonModules.dbManage import DatabaseManager

# Kullanım örneği
if __name__ == "__main__":
    db_manager = DatabaseManager()
    
    db_manager.reset_monthly()

    db_manager.close_connection()


    # """ Localdeki veritabanını her ayın birinci gününde sıfırlayan kod, bu işlev için bir cronjob oluşturulmalıdır.
    # """