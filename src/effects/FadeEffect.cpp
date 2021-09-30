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

#include "FadeEffect.h"

FadeEffect::FadeEffect(uint32_t color_input, unsigned long delay_input) {
    color = color_input;
    delayLength = delay_input;
}

int8_t phase = 0;
int16_t led = 0;
void FadeEffect::update() {
    if(led > strip.numPixels()) {
        led = 0;
        phase++;
        strip.show();
    }
    uint32_t pixelColor = color;
    if(phase == 0) {
        pixelColor = ((strip.getPixelColor(led) * 2) + color) / 2;
    } else if(phase == 1) {
        pixelColor = (strip.getPixelColor(led) + color) / 2;
    } else if(phase == 2) {
        pixelColor = (strip.getPixelColor(led) + (color * 2)) / 2;
    }

    strip.setPixelColor(led, pixelColor);
    led++;
    delay(delayLength);
}

bool FadeEffect::isCompleted() {
    return phase > 3;
}

