rpi-lcd-display
===============

Driving a 2-line LCD display from a Raspberry Pi. Functions supported

 * `message(string)` - display a message
 * `scroll_message(string, scroll_delay, skip_lines)` - vertically scroll a message, using a separate thread

Inspired by <https://github.com/adafruit/Adafruit_Python_CharLCD> (which is more comprehensive in terms of low-level functions)