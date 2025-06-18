#ifndef RECORDER_SETTINGS_H
#define RECORDER_SETTINGS_H

#include <string>

struct Settings {
    std::string ip;
    int fifo_size;
    int recording_delay;
    std::string flname;
    bool display;
    bool stream_lsl;
};

Settings read_settings(const std::string& toml_filename);

#endif // RECORDER_SETTINGS_H