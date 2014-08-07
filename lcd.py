import RPi.GPIO as GPIO
import time
import textwrap

# Define GPIO to LCD mapping
LCD_RS = 27
LCD_E  = 22
LCD_DB4 = 25
LCD_DB5 = 24
LCD_DB6 = 23
LCD_DB7 = 18

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_LINES = 2     # Number of lines
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Offset for up to 4 rows.
LCD_ROW_OFFSETS         = (0x00, 0x40, 0x14, 0x54)

# Commands
LCD_CLEAR_DISPLAY        = 0x01
LCD_RETURN_HOME          = 0x02
LCD_ENTRY_MODE_SET       = 0x04
LCD_DISPLAY_CONTROL      = 0x08
LCD_CURSOR_SHIFT         = 0x10
LCD_FUNCTION_SET         = 0x20
LCD_SET_CGRAM_ADDR       = 0x40
LCD_SET_DDRAM_ADDR       = 0x80

# Control flags
LCD_DISPLAY_ON           = 0x04
LCD_DISPLAY_OFF          = 0x00
LCD_CURSOR_ON            = 0x02
LCD_CURSOR_OFF           = 0x00
LCD_BLINK_ON             = 0x01
LCD_BLINK_OFF            = 0x00

# Move flags
LCD_DISPLAY_MOVE         = 0x08
LCD_CURSOR_MOVE          = 0x00
LCD_MOVE_RIGHT           = 0x04
LCD_MOVE_LEFT            = 0x00

# Function set flags
LCD_8BIT_MODE            = 0x10
LCD_4BIT_MODE            = 0x00
LCD_2LINE                = 0x08
LCD_1LINE                = 0x00
LCD_5x10_DOTS            = 0x04
LCD_5x8_DOTS             = 0x00

# Entry flags
LCD_ENTRY_RIGHT          = 0x00
LCD_ENTRY_LEFT           = 0x02
LCD_ENTRY_SHIFT_INCREMENT = 0x01
LCD_ENTRY_SHIFT_DECREMENT = 0x00

# Timing constants
E_PULSE = 0.00005
E_DELAY = 0.00005

class LCD_Display(object):

    rs = LCD_RS
    e = LCD_E
    db4 = LCD_DB4
    db5 = LCD_DB5
    db6 = LCD_DB6
    db7 = LCD_DB7
    lines = LCD_LINES
    cols = LCD_WIDTH

    def init(self):
        GPIO.setmode(GPIO.BCM)

        # Set up output pins
        GPIO.setup(self.rs, GPIO.OUT)
        GPIO.setup(self.e, GPIO.OUT)
        GPIO.setup(self.db4, GPIO.OUT)
        GPIO.setup(self.db5, GPIO.OUT)
        GPIO.setup(self.db6, GPIO.OUT)
        GPIO.setup(self.db7, GPIO.OUT)

        # Initialize display
        self._send_cmd(0x33)
        self._send_cmd(0x32)

        # Initialize display control, function, and mode registers.
        self._send_cmd(LCD_DISPLAY_CONTROL | LCD_DISPLAY_ON | LCD_CURSOR_OFF | LCD_BLINK_OFF)
        self._send_cmd(LCD_FUNCTION_SET | LCD_4BIT_MODE | LCD_2LINE | LCD_5x8_DOTS)
        self._send_cmd(LCD_ENTRY_MODE_SET | LCD_ENTRY_LEFT | LCD_ENTRY_SHIFT_DECREMENT)
        self.clear()

    def home(self):
        """Move the cursor back to its home (first line and first column)."""
        self._send_cmd(LCD_RETURN_HOME)  # set cursor position to zero
        time.sleep(0.003)  # this command takes a long time!

    def clear(self):
        """Clear the LCD."""
        self._send_cmd(LCD_CLEAR_DISPLAY)  # command to clear display
        time.sleep(0.003)

    def scroll_message(self, string):
        # Format the string into lines first
        string_lines = textwrap.wrap(string, LCD_WIDTH)
        current_first_line = 0

        while True:
            print "Line {0}: {1}".format(current_first_line, string_lines[current_first_line])
            # Update first line
            self._send_cmd(LCD_LINE_1)
            self._send_line(string_lines[current_first_line])

            # Update second line
            self._send_cmd(LCD_LINE_2)
            if current_first_line < len(string_lines) - 1:
                self._send_line(string_lines[current_first_line + 1])
            else:
                self._send_line("")

            current_first_line = (current_first_line + 1) % len(string_lines)

            time.sleep(1.5)

    def message(self, string):
        # Start on first line
        self._send_cmd(LCD_LINE_1)
        for char in string:
            if char == '\n':
                self._send_cmd(LCD_LINE_2)
            else:
                self._send_char(ord(char))

    def _send_line(self, string):
        for char in string:
            self._send_char(ord(char))

        if len(string) < LCD_WIDTH:
            for cc in range(len(string), LCD_WIDTH):
                self._send_char(ord(" "))

    def _send_cmd(self, value):
        self._send_byte(value, LCD_CMD)

    def _send_char(self, value):
        self._send_byte(value, LCD_CHR)

    def _send_byte(self, value, mode):
        """ Send byte to data pins
            mode = True  for character
                   False for command """

        GPIO.output(self.rs, mode)

        # High bits
        GPIO.output(self.db4, ((value >> 4) & 1) > 0)
        GPIO.output(self.db5, ((value >> 5) & 1) > 0)
        GPIO.output(self.db6, ((value >> 6) & 1) > 0)
        GPIO.output(self.db7, ((value >> 7) & 1) > 0)

        # Toggle Enable pin
        self._toggle_e()

        # Low bits
        GPIO.output(self.db4, ( value       & 1) > 0)
        GPIO.output(self.db5, ((value >> 1) & 1) > 0)
        GPIO.output(self.db6, ((value >> 2) & 1) > 0)
        GPIO.output(self.db7, ((value >> 3) & 1) > 0)

        # Toggle Enable pin
        self._toggle_e()

    def _toggle_e(self):
        time.sleep(E_DELAY)
        GPIO.output(self.e, True)
        time.sleep(E_PULSE)
        GPIO.output(self.e, False)
        time.sleep(E_DELAY)

if __name__ == '__main__':
    try:
        display = LCD_Display()
        display.init()
        display.scroll_message("here's quite a long string, I wonder if this will be more than enough to fill the display")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Exiting"
    except Exception as e:
        raise(e)
    finally:
        GPIO.cleanup()


