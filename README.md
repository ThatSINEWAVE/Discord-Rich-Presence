# Sinewave's CustomRP - Discord Rich Presence

Sinewave's CustomRP is a Python script designed to offer you the flexibility to showcase a fully customizable status (rich presence) on Discord. By leveraging the pypresence library, users can dynamically update their Discord presence with a variety of details, including project status, current activity, and more. This README provides all necessary details to get started, customize, and use the script effectively.

 ![MAIN MENU](https://github.com/ThatSINEWAVE/Custom-DiscordRP/assets/133239148/2d27c186-c6a5-4f2e-b1de-9fc24495fd87)

## Features!


- **Multiple Rich Presence Configurations**: Configure and cycle through multiple rich presence settings as defined in a `config.json` file.
- **Dynamic Presence Updates**: Automatically update your Discord presence at specified intervals.
- **Customizable Elements**: Set detailed states, images, buttons, and more for each rich presence configuration.
- **Interactive Commands**: Control the script in real-time using command-line inputs.
- **Extensive Customization**: Utilize a wide array of parameters for rich presence, including details, state, images, and clickable buttons linking to external URLs.

## Prerequisites

- **Python 3.6+**: Ensure Python is installed on your system. The script is compatible with Python 3.6 and newer versions.
- **pypresence Library**: A Python library that allows interaction with Discord's Rich Presence feature.

## Installation

1. **Install Python**: Download and install Python 3.6 or newer from the official Python website.

2. **Install pypresence**: Open a terminal or command prompt and install the pypresence library using pip:

```python
pip install pypresence
```

3. **Download the Script**: Download the Custom Discord Rich Presence script and the sample `config.json` file to your desired directory.

## Configuration (config.json)

![Premade Configs](https://github.com/ThatSINEWAVE/Discord-Rich-Presence/assets/133239148/b11d6f30-e320-4b13-a555-ccf95cce9924)

The ``config.json`` file is where you define your rich presence configurations. Here's a breakdown of the file structure:

- `application_id`: Your Discord application ID.
- `timer_interval`: The interval (in seconds) at which the rich presence updates cycle through the configured messages.
- `message_sets`: An array of message configurations, each with the following fields:
- `name`: A unique identifier for the configuration.
- `details`, state: Text fields for setting the user's current activity.
- `large_image`, `small_image`: URLs or keys for the images to display.
- `large_text`, `small_text`: Hover texts for the images.
- `buttons`: An array of buttons, each with a label and a url.
- `party_size`: (Optional) Displays the current and maximum size of a party.
- `startTimestamp`, `endTimestamp`: (Optional) Timestamps to show elapsed or remaining time.

Refer to the provided config.json example for more detailed configurations.

## Usage

- **Start the Script**: Navigate to the script's directory in a terminal or command prompt and execute the script:

```python
python main.py
```

### Use Commands:

![HELP MENU](https://github.com/ThatSINEWAVE/Custom-DiscordRP/assets/133239148/6d4ea699-89a9-4417-a936-fc81f9718e6e)

Once the script is running, it will prompt you for commands. Use the help command to see all available options:

- `start`: Initiates the rich presence update process.
- `stop`: Halts any ongoing rich presence updates.
- `mode <all|multi|single>`: Sets the update mode to cycle through all configured messages, stick to a single one or choose multiple ones.
- `timer <seconds>`: Adjusts the interval between updates.
- `appid <application_id>`: Updates the Discord application ID used for the rich presence.
- `help`: Displays a list of available commands.
- `info`: Information about your current setup.
- `about`: Shows information about the script.
- `quit`: Exits the script.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.

## Disclaimer

This script is not affiliated with or endorsed by Discord.
Use this script responsibly and in accordance with Discord's guidelines and terms of service.
