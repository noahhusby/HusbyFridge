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

#include "CenterCollapse.h"

CenterCollapse::CenterCollapse(uint32_t color_input) {
    this->color = color_input;
}

int pixel = -1;

void CenterCollapse::update() {
    if(pixel == -1) {
        pixel = strip.numPixels() / 2;
    }
    uint16_t size = strip.numPixels();
    strip.setPixelColor(size + pixel, (strip.getPixelColor(size + pixel) + color) / 2);
    strip.setPixelColor(size - pixel, (strip.getPixelColor(size - pixel) + color) / 2);
    strip.show();
    delay(2);
    strip.setPixelColor(size + pixel, color);
    strip.setPixelColor(size - pixel, color);
    strip.show();
    delay(2);
    pixel--;
}

bool CenterCollapse::isCompleted() {
    return pixel < 1;
}

