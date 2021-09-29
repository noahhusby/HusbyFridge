#include <Arduino.h>
#include <Adafruit_DotStar.h>
#include <SPI.h>

#define FRONT_DATA 4
#define FRONT_CLOCK 5
#define INTERIOR_DATA 6
#define INTERIOR_CLOCK 7

#define FRONT_LENGTH 108
#define INTERIOR_LENGTH 108

Adafruit_DotStar front(FRONT_LENGTH, FRONT_DATA, FRONT_CLOCK);
Adafruit_DotStar interior(INTERIOR_LENGTH, INTERIOR_DATA, INTERIOR_CLOCK);

enum lightingMode {
    OFF,
    ON,
    LISTENING,
    SPEAKING,
    MUTE
};

lightingMode currentFrontMode = OFF;
lightingMode desiredFrontMode = ON;

lightingMode currentInteriorMode = OFF;
lightingMode desiredInteriorMode = ON;

void setup() {
    Serial.begin(9600);

    front.begin();
    interior.begin();
    front.show();
    interior.show();
}

/**
 * Fill the led strip from the center -> out
 *
 * @param strip Adafruit DotStar LED Strip
 * @param color Hex color
 * @param delayLength Delay
 */
void centerFill(Adafruit_DotStar strip, uint32_t color, unsigned long delayLength) {
    uint16_t size = strip.numPixels();
    for(int i = 0; i < size / 2; i++) {
        strip.setPixelColor(size + i, (strip.getPixelColor(size + i) + color) / 2);
        strip.setPixelColor(size - i, (strip.getPixelColor(size - i) + color) / 2);
        strip.show();
        delay(delayLength);
        strip.setPixelColor(size + i, color);
        strip.setPixelColor(size - i, color);
        strip.show();
        delay(delayLength);
    }
}

/**
 * Fill the led strip from out -> center
 *
 * @param strip Adafruit DotStar LED Strip
 * @param color Hex Color
 * @param delayLength Delay
 */
void centerCollapse(Adafruit_DotStar strip, uint32_t color, unsigned long delayLength) {
    uint16_t size = strip.numPixels();
    for(int i = size / 2; i > 0; i--) {
        strip.setPixelColor(size + i, (strip.getPixelColor(size + i) + color) / 2);
        strip.setPixelColor(size - i, (strip.getPixelColor(size - i) + color) / 2);
        strip.show();
        delay(delayLength);
        strip.setPixelColor(size + i, color);
        strip.setPixelColor(size - i, color);
        strip.show();
        delay(delayLength);
    }
}

/**
 * Fades a LED strip to a color at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param color Hex Color
 * @param delayLength Delay
 */
void fade(Adafruit_DotStar strip, uint32_t color, unsigned long delayLength) {
    for(int pixel = 0; pixel < strip.numPixels(); pixel++) {
        int32_t average = ((strip.getPixelColor(pixel) * 2) + color) / 2;
        strip.setPixelColor(pixel, average);
    }
    strip.show();
    delay(delayLength);
    for(int pixel = 0; pixel < strip.numPixels(); pixel++) {
        int32_t average = (strip.getPixelColor(pixel) + color) / 2;
        strip.setPixelColor(pixel, average);
    }
    strip.show();
    delay(delayLength);
    for(int pixel = 0; pixel < strip.numPixels(); pixel++) {
        int32_t average = (strip.getPixelColor(pixel) + (color * 2)) / 2;
        strip.setPixelColor(pixel, average);
    }
    strip.show();
    delay(delayLength);
    strip.fill(color);
    strip.show();
}

/**
 * Fades a LED strip up from a specific start and stop brightness at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param start Start brightness
 * @param end End brightness
 * @param delayLength Delay
 */
void fadeUp(Adafruit_DotStar strip, uint8_t start, uint8_t end, unsigned long delayLength) {
    strip.setBrightness(start);
    strip.show();
    for(int i = start; i < end; i++) {
        strip.setBrightness(i);
        strip.show();
        delay(delayLength);
    }
}

/**
 * Fades a LED strip up at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param delayLength Delay
 */
void fadeUp(const Adafruit_DotStar& strip, unsigned long delayLength) {
    fadeUp(strip, 0, 255, delayLength);
}

/**
 * Fades a LED strip up to a specific color at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param color Hex Color
 * @param delayLength Delay
 */
void fadeUp(Adafruit_DotStar strip, uint32_t color, unsigned long delayLength) {
    fade(strip, color, delayLength);
    fadeUp(strip, delayLength);
}

/**
 * Fades a LED strip down from a specific start and stop brightness at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param start Start brightness
 * @param end End brightness
 * @param delayLength Delay
 */
void fadeDown(Adafruit_DotStar strip, uint8_t start, uint8_t end, unsigned long delayLength) {
    strip.setBrightness(start);
    strip.show();
    for(int i = start; i > end; i--) {
        strip.setBrightness(i);
        strip.show();
        delay(delayLength);
    }
}

/**
 * Fades a LED strip down from a specific start and stop brightness at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param start Start brightness
 * @param end End brightness
 * @param delayLength Delay
 */
void fadeDown(const Adafruit_DotStar& strip, unsigned long delayLength) {
    fadeDown(strip, 255, 0, delayLength);
}

/**
 * Fades a LED strip down to a specific color at a specified rate
 *
 * @param strip Adafruit DotStar LED Strip
 * @param color Hex Color
 * @param delayLength Delay
 */
void fadeDown(Adafruit_DotStar strip, uint32_t color, unsigned delayLength) {
    fade(strip, color, delayLength);
    fadeDown(strip, delayLength);
}

void loop() {
    if(Serial.available() > 0) {
        String data = Serial.readString();
        if(data.equals("OFF")) {
            desiredFrontMode = OFF;
            desiredFrontMode = OFF;
        } else if(data.equals("ON")) {
            desiredFrontMode = ON;
            desiredInteriorMode = ON;
        } else if(data.equals("LISTENING")) {
            desiredFrontMode = LISTENING;
        } else if(data.equals("SPEAKING")) {
            desiredFrontMode = SPEAKING;
        } else if(data.equals("MUTE")) {
            desiredFrontMode = MUTE;
        }
    }
    if(currentFrontMode != desiredFrontMode) {
        if(desiredFrontMode == ON) {
            fadeUp(front, 0xFFFFFF, 2);
            currentFrontMode = ON;
        }
        if(desiredFrontMode == OFF) {
            if(currentFrontMode == LISTENING || currentFrontMode == SPEAKING || currentFrontMode == MUTE) {
                centerCollapse(front, 0x000000, 2);
            } else {
                fadeDown(front, 4);
            }
            currentFrontMode = OFF;
        }
        if(desiredFrontMode == LISTENING) {
            centerFill(front, 0x4287f5, 3);
            currentFrontMode = LISTENING;
        }
        if(desiredFrontMode == SPEAKING) {
            centerFill(front, 0xFFFFFF, 3);
            currentFrontMode = SPEAKING;
        }
    }
    if(currentInteriorMode != desiredInteriorMode) {
        if(desiredInteriorMode == ON) {
            fadeUp(interior, 0xFFFFFF, 2);
            currentInteriorMode = ON;
        }
        if(desiredInteriorMode == OFF) {
            fadeDown(interior, 4);
            currentInteriorMode = OFF;
        }
    }
}

