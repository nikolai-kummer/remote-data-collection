#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>

String urlEncode(const char* str);
int32_t indexOf(const char* haystack, unsigned int haystack_len, const char* needle, unsigned search_len, long offset);

#endif // UTILS_H
