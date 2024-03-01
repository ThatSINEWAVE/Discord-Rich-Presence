# Custom DiscordRP - Fully Customizable Rich Presence

This repository contains a customizable Discord Rich Presence script, allowing you to showcase various activities and statuses on your Discord profile. The script provides flexibility in configuring different presence sets, including details, images, buttons, and more.

## Features

- **Fully Customizable**: You can define multiple presence sets with different details, images, buttons, and timestamps.
- **Dynamic Updating**: Presence updates are sent periodically based on the specified timer interval.
- **User-Friendly Commands**: Easy-to-use commands to control and customize the script's behavior.

## Installation

Clone this repository to your local machine:

```bash
git clone https://github.com/ThatSINEWAVE/Custom-DiscordRP.git
```

### Install the required dependencies by running:

```python
pip install -r requirements.txt
```

## Configuration

The `config.json` file contains all the configuration settings for the script.
You can customize the following parameters:

**application_id**: Your Discord application ID.
**timer_interval**: Interval (in seconds) for updating the presence.
**message_sets**: Define different presence sets with various details, images, buttons, and timestamps.
Modify the `config.json` file according to your preferences before running the script.

### Example Configuration

```json
{
    "application_id": "YOUR_APPLICATION_ID",
    "timer_interval": 6,
    "message_sets": [
        {
            "name": "TEXT SET 1",
            "details": {
                "text": "Future Playtest Q2 2024",
                "enabled": true
            },
            // Other configuration parameters...
        },
        {
            "name": "TEXT SET 2",
            "details": {
                "text": "Future Playtest Q2 2024",
                "enabled": true
            },
            // Other configuration parameters...
        }
    ]
}
```

## Usage

To start the script, run main.py:

```python
python main.py
```

Once the script is running, you can interact with it using the following commands:

- **start**: Starts the Discord Rich Presence with the configured settings.
- **stop**: Stops the Discord Rich Presence.
- **timer <seconds>**: Sets the update interval for the presence.
- **appid <application_id>**: Updates the application ID used for the presence.
- **quit**: Exits the script.
- **help**: Displays a list of available commands and their usage.
- **about**: Provides information about the script and its author.

## Contributing
Your contributions are welcome! Whether it's adding new features, improving documentation, or reporting bugs, please feel free to fork this repository and submit a pull request.

## License
This project is open-sourced under the MIT License.
