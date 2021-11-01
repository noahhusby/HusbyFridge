/*
 * MIT License
 *
 * Copyright 2021 noahhusby
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
 * is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
 * OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 *
 */

#include <Arduino.h>
#include <Adafruit_DotStar.h>
#include <LEDController.h>
#include <effects/FadeDown.h>
#include <effects/FadeUp.h>
#include <effects/CenterFill.h>
#include <effects/CenterCollapse.h>
#include <effects/ColorChase.h>
#include <effects/Strobe.h>
#include <SPI.h>

#define FRONT_DATA 9
#define FRONT_CLOCK 8
#define INTERIOR_DATA 11
#define INTERIOR_CLOCK 10

#define FRONT_LENGTH 54
#define INTERIOR_LENGTH 56

LEDController front(FRONT_LENGTH, FRONT_DATA, FRONT_CLOCK);
LEDController interior(INTERIOR_LENGTH, INTERIOR_DATA, INTERIOR_CLOCK);

String lastData = "";

void setup() {
    pinMode(FRONT_DATA, OUTPUT);
    pinMode(FRONT_CLOCK, OUTPUT);
    Serial.begin(9600);
    front.begin();
    interior.begin();
    front.setEffect(new FadeUp(0x00FFFFFF));
    interior.setEffect(new FadeUp(0x00FFFFFF));
}

void loop() {
    if(Serial.available() > 0) {
        String data = Serial.readStringUntil('\n');
        if(data == "OFF") {
            if(lastData == "LISTENING" || lastData == "SPEAKING" || lastData == "MUTE") {
                front.setEffect(new CenterCollapse(0x00000000));
            } else {
                front.setEffect(new FadeDown(-1));
            }
            interior.setEffect(new FadeDown(-1));
        } else if(data == "ON") {
                front.setEffect(new FadeUp(0x00FFFFFF));
                interior.setEffect(new FadeUp(0x00FFFFFF));
        } else if(data == "LISTENING") {
            front.setEffect(new CenterFill(0x000000FF));
            interior.setEffect(new ColorChase(0x00FFFFFF, 0x000000FF));
        } else if(data == "SPEAKING") {
            front.setEffect(new CenterFill(0x00FFFFFF));
            interior.setEffect(new CenterFill(0x00FFFFFF));
        } else if(data == "MUTE") {
            front.setEffect(new CenterFill(0x00FF0000));
            interior.setEffect(new CenterFill(0x00FF0000));
        } else if(data == "COOL_EFFECT") {
            interior.setEffect(new ColorChase(0x00FF0000, 0x008d32a8));
        } else if(data == "ALARM") {
            front.setEffect(new ColorChase(0x00FF0000, 0x00000000));
            interior.setEffect(new ColorChase(0x00FF0000, 0x00000000));
        } else if(data == "TIMER") {
            front.setEffect(new ColorChase(0x00FFFFFF, 0x00000000));
            interior.setEffect(new ColorChase(0x000000FF, 0x00000000));
        }
        lastData = data;
    }
    front.update();
    interior.update();
    delay(2);
}

