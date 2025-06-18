# Makefile for building readline program

# Compiler
CC = g++

# Compiler flags (optional: add -Wall to show all warnings)
CFLAGS = -Wall
TARGET = clipx_force_recorder
OBJS = src/main.cpp src/utils.cpp

compile:
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET) -l:ClipXLinuxApi.so -llsl -L/opt/homebrew/lib -I/opt/homebrew/include

run:
	./$(TARGET)

