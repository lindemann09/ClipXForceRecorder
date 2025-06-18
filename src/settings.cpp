#include "settings.h"
#include "toml.hpp"

Settings read_settings(const std::string& toml_filename) {
	Settings rtn;

    toml::table tbl = toml::parse_file(toml_filename);
	rtn.ip = tbl["ip"].value_or("");
	rtn.fifo_size = tbl["fifo_size"].value_or(50);
	rtn.recording_delay = tbl["recording_delay"].value_or(1);

	rtn.flname = tbl["output_file"].value_or("");
	rtn.display = tbl["display"].value_or(1) > 0;
	rtn.stream_lsl = tbl["lsl"].value_or(1) > 0;

    return rtn;
};