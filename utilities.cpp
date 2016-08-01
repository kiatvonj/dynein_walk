#include <cassert>
#include <fenv.h>
#include <fstream>
#include <stdlib.h>
#include <cstring>

#include "dynein_struct.h"
#include "simulations/simulation_defaults.h"

extern double bla_init;
extern double mla_init;
extern double mra_init;
extern double bra_init;

double dist(double x1, double y1, double x2, double y2) {
	return sqrt(pow(x2-x1, 2) + pow(y2-y1, 2));
}

double randAngle(double range) {
	srand(time(NULL));
	return ((((double)(rand() % 1000))/500) - 1) * range;
}

double square(double num) {
	return num * num;
}

double cube(double num) {
	return num * num * num;
}

double fourth(double num) {
	return num * num * num * num;
}

double fifth(double num) {
	return num * num * num * num * num;
}

double get_average(double* data, int len) {
  assert(len != 0);
  double sum = 0;
  for (int i = 0; i < len; i++) {
    sum += data[i];
  }
  return sum / len;
}

double get_variance(double* data, int len) {
  assert(len != 0);
  double sum = 0;
  double ave = get_average(data, len);
  for (int i = 0; i < len; i++) {
    sum += (data[i] - ave)*(data[i] - ave);
  }
  return sum / len;
}

void prepare_data_file(const char* custom_str, char* fname) {
  if (custom_str == NULL) {
    FILE* data_file = fopen(fname, "w"); // clear the file
    if (errno) {
      perror("Error preparing data file");
      printf("data file: %s\n", fname);
      exit(errno);
    }
    fclose(data_file);
  }
  else {
    FILE* data_file = fopen(fname, "w");
    if (errno) {
      perror("Error preparing data file");
      printf("data file: %s\n", fname);
      exit(errno);
    }
    fprintf(data_file, "%s\n", custom_str);
    fclose(data_file);
  }
}

void append_data_to_file(double* data1, double* data2, int len, FILE* file) {
    for (int i = 0; i < len; i++) {
      assert(data1[i] == data1[i]);
      // assert(data2[i] == data2[i]);
      fprintf(file, "%+.12e     %+.5e\n", data1[i], data2[i]);
    }
}

void write_config_file(char* fname, int omit_flags, const char* custom_str) {
  char text_buf[2048];
  char buf[100];
  text_buf[0] = 0;
  strcat(text_buf, custom_str);
  sprintf(buf, "Lt: %g\n", Lt);
  strcat(text_buf, buf);
  sprintf(buf, "Ls: %g\n", Ls);
  strcat(text_buf, buf);
  sprintf(buf, "T: %g\n", T);
  if ((omit_flags & CONFIG_OMIT_T) == 0) strcat(text_buf, buf);
  sprintf(buf, "ct: %.2e\n", ct);
  if ((omit_flags & CONFIG_OMIT_C) == 0) strcat(text_buf, buf);
  sprintf(buf, "cm: %.2e\n", cm);
  if ((omit_flags & CONFIG_OMIT_C) == 0) strcat(text_buf, buf);
  sprintf(buf, "cb: %.2e\n", cb);
  if ((omit_flags & CONFIG_OMIT_C) == 0) strcat(text_buf, buf);
  sprintf(buf, "dt: %g\n", dt);
  strcat(text_buf, buf);
  if ((omit_flags & CONFIG_INCLUDE_SKIPINFO) != 0) {
    sprintf(buf, "lavg width: %d\n", generate_averaging_width);
    strcat(text_buf, buf);
    sprintf(buf, "lavg pe points: %d\n", num_generate_pe_datapoints);
    strcat(text_buf, buf);
    sprintf(buf, "lavg angle points: %d\n", num_generate_angle_datapoints);
    strcat(text_buf, buf);
  }
  

  FILE* data_file = fopen(fname, "w");
  fputs(text_buf, data_file);
  fclose(data_file);
}

void FPE_signal_handler(int signum) {
  fexcept_t flag;
  fegetexceptflag(&flag, FE_ALL_EXCEPT);
  printf("FE exception occured.\n");
  printf("FE_INVALID | flag: %d\n", FE_INVALID & flag);
  printf("FE_DIVBYZERO | flag: %d\n", FE_DIVBYZERO & flag);
  printf("FE_INEXACT | flag: %d\n", FE_INEXACT & flag);
  printf("FE_UNDERFLOW | flag: %d\n", FE_UNDERFLOW & flag);
  printf("FE_OVERFLOW | flag: %d\n", FE_OVERFLOW & flag);
  exit(EXIT_FAILURE);
}

#ifdef __APPLE__
void feenableexcept(int x) { printf("fake feenableexcept for mac.\n"); }
#endif
