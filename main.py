from pypresence import Presence
import time
import json
import threading
import sys


def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Failed to load configuration: {e}")
        sys.exit(1)


config = load_config()
presence_thread = None

# Use a threading event to signal when to stop the thread.
stop_event = threading.Event()


def update_presence(application_id, message_sets, timer_interval):
    RPC = Presence(client_id=application_id)
    try:
        RPC.connect()
    except Exception as e:
        print(f"Could not connect to Discord RPC: {e}")
        return

    index = 0
    while not stop_event.is_set():
        current_set = message_sets[index % len(message_sets)]
        set_name = current_set.get('name', f'Set {index + 1}')

        update_kwargs = {
            "state": current_set["state"]["text"] if current_set["state"].get("enabled", False) else "",
            "details": current_set["details"]["text"] if current_set["details"].get("enabled", False) else "",
            "large_image": current_set["large_image"]["key"] if current_set["large_image"].get("enabled", False) else "",
            "small_image": current_set["small_image"]["key"] if current_set["small_image"].get("enabled", False) else "",
            "large_text": current_set["large_text"]["text"] if current_set["large_text"].get("enabled", False) else "",
            "small_text": current_set["small_text"]["text"] if current_set["small_text"].get("enabled", False) else "",
            "buttons": [{"label": button["label"], "url": button["url"]} for button in current_set["buttons"] if button.get("enabled", True)]
        }

        if "startTimestamp" in current_set and current_set["startTimestamp"].get("enabled", False):
            update_kwargs["start"] = current_set["startTimestamp"]["time"]
        if "endTimestamp" in current_set and current_set["endTimestamp"].get("enabled", False):
            update_kwargs["end"] = current_set["endTimestamp"]["time"]

        if "party_size" in current_set and current_set["party_size"].get("enabled", False):
            update_kwargs["party_id"] = "party_" + str(index)
            update_kwargs["party_size"] = [current_set["party_size"]["current_size"], current_set["party_size"]["max_size"]]

        RPC.update(**update_kwargs)
        print(f"Updated presence with '{set_name}'.")

        index += 1
        time.sleep(timer_interval)

    RPC.clear()  # Clear the presence when stopping
    RPC.close()  # Close the connection properly
    stop_event.clear()  # Reset the stop event for potential future use


def handle_command(command):
    global config, presence_thread

    if command == "help":
        print("Available commands:")
        print("start - Starts the Discord Rich Presence.")
        print("stop - Stops the Discord Rich Presence.")
        print("timer <seconds> - Sets the update interval for the presence.")
        print("appid <application_id> - Updates the application ID used for the presence.")
        print("quit - Exit the script.")
        print("about - Provides information about this script.")
    elif command == "about":
        print("ThatSINEWAVE's Custom Rich Presence Script")
        print("For more information, visit: https://github.com/ThatSINEWAVE/Custom-DiscordRP")
        print("Contact info: You can contact me via GitHub")
    elif command == "start":
        if presence_thread is None or not presence_thread.is_alive():
            stop_event.clear()  # Ensure the stop event is clear before starting
            presence_thread = threading.Thread(target=update_presence,
                                               args=(config["application_id"], config["message_sets"], config["timer_interval"]))
            presence_thread.start()
            print("Discord Rich Presence has started.")
    elif command == "stop":
        stop_event.set()  # Signal the thread to stop
        if presence_thread:
            presence_thread.join()  # Wait for the thread to finish
            presence_thread = None
            print("Discord Rich Presence has been stopped. Enter a command:")
    # Existing logic for timer and appid commands
    elif command.startswith("timer"):
        try:
            _, new_timer = command.split()
            config["timer_interval"] = int(new_timer)
            try:
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=4)
                print(f"Timer interval set to {config['timer_interval']} seconds.")
            except Exception as e:
                print(f"Failed to save configuration: {e}")
        except ValueError:
            print("Invalid command. Usage: timer <seconds>. A number is required in seconds.")
    elif command == "quit":
        stop_event.set()  # Ensure the thread is signaled to stop
        if presence_thread:
            presence_thread.join()  # Wait for the thread to finish if it's running
        print("Exiting script.")
        sys.exit(0)
    elif command.startswith("appid"):
        try:
            _, new_appid = command.split()
            config["application_id"] = new_appid
            try:
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=4)
                print(f"Application ID updated to {new_appid}.")
            except Exception as e:
                print(f"Failed to save configuration: {e}")
        except ValueError:
            print("Invalid command. Usage: appid <application_id>. Application ID is required.")
    else:
        print("Unknown command. Type 'help' for a list of commands.")


if __name__ == "__main__":
    print("Welcome to ThatSINEWAVE's custom rich presence script!")
    print("To get started, please type 'help'")

    while True:
        user_input = input("Enter command: ").strip().lower()
        handle_command(user_input)
