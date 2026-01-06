from app.tasks.scheduler import create_scheduler

if __name__ == "__main__":
    scheduler = create_scheduler()
    scheduler.start()
    import time
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
