import threading

class MonitoredThread(threading.Thread):
    def __init__(self, target, args=(), kwargs=None, thread_name="MonitoredThread", critical=False):
        super().__init__(target=target, args=args, kwargs=kwargs, name=thread_name)
        self.stopped = threading.Event()
        self.kwargs = kwargs if kwargs is not None else {}
        self.status = 'initialized'
        self.critical = critical  # Yeni eklenen hayati flag

    def run(self):
        try:
            self.status = 'running'
            if self._target:  # Hedef işlev kontrolü
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            self.status = f'error: {e}'
            print(f"Thread {self.name} encountered an error: {e}")
            if self.critical:  # Eğer hayati bir thread ise programı durdur
                print(f"Critical thread '{self.name}' failed. Stopping the program...")
                raise SystemExit(e)
            else:
                # Kritik olmayan thread için hatayı sadece logla
                print(f"Non-critical thread '{self.name}' encountered an error but will continue.")
        finally:
            if not self.stopped.is_set():
                self.stopped.set()  # Stopped durumu güvenilir şekilde güncellenir
            self.status = 'stopped'


    def stop(self):
        self.stopped.set()
        if self.is_alive():
            self.stop()

    def __del__(self):
        if self.is_alive():
            self.stop()
        else:
            self.status = 'stopped'
