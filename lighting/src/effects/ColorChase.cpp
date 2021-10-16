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

#include "ColorChase.h"
#include <Adafruit_DotStar.h>

ColorChase::ColorChase(uint32_t color_a_input, uint32_t color_b_input) {
    color_a = color_a_input;
    color_b = color_b_input;
}

void ColorChase::update(Adafruit_DotStar &strip) {
    if(slow) {
        if(threadDelay < 10) {
            threadDelay++;
            return;
        }
        threadDelay = 0;
    }
    strip.setPixelColor(l, cyclePhase ? color_a : color_b);
    strip.show();
    l++;
    if(l >= strip.numPixels()) {
        cyclePhase = !cyclePhase;
        l = 0;
        slow = true;
    }
}

bool ColorChase::isCompleted() {
    return false;
}

