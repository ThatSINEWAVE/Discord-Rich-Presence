from pypresence import Presence
import time
import json
import threading
import sys
import itertools
import os
import queue


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
command_queue = queue.Queue()
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


def command_input_thread():
    while True:
        cmd = input("[CustomRP] Enter command: ").strip().lower()
        command_queue.put(cmd)


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def animated_countdown(duration, prefix=""):
    global stop_event, command_queue
    symbols = itertools.cycle(['|', '/', '-', '\\'])
    end_time = time.time() + duration

    while time.time() < end_time and not stop_event.is_set():
        sys.stdout.write(f"\r{prefix} {next(symbols)}  Remaining: {int(end_time - time.time())}s ")
        sys.stdout.flush()

        # Check for commands more frequently within the countdown
        for _ in range(10):  # Split the sleep into smaller intervals for responsiveness
            time.sleep(0.01)

            # Check for new commands in the command queue
            try:
                cmd = command_queue.get_nowait()
                if cmd == "stop":
                    clear_console()
                    print(welcome_art)
                    print("[CustomRP] Stopping Rich Presence...")
                    stop_event.set()
                    return  # Exit the countdown early
                else:
                    clear_console()
                    print(welcome_art)
                    print("[CustomRP] Rich Presence is active. Only 'stop' command is accepted.")
            except queue.Empty:
                # Queue is empty, no commands to process
                pass

        if stop_event.is_set():
            return  # Check if stop_event has been set to exit early

    sys.stdout.write('\r[CustomRP] Done!                                        \n')


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
        # This check ensures we loop through message_sets correctly in 'all' and 'multi' modes
        if index >= len(message_sets):
            index = 0  # Reset index if out of range

        current_set = message_sets[index]
        set_name = current_set.get('name', f'Set {index + 1}')

        # Constructs kwargs for RPC.update()
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
            print(f"[CustomRP] Current presence: '{set_name}' {symbol}")
            # Increment the index for 'all' and 'multi' modes to cycle through message sets
            if presence_mode in ["all", "multi"]:
                index += 1
            animated_countdown(timer_interval, prefix=f"[CustomRP] Next update in:")
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
        print("[CustomRP] mode <all|multi|single> - Sets the mode to either 'all', 'multi' or 'single'.")
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

        print("[CustomRP] Starting Discord Rich Presence in '{}' mode.".format(mode))
        presence_thread = threading.Thread(target=update_presence, args=(
            config["application_id"], config["message_sets"], config["timer_interval"], mode))
        presence_thread.start()

    elif command == "stop":
        if presence_thread is not None:
            stop_event.set()
            if presence_thread.is_alive():
                presence_thread.join()
            presence_thread = None
            print("[CustomRP] Stopping Rich Presence...")
            print("[CustomRP] Discord RPC connection closed.")
            print("[CustomRP] Enter command: ")

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
            print(
                "[CustomRP] Use 'mode all', 'mode single', or type 'mode multi' and enter names of the parts afterwards.")
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
            names_input = input(
                "[CustomRP] Enter the names of the parts you want to use, separated by a comma: ").strip()
            names = [name.strip() for name in names_input.split(',')]
            selected_sets = [part for part in config["message_sets"] if part.get("name") in names]
            if selected_sets:
                config["message_sets"] = selected_sets
                mode = "multi"
                print(f"[CustomRP] Mode set to multi, using parts: {', '.join(names)}")
            else:
                print("[CustomRP] Specified parts not found in config.json.")
    else:
        print(f"[CustomRP] '{command_name}' is not a known command. Please try again.")
        print("[CustomRP] Type 'help' for a list of commands.")


if __name__ == "__main__":
    clear_console()
    print(welcome_art)
    print("[CustomRP] Welcome to ThatSINEWAVE's custom rich presence script!")
    print("[CustomRP] To get started, please type 'help'")

    # Start the command input thread
    input_thread = threading.Thread(target=command_input_thread, daemon=True)
    input_thread.start()

    while True:
        if not command_queue.empty():
            user_input = command_queue.get()
            handle_command(user_input)
        else:
            time.sleep(0.1)  # Adjust as necessary for responsiveness vs CPU usage
