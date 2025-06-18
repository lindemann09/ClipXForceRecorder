# Makefile for building readline program

# Compiler
CC = g++

# Compiler flags (optional: add -Wall to show all warnings)
CFLAGS = -Wall
TARGET = clipx_force_recorder
OBJS = src/main.cpp src/utils.o src/settings.o


$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $(TARGET) -l:ClipXLinuxApi.so -llsl

%.o: %.cpp %.h
	$(CC) $(CFLAGS) -c $< -o $@

compile:
	make $(TARGET)

run:
	./$(TARGET)

clean:
	rm src/*.o

