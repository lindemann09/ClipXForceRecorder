%Loading the ClipXApi library. 
if ~libisloaded('ClipXApi')
   %Enter the path of your ClipXApi here.
   %addpath('C:\Users\Siepmann\Desktop\Matlab')
   loadlibrary('ClipXApi.dll', 'ClipX_Interface.h');
end

%Create file to log data
file = fopen('MeasurementData.csv', 'w');

%Enter the IP address of ClipX
ip = '10.144.71.14';
h = calllib('ClipXApi', 'ClipX_Connect', ip);

idx = 17448;
sidx = 8;

%Enter the desired sample rate
samplerate = '1000';

calllib('ClipXApi', 'ClipX_SDOWrite', h, idx, sidx, samplerate);
[intres, readsamplerate] = calllib('ClipXApi', 'ClipX_SDORead', h, idx, sidx, 'abc', 10);

%Enter the desired signal indices
signals = [ 2 3 4 5 21 7 ];
[res] = signalSelector(signals, h);

calllib('ClipXApi','ClipX_startMeasurement', h);
pause(1);

%resptr = libpointer('doublePtr', zeros(1, 200));

%Amount of taken readings
c = 1000;

%Get signal names
name1 = getName(signals(1));
name2 = getName(signals(2));
name3 = getName(signals(3));
name4 = getName(signals(4));
name5 = getName(signals(5));
name6 = getName(signals(6));

%valueptr for .dll function results
time = libpointer('doublePtr', zeros(1, 200));
value1 = libpointer('doublePtr', zeros(1, 200));
value2 = libpointer('doublePtr', zeros(1, 200));
value3 = libpointer('doublePtr', zeros(1, 200));
value4 = libpointer('doublePtr', zeros(1, 200));
value5 = libpointer('doublePtr', zeros(1, 200));
value6 = libpointer('doublePtr', zeros(1, 200));

%Arrays for storing the measurement values
times = [];
value1s = [];
value2s = [];
value3s = [];
value4s = [];
value5s = [];
value6s = [];

ntpbegin = 0;
fprintf(file, '%4s ;%6s ;%6s ;%6s ;%6s ;%6s; %6s \r\n', 'time', 'value1', 'value2', 'value3', 'value4', 'value5', 'value6');



for i = 1:100
    count = calllib('ClipXApi', 'ClipX_ReadNextBlock', h, 200, time, value1, value2, value3, value4, value5, value6);
    if(i == 1)
       ntpbegin = time.Value(1); 
    end
    times = [times time.Value(1:count)];
    value1s = [value1s value1.Value(1:count)];
    value2s = [value2s value2.Value(1:count)];
    value3s = [value3s value3.Value(1:count)];
    value4s = [value4s value4.Value(1:count)];
    value5s = [value5s value5.Value(1:count)];
    value6s = [value6s value6.Value(1:count)];

    for j = 1:count 
        fprintf(file, '%12.3f ;%d ;%d ;%d ;%d ;%d ;%d \r\n', time.Value(j), value1.Value(j), value2.Value(j), value3.Value(j), value4.Value(j), value5.Value(j), value6.Value(j));  
    end
    pause(0.05)
end
timeplot = times-ntpbegin;
figure
hold on
plot(timeplot, value1s)
plot(timeplot, value2s)
plot(timeplot, value3s)
plot(timeplot, value4s)
plot(timeplot, value5s)
plot(timeplot, value6s)
xlabel('Values')
ylabel('Time in s')
title('Measurement')
grid on

fclose(file);
save measurement.mat

calllib('ClipXApi', 'ClipX_stopMeasurement', h);
calllib('ClipXApi', 'ClipX_Disconnect', h);