import display
import time
import version
import neopixel
import buttons
import utime
import machine
import wifi

# TODO: Turn hands from CCW to CW
# TODO: Button Press for Reconnect
# TODO: Button Press for Resync
# TODO: dimmer

neopixel.enable()

display.drawFill(0x000000)
display.drawText(0, 0, "Connecting...", 0xFFFFFF, "7x5")
display.flush()


class clock:
    def __init__(self):
        self.running = True
        wifi.connect()
        if not wifi.wait():
            stop()
        if wifi.status():
            display.drawFill(0x000000)
            display.drawText(0, 0, "Connected!", 0xFFFFFF, "7x5")
            display.flush()
            wifi.ntp()
            self.rtc = machine.RTC()
            self.rtc.ntp_sync("pool.ntp.org")
            self.is_initialized = True
        else:
            ledData = [0x00, 0x00, 0x00, 0x00, 0x79, 0x00]*6
            neopixel.send(bytes(ledData))
            stop()

    def updateDisplay(self):
        display.drawFill(0x000000)
        display.flush()

    def ledProc(self):
        if self.is_initialized:
            ledState = 0
            ledData = [0x00, 0x00, 0x00]*12
            while True:
                for i in range(len(ledData)):
                    if ledData[i] > 64:
                        ledData[i] -= 64
                    else:
                        ledData[i] = 0
                    time_full = self.rtc.now()
                    hours = int(time_full[3]) % 12
                    minutes = int(time_full[4] / 5)
                    seconds = int(time_full[5] / 5)
                    if self.running:
                        for i in range(12):
                            # blue = 0xff if seconds // 5 == i else 0
                            # green = 0xff if minutes // 5 == i else 0
                            # red = 0xff if hours % 12 == i else 0
                            green = 0xff if i == (12 - minutes) else 0x00
                            blue = 0xff if i == (12 - seconds) else 0x00
                            red = 0xff if i == (12 - hours) else 0x00
                            ledData[3*i] = green >> 2
                            ledData[3*i+1] = red >> 2
                            ledData[3*i+2] = blue >> 2
                    neopixel.send(bytes(ledData))
                    ledState = ledState + 1
                    if ledState > 254:
                        ledState = 0
                    time.sleep_ms(20)


a = clock()
a.ledProc()
