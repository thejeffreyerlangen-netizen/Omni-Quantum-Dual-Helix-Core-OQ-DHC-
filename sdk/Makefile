# OQ-DHC SDK Makefile
CC      ?= gcc
CFLAGS  ?= -O2 -Wall -Wextra -std=c11
LDFLAGS ?= -lm

.PHONY: all test clean

all: test_sdk

test_sdk: test_sdk.c libdhqhk.c libdhqhk.h
	$(CC) $(CFLAGS) -o $@ test_sdk.c libdhqhk.c $(LDFLAGS)

test: test_sdk
	./test_sdk

clean:
	rm -f test_sdk *.o
