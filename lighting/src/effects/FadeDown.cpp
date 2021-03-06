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

#include "FadeDown.h"

FadeDown::FadeDown() : FadeDown(-1) { }

FadeDown::FadeDown(uint32_t color_input) : FadeDown(color_input, 255, 0) { }

FadeDown::FadeDown(uint32_t color_input, uint8_t start_input, uint8_t end_input) {
    this->color = color_input;
    this->b = start_input;
    this->end = end_input;
}

void FadeDown::update(Adafruit_DotStar& strip) {
    if(color != -1 && !configuredColor) {
        strip.fill(color);
        configuredColor = true;
    }
    strip.setBrightness(b);
    strip.show();
    b--;
    if(b == end) {
        strip.fill(0x00000000);
        strip.setBrightness(255);
        strip.show();
    }
}

bool FadeDown::isCompleted() {
    return b == end;
}

