<p align="Center">
  <a href="https://github.com/noahhusby/HusbyFridge">
    <img src="https://raw.githubusercontent.com/noahhusby/noahhusby/master/assets/husbyfridge/fridge.png" alt="Logo" width="250" height="250">
  </a>
</p>

<h1 align="Center">HusbyFridge</h1>

<p align="center">
  <b>A Google-Assistant powered Mini-Fridge.</b>
</p>

## Backstory
We found a Red Bull merchandise mini-fridge with a sticky-note indiciating it was free. Why wouldn't we take it? The fridge had seen better years completed with dings, burnt bulbs, and several other issues. After replacing the fan and temperature control, I was able to get the fridge cooling again. Simply replacing the old fluorescent bulbs felt uncreative, so I purchased three addressable LED strips. Two for the interior lighting, and one for the upper graphics luminary. To go along with the addressable LEDs, I used an Arduino and a 30W power supply to power the setup. I decided that I would attempt to make the fridge into a "smart-fridge". I grabbed a Raspberry PI from off the shelf and got to work. I used a serial connection between the Arduino and the PI to make the lighting respond to the Google Assistant status.

## Electronics
To put everything together, I designed a PCB for connecting the LEDs and the PI to the Arduino.
![](https://raw.githubusercontent.com/noahhusby/noahhusby/master/assets/husbyfridge/pcb.png)

## Code

### [Lighting](https://github.com/noahhusby/HusbyFridge/tree/main/lighting)
* C++ project for driving the leds.
* Compiled using PlatformIO.

### [Google Assistant](https://github.com/noahhusby/HusbyFridge/tree/main/src)
* Written in Python using Google Python API.
* Ability to control smart devices in room.

## Deploy
I can't imagine a use-case where anybody else would ever need to deploy this, but the instructions remain below.
* Read PlatformIO's documentation on how to compile `/lighting` and push it to an arduino.
* Clone the repo to your PI by using `git clone https://github.com/noahhusby/HusbyFridge`
```bash
cd HusbyFridge

chmod +x ./scripts/husbyfridge-installer.sh
./HusbyFridge/scripts/husbyfridge-installer.sh

chmod +x ./scripts/service-installer.sh
./scripts/service-installer.sh

sudo systemctl start HusbyFridge
```
