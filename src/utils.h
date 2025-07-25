#ifndef KBHIT_H
#define KBHIT_H

#include <string>

#ifndef _WIN32
    int kbhit();
#endif

double seconds_since_epoch();
char check_kb();


class DataFile {
private:
    FILE* file = nullptr;

public:
    DataFile(const std::string& filename);
    ~DataFile();

    bool writes_line(const std::string& line);
    bool is_open();
    void close();
};

#endif // KBHIT_H