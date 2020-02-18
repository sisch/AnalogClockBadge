import display
import time
import version
import neopixel
import buttons
import utime
import machine
import wifi
import system

# TODO: Turn hands from CCW to CW: Done
# TODO: Button Press for Reconnect:
# TODO: Button Press for Resync:
# TODO: dimmer: maybe done

neopixel.enable()


def display_connecting():
    display.drawFill(0x000000)
    display.drawText(0, 0, "Connecting...", 0xFFFFFF, "7x5")
    display.flush()


def display_connected(additional_info=[]):
    display.drawFill(0x000000)
    display.drawText(0, 0, "Connected!", 0xFFFFFF, "7x5")
    for i, info in enumerate(additional_info):
        display.drawText(0, 8*(i+1), info, 0xFFFFFF, "7x5")
    display.flush()


def reconnect(pressed):
    if pressed:
        wifi.disconnect()
        display_connecting()
        wifi.connect()
        display_connected()


class clock:
    def __init__(self):
        self.running = True
        self.dimmer = 2
        self.rtc = machine.RTC()
        display_connecting()
        wifi.connect()
        if not wifi.wait():
            system.launcher()
        if wifi.status():
            display_connected(["Dimmer: %d (lf,rt)" % self.dimmer])
            self.sync_ntp(True)
            self.is_initialized = True
        else:
            ledData = [0x00, 0x00, 0x00, 0x00, 0x79, 0x00]*6
            neopixel.send(bytes(ledData))
            system.launcher()

    def sync_ntp(self, pressed):
        if pressed:
            self.rtc = machine.RTC()
            self.rtc.ntp_sync("pool.ntp.org")

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
                            green = 0xff if i == (11 - minutes) else 0x00
                            blue = 0xff if i == (11 - seconds) else 0x00
                            red = 0xff if i == (11 - hours) else 0x00
                            ledData[3*i] = green >> self.dimmer
                            ledData[3*i+1] = red >> self.dimmer
                            ledData[3*i+2] = blue >> self.dimmer
                    neopixel.send(bytes(ledData))
                    ledState = ledState + 1
                    if ledState > 254:
                        ledState = 0
                    time.sleep_ms(20)

    def light_intensity_up(self, pressed):
        if pressed:
            self.dimmer = max(0, self.dimmer - 1)
            display_connected(["Dimmer: %d (lf,rt)" % self.dimmer])

    def light_intensity_down(self, pressed):
        if pressed:
            self.dimmer = min(7, self.dimmer + 1)
            display_connected(["Dimmer: %d (lf,rt)" % self.dimmer])


a = clock()
buttons.attach(buttons.BTN_LEFT, a.light_intensity_down)
buttons.attach(buttons.BTN_RIGHT, a.light_intensity_up)
buttons.attach(buttons.BTN_UP, reconnect)
buttons.attach(buttons.BTN_DOWN, a.sync_ntp)

a.ledProc()
