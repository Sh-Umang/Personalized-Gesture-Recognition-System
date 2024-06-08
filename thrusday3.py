import time
import pygetwindow as gw

def extract_app_name(full_title):
    # Extract the application name from the full window title
    app_name = full_title.split('-')[-1].strip()
    return app_name

def get_running_applications():
    # Get a list of all open windows
    windows = gw.getAllTitles()
    return [extract_app_name(title) for title in windows]

def get_active_application():
    # Get the currently active window
    active_window = gw.getActiveWindow()
    if active_window:
        return extract_app_name(active_window.title)
    else:
        return None

def main():
    # Initialize a variable to store the previous active application
    previous_active_app = None

    while True:
        # Get the current active application
        current_active_app = get_active_application()

        # Check if the active application has changed
        if current_active_app != previous_active_app:
            print("Active Application:", current_active_app)
            print("Running Applications:", get_running_applications())
            print("=" * 30)

            # Update the previous active application
            previous_active_app = current_active_app

        # Wait for a short duration before checking again
        time.sleep(1)

if __name__ == "__main__":
    main()
