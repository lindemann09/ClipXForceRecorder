#include "utils.h"

#include <cstdio>
#include <string>
#include <chrono>

using namespace std;

#ifdef _WIN32
    // Windows implementation
    #include <conio.h>

    int kbhit() {
        return _kbhit();
    }

#else
    // macOS / Linux implementation
    #include <termios.h>
    #include <unistd.h>
    #include <fcntl.h>
    #include <cstdio>

    int kbhit() {
        termios oldt, newt;
        int ch;
        int oldf;

        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);

        oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
        fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);

        ch = getchar();

        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
        fcntl(STDIN_FILENO, F_SETFL, oldf);

        if (ch != EOF) {
            ungetc(ch, stdin);
            return 1;
        }

        return 0;
    }
#endif

char check_kb() {
    if (kbhit()) {
        char rtn = getchar();
        if (rtn == 27) rtn = 'q';
        return rtn;
    }
    return 0;
};


double seconds_since_epoch(){
	auto now = chrono::high_resolution_clock::now();
	return chrono::duration<double>(now.time_since_epoch()).count();
};


DataFile::DataFile(const std::string& filename) {
    if (filename.length() > 0) {
        file = std::fopen(filename.c_str(), "w");
        if (file == nullptr) {
            perror("Can not open data file!");
            exit(1);
        }
    } else
        file = nullptr;
}

bool DataFile::writes_line(const std::string& line) {
    if (!file) return false;
    if (std::fputs(line.c_str(), file) == EOF) return false;
    if (std::fputc('\n', file) == EOF) return false;
    return true;
}

void DataFile::close() {
    if (file) {
        std::fclose(file);
        file = nullptr;
    }
}

DataFile::~DataFile() {
    close();
}

bool DataFile::is_open() {
    return file != nullptr;
}
