import psutil
import pygetwindow as gw

def get_running_apps():
    running_apps = set()

    # Iterate through all running processes
    for process in psutil.process_iter(['pid', 'name']):
        try:
            # Get the process name
            process_name = process.info['name']
            running_apps.add(process_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Handle exceptions that might occur while accessing process information
            pass

    return running_apps

def get_active_app():
    try:
        # Get the currently active window
        active_window = gw.getActiveWindow()
        if active_window:
            # Extract the application name from the full window title
            app_title = active_window.title
            app_name = app_title.split('-')[-1].strip()
            return app_name
        else:
            return None
    except Exception as e:
        print(f"Error while getting active window: {e}")
        return None

if __name__ == "__main__":
    running_apps = get_running_apps()
    active_app = get_active_app()

    if running_apps:
        print("Running applications:")
        for app in running_apps:
            print(app)

    if active_app:
        print("\nCurrently active application:")
        print(active_app)
    else:
        print("\nNo active application found.")
