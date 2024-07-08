import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from blackhole import start, resumeUncached, getPath

class BlackholeHandler(FileSystemEventHandler):
    def __init__(self, is_radarr):
        super().__init__()
        self.is_processing = False
        self.is_radarr = is_radarr
        self.path_name = getPath(is_radarr, create=True)

    def on_created(self, event):
        if not self.is_processing and not event.is_directory and event.src_path.lower().endswith((".torrent", ".magnet")):
            self.is_processing = True
            try:
                start(self.is_radarr)
            finally:
                self.is_processing = False


async def scheduleResumeUncached():
    await resumeUncached()


if __name__ == "__main__":
    print("Watching blackhole")

    radarr_handler = BlackholeHandler(is_radarr=True)
    sonarr_handler = BlackholeHandler(is_radarr=False)

    radarr_observer = Observer()
    radarr_observer.schedule(radarr_handler, radarr_handler.path_name)

    sonarr_observer = Observer()
    sonarr_observer.schedule(sonarr_handler, sonarr_handler.path_name)

    try:
        radarr_observer.start()
        sonarr_observer.start()
        asyncio.run(scheduleResumeUncached())
    except KeyboardInterrupt:
        radarr_observer.stop()
        sonarr_observer.stop()

    radarr_observer.join()
    sonarr_observer.join()
