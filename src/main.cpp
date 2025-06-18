#include <cstdio>
#include <unistd.h>
#include <stdlib.h>
#include <string>
#include <lsl_cpp.h>

#include "toml.hpp"
#include "ClipX.h"
#include "utils.h"

using namespace std;

const int MAX_DATA_LINE = 200;
const int lsl_nchannels = 3;

ClipX StartClipX(const string &ip, const int buffer_size)
{
	ClipX dev = ClipX();
	char buf[100]; //TODO change?
	dev.Connect(ip.c_str());
	dev.SDOWrite(0x4428, 8, to_string(buffer_size).c_str());
	dev.SDORead(0x4428, 8, buf, buffer_size);
	printf("Fifo Fill Rate: %s \n", buf);
	dev.startMeasurement();
	printf("Measurement Started\n");
	return dev;
}

double empty_clipx_buffer(ClipX &dev)
{
	// returns time sync double
	// get started and read all buffered samples()
	double values[7];
	while (dev.ReadNextLine(values) > 0)
		;
	return values[0] - seconds_since_epoch(); // time sample of last samples
}


void record_clipx(ClipX &dev, const double time_sync,
				  DataFile &data_fl,
				  lsl::stream_outlet* ptr_lsl_outlet =nullptr,
				  const bool display = true)
{
	bool paused = false;
	double values[7];
	double lsl_sample[lsl_nchannels];
	int chunk_cnt;
	double t;
	char data_line[MAX_DATA_LINE];
	char ch;

	while (true)
	{
		chunk_cnt = 0;
		while (dev.AvailableLines() > 0)
		{
			t = seconds_since_epoch(); //TODO = lsl::local_clock()
			if (dev.ReadNextLine(values) > 0)
			{
				// stream lsl
				if (ptr_lsl_outlet != nullptr) {
					lsl_sample[0] = (float)values[0];
					lsl_sample[1] = (float)values[1];
					lsl_sample[2] = (float)values[2];
					ptr_lsl_outlet->push_sample(lsl_sample);
				}
				// print and save
				++chunk_cnt;
				// printf("Time: \t %f \t %f \t %f \t %f \t %f \t %f \t %f \n", values[0], values[1], values[2], values[3], values[4], values[5], values[6]);
				sprintf(data_line, "%f, %f, %f, %i, %f, %f",
						values[0], // clipx time
						t,		   // local time
						(values[0] - t) - time_sync,
						chunk_cnt, // counter
						values[1], values[2]);

				if (display)
					printf("%s\n", data_line);

				data_fl.writes_line(data_line);
			} //
 		} // while available lines

		if (kbhit())
		{
			ch = getchar();
			if (ch == 27 or ch == 'q')
			{
				printf("Exiting...");
				break;
			}
			else if (ch == 'p')
			{
				paused = !paused; // toggle pause state
				printf("%s\n", (paused ? "Paused." : "Resumed."));
			}
		}
	} // while true
}

lsl::stream_outlet* make_lsl_outlet(const toml::table &settings) {
	//FIXME add settings
	lsl::stream_info info("ForceStream", "force", lsl_nchannels, 1000); //FIXME settings?
	return new lsl::stream_outlet(info);
}

int main()
{
	// settings
	toml::table settings = toml::parse_file("settings.toml");
	string ip_str = settings["ip"].value_or("");
	int fifo_size = settings["fifo_size"].value_or(50);
	int recording_delay = settings["recording_delay"].value_or(1);

	string flname = settings["output_file"].value_or("");
	bool display = settings["display"].value_or(1) > 0;
	bool stream_lsl = settings["lsl"].value_or(1) > 0;

	DataFile data_file = DataFile(flname);
	ClipX dev = StartClipX(ip_str, fifo_size);

	lsl::stream_outlet* ptr_lsl_outlet = nullptr;
	if (stream_lsl) ptr_lsl_outlet = make_lsl_outlet(settings);

	sleep(recording_delay);
	double time_sync = empty_clipx_buffer(dev);

	printf("Recoding Started\n");
	record_clipx(dev, time_sync, data_file, ptr_lsl_outlet, display);

	data_file.close();
	delete ptr_lsl_outlet;
	dev.stopMeasurement();
	dev.Disconnect();
}