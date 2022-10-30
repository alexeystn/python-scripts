#include <stdio.h>

int square(float *input, float *output, int len) {
	int i;
	for (i = 0; i < len; i++) {
		output[i] = input[i] * input[i];
	}
	return 0;
}
