# Pi Pico Tally
Pico-Tally is a Python-based tallylight implementation for the Raspberry Pi Pico, designed to be compabitle with [TallyOBS](https://github.com/deckerego/tally_obs). This project allows you to control tally lights via OBS (Open Broadcaster Software), enabling visual feedback on the status of your video sources (e.g., preview, program, or idle).

## Getting Started
### Prerequesites
 - Raspberry Pi Pico W with [Waveshare LED Matrix](https://www.waveshare.com/pico-rgb-led.htm)
 - MicroPython installed on the Pico
 - OBS (Open Broadcaster Software) with [Tally OBS Script](https://github.com/deckerego/tally_obs/blob/master/docs/OBS.md)

### Installation
 1. Clone this repository to your local machine: `git clone https://github.com/philhartung/pico-tally.git`
 2. Connect your Raspberry Pi Pico to your computer and upload all files under `src/` to the Pico using a tool like Thonny or ampy. Adjust the config.exmaple.json and rename it to config.json

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
 - Inspired by [TallyOBS](https://github.com/deckerego/tally_obs)
 - `src/tinyweb.py` is a modified version of [tinyweb](https://github.com/belyalov/tinyweb) under MIT License
