from pypresence import Presence
import time
import json
import threading
import sys
import itertools
import os


def load_config():
    try:
        with open('config.json', 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"[CustomRP] Failed to load configuration: {e}")
        sys.exit(1)


config = load_config()

# Global variables
presence_thread = None
stop_event = threading.Event()
mode = "all"  # Default mode is 'all'
show_timestamps = True
welcome_art = r"""
   _____  _____  _   _  ______ __          __  __      __ ______  _  _____ 
  / ____||_   _|| \ | ||  ____|\ \        / //\\ \    / /|  ____|( )/ ____|
 | (___    | |  |  \| || |__    \ \  /\  / //  \\ \  / / | |__   |/| (___  
  \___ \   | |  | . ` ||  __|    \ \/  \/ // /\ \\ \/ /  |  __|     \___ \ 
  ____) | _| |_ | |\  || |____    \  /\  // ____ \\  /   | |____    ____) |
 |_____/ |_____||_| \_||______|    \/  \//_/    \_\\/    |______|  |_____/ 
          _____              _                      _____   _____            
         / ____|            | |                    |  __ \ |  __ \           
        | |      _   _  ___ | |_   ___   _ __ ___  | |__) || |__) |          
        | |     | | | |/ __|| __| / _ \ | '_ ` _ \ |  _  / |  ___/           
        | |____ | |_| |\__ \| |_ | (_) || | | | | || | \ \ | |               
         \_____| \__,_||___/ \__| \___/ |_| |_| |_||_|  \_\|_|               
                                                                           
                                                                           
    """


def custom_print(message):
    """Prints a message with a timestamp if enabled."""
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
    if show_timestamps:
        print(message.replace("{TIME_STAMP}", timestamp))
    else:
        print(message.replace("{TIME_STAMP} ", ""))


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def animated_countdown(duration, prefix=""):
    symbols = itertools.cycle(['|', '/', '-', '\\'])
    end_time = time.time() + duration
    while time.time() < end_time:
        sys.stdout.write(f"\r{prefix} {next(symbols)}  Remaining: {int(end_time - time.time())}s ")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!                                        \n')


def update_presence(application_id, message_sets, timer_interval, presence_mode):
    global stop_event
    print("[CustomRP] Attempting to connect to Discord RPC...")
    RPC = Presence(client_id=application_id)
    try:
        RPC.connect()
        print(f"[CustomRP] Connected to Discord RPC.")
    except Exception as e:
        print(f"[CustomRP] Could not connect to Discord RPC: {e}")
        return

    index = 0
    animation_symbols = itertools.cycle(['|', '/', '-', '\\'])
    while not stop_event.is_set():
        clear_console()
        print(welcome_art)
        if index >= len(message_sets) and presence_mode == "all":
            index = 0  # Reset index if out of range for 'all' mode

        current_set = message_sets[index]
        set_name = current_set.get('name', f'Set {index + 1}')

        # Construct the kwargs for RPC.update()
        update_kwargs = {
            "state": current_set["state"]["text"] if "state" in current_set and current_set["state"].get("enabled",
                                                                                                         False) else "",
            "details": current_set["details"]["text"] if "details" in current_set and current_set["details"].get(
                "enabled", False) else "",
            "large_image": current_set["large_image"]["key"] if "large_image" in current_set and current_set[
                "large_image"].get("enabled", False) else "",
            "small_image": current_set["small_image"]["key"] if "small_image" in current_set and current_set[
                "small_image"].get("enabled", False) else "",
            "large_text": current_set["large_text"]["text"] if "large_text" in current_set and current_set[
                "large_text"].get("enabled", False) else "",
            "small_text": current_set["small_text"]["text"] if "small_text" in current_set and current_set[
                "small_text"].get("enabled", False) else "",
            "buttons": [{"label": button["label"], "url": button["url"]} for button in current_set.get("buttons", []) if
                        button.get("enabled", True)]
        }
        if "startTimestamp" in current_set and current_set["startTimestamp"].get("enabled", False):
            update_kwargs["start"] = current_set["startTimestamp"]["time"]
        if "endTimestamp" in current_set and current_set["endTimestamp"].get("enabled", False):
            update_kwargs["end"] = current_set["endTimestamp"]["time"]
        if "party_size" in current_set and current_set["party_size"].get("enabled", False):
            update_kwargs["party_id"] = "party_" + str(index)
            update_kwargs["party_size"] = [current_set["party_size"]["current_size"],
                                           current_set["party_size"]["max_size"]]

        try:
            RPC.update(**update_kwargs)
            symbol = next(animation_symbols)
            custom_print(f"[CustomRP] Current presence: '{set_name}' {symbol}")
            if mode == "all":
                # For 'all' mode, use animated countdown for each presence update
                animated_countdown(timer_interval, prefix=f"[CustomRP] Next update in:")
                index += 1  # Move to the next presence set
            else:
                # For 'single' mode, maintain current presence without incrementing index
                animated_countdown(timer_interval, prefix=f"[CustomRP] Maintaining presence: '{set_name}'")
        except Exception as e:
            print(f"[CustomRP] Failed to update Discord presence: {e}")
            break  # Exit the loop on failure to update presence

    RPC.clear()
    RPC.close()
    print("[CustomRP] Discord RPC connection closed.")
    stop_event.clear()


def handle_command(command):
    global config, presence_thread, stop_event, mode  # Declare 'mode' here along with other globals

    clear_console()  # Clear the console at the beginning of handling any command
    print(welcome_art)  # Display the welcome art each time a command is handled

    command_parts = command.split()
    command_name = command_parts[0] if command_parts else ""
    command_args = command_parts[1:]

    if command == "help":
        print("[CustomRP] Available commands:")
        print("[CustomRP] start - Starts the Discord Rich Presence.")
        print("[CustomRP] stop - Stops the Discord Rich Presence.")
        print("[CustomRP] mode <all|single> - Sets the mode to either 'all' or 'single'.")
        print("[CustomRP] timer <seconds> - Sets the update interval for the presence.")
        print("[CustomRP] appid <application_id> - Updates the application ID.")
        print("[CustomRP] help - You are here, this is the help command :)")
        print("[CustomRP] about - Provides information about this script.")
        print("[CustomRP] quit - Exits the script.")

    elif command == "about":
        print("[CustomRP] ThatSINEWAVE's Custom Rich Presence Script")
        print("[CustomRP] For more information, visit: https://github.com/ThatSINEWAVE/Custom-DiscordRP")
        print("[CustomRP] Contact info: You can contact me via GitHub")

    elif command == "start":
        if presence_thread is not None and presence_thread.is_alive():
            print("[CustomRP] Stopping the current Rich Presence update.")
            stop_event.set()
            presence_thread.join()

        stop_event.clear()  # Reset the stop event for the new thread

        custom_print("[CustomRP] Starting Discord Rich Presence in '{}' mode.".format(mode))
        presence_thread = threading.Thread(target=update_presence, args=(
            config["application_id"], config["message_sets"], config["timer_interval"], mode))
        presence_thread.start()

    elif command == "stop":
        if presence_thread is not None:
            stop_event.set()
            if presence_thread.is_alive():
                presence_thread.join()
            presence_thread = None
            print("[CustomRP] Discord Rich Presence has been stopped.")
            print("[CustomRP] Please wait a second for Discord to update.")

    elif command_name == "timer":
        if len(command_args) == 1:
            new_timer = command_args[0]
            try:
                config["timer_interval"] = int(new_timer)
                with open('config.json', 'w') as file:
                    json.dump(config, file, indent=4)
                print(f"[CustomRP] Timer interval set to {config['timer_interval']} seconds.")
            except ValueError:
                print("[CustomRP] Invalid timer value.")
                print("[CustomRP] Please specify an integer number of seconds.")
        else:
            print("[CustomRP] Invalid command.")
            print("[CustomRP] Usage: timer <seconds>.")

    elif command_name == "appid":
        if len(command_args) == 1:
            new_appid = command_args[0]
            config["application_id"] = new_appid
            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)
            print(f"[CustomRP] Application ID updated to {new_appid}.")
        else:
            print("[CustomRP] Invalid command.")
            print("[CustomRP] Usage: appid <NewApplicationID>.")

    elif command == "quit":
        if presence_thread is not None:
            stop_event.set()
            if presence_thread.is_alive():
                presence_thread.join()
        print(f"[CustomRP] Script stopped successfully {animated_countdown(duration=2)}")
        print(f"[CustomRP] Thanks for using my script :)")
        time.sleep(2)
        clear_console()
        sys.exit(0)
    elif command.startswith("mode"):
        mode_args = command.split(maxsplit=1)
        if len(mode_args) < 2:
            print("[CustomRP] Please select a mode: 'all', 'single', or 'multi'.")
            print("[CustomRP] Use 'mode all', 'mode single', or type 'mode multi' and enter names of the parts afterwards.")
            return
        _, selected_mode = mode_args
        if selected_mode == "all" or selected_mode == "single":
            mode = selected_mode
            print(f"[CustomRP] Mode set to {mode}.")
            if mode == "single":
                message_name = input("[CustomRP] Enter the name of the part you want to use: ").strip()
                selected_sets = [part for part in config["message_sets"] if part.get("name") == message_name]
                if selected_sets:
                    config["message_sets"] = selected_sets
                    print(f"[CustomRP] Mode set to single, using part: {message_name}")
                else:
                    print("[CustomRP] Specified part not found in config.json.")
        elif selected_mode == "multi":
            names_input = input("[CustomRP] Enter the names of the parts you want to use, separated by a comma: ").strip()
            names = [name.strip() for name in names_input.split(',')]
            selected_sets = [part for part in config["message_sets"] if part.get("name") in names]
            if selected_sets:
                config["message_sets"] = selected_sets
                mode = "multi"
                print(f"[CustomRP] Mode set to multi, using parts: {', '.join(names)}")
            else:
                print("[CustomRP] Specified parts not found in config.json.")
    elif command.startswith("mode"):
        mode_args = command.split(maxsplit=1)
        if len(mode_args) < 2:
            print("[CustomRP] Please select a mode: 'all', 'single', or 'multi'.")
            print("[CustomRP] Use 'mode all', 'mode single', or 'mode multi <NAME_1, NAME_2, ...>'.")
            return
        mode_type, *mode_values = mode_args[1].split(maxsplit=1)
        if mode_type in ["all", "single"]:
            mode = mode_type
            print(f"[CustomRP] Mode set to {mode}.")
            if mode == "single" and mode_values:
                message_name = mode_values[0]
                found = any(part.get("name") == message_name for part in config["message_sets"])
                if found:
                    config["message_sets"] = [part for part in config["message_sets"] if
                                              part.get("name") == message_name]
                    print(f"[CustomRP] Mode set to single, using part: {message_name}")
                else:
                    print("[CustomRP] Specified part not found in config.json.")
        elif mode_type == "multi" and mode_values:
            names = [name.strip() for name in mode_values[0].split(',')]
            selected_sets = [part for part in config["message_sets"] if part.get("name") in names]
            if selected_sets:
                config["message_sets"] = selected_sets
                mode = "multi"
                print(f"[CustomRP] Mode set to multi, using parts: {', '.join(names)}")
            else:
                print("[CustomRP] Specified parts not found in config.json.")
        else:
            print("[CustomRP] Invalid mode.")
            print("[CustomRP] Use 'mode all', 'mode single <NAME>', or 'mode multi <NAME_1, NAME_2, ...>'.")
    elif command.startswith("mode"):
        mode_args = command.split(maxsplit=1)
        if len(mode_args) < 2:
            print("[CustomRP] Please select a mode: 'all' or 'single'.")
            print("[CustomRP] Use 'mode all' or 'mode single'.")
            return
        _, selected_mode = mode_args
        if selected_mode in ["all", "single"]:
            mode = selected_mode
            print("[CustomRP] Mode set to {}.".format(mode))
            if mode == "single":
                message_name = input("[CustomRP] Enter the name of the part you want to use: ").strip()
                for part in config["message_sets"]:
                    if part.get("name") == message_name:
                        config["message_sets"] = [part]
                        print("[CustomRP] Mode set to single, using part: {}".format(message_name))
                        return
                print("[CustomRP] Specified part not found in config.json.")
        else:
            print("[CustomRP] Invalid mode.")
            print("[CustomRP] Use 'mode all' or 'mode single'.")

    else:
        print("[CustomRP] Unknown command.")
        print("[CustomRP] Type 'help' for a list of commands.")


if __name__ == "__main__":
    clear_console()
    print(welcome_art)
    print("[CustomRP] Welcome to ThatSINEWAVE's custom rich presence script!")
    print("[CustomRP] To get started, please type 'help'")

    while True:
        user_input = input("[CustomRP] Enter command: ").strip().lower()
        handle_command(user_input)
