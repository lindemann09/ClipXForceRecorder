%Loading the ClipXApi library. 
if ~libisloaded('ClipXApi')
   %Enter the path of your ClipXApi here.
   addpath('.\')
   loadlibrary('ClipXApi', 'ClipX_Interface.h');
end

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

%Initializing the arrays to store data
%time = zeros(1,c);
%elec = zeros(1,c);
%gross = zeros(1,c);
%net = zeros(1,c);
%min = zeros(1,c);
%max = zeros(1,c);
%peak = zeros(1,c);

%valueptr
time = libpointer('doublePtr', zeros(1, 200));
value1 = libpointer('doublePtr', zeros(1, 200));
value2 = libpointer('doublePtr', zeros(1, 200)); 
value3 = libpointer('doublePtr', zeros(1, 200));
value4 = libpointer('doublePtr', zeros(1, 200));
value5 = libpointer('doublePtr', zeros(1, 200));
value6 = libpointer('doublePtr', zeros(1, 200));

figure
grid on
hold on

subplot(6,2,1)
an1 = animatedline('Color','r');
title('Signal 1')
ylabel('Signal1')
subplot(6,2,2)
an2 = animatedline('Color','y');
title('Signal 2')
subplot(6,2,3)
an3 = animatedline('Color','m');
title('Signal 3')
subplot(6,2,4)
an4 = animatedline('Color','c');
title('Signal 4')
subplot(6,2,5)
an5 = animatedline('Color','b');
title('Signal 5')
subplot(6,2,6)
an6 = animatedline('Color','k');
title('Signal 6')
xlabel('Time')

ntpbegin = 0;



for i = 1:1000
    count = calllib('ClipXApi', 'ClipX_ReadNextBlock', h, 200, time, value1, value2, value3, value4, value5, value6);
    if(i == 1)
       ntpbegin = time.Value(1); 
    end
    %time(i) = resptr.Value(1) - ntpbegin;
    %elec(i) = resptr.Value(2);
    %gross(i) = resptr.Value(3);
    %net(i) = resptr.Value(4);
    %min(i) = resptr.Value(5);
    %max(i) = resptr.Value(6);
    %peak(i) = resptr.Value(7);
    for j = 1:count 
        t = time.Value(j) - ntpbegin;
        addpoints(an1, t, value1.Value(j));
        addpoints(an2, t, value2.Value(3));
        addpoints(an3, t, value3.Value(4));
        addpoints(an4, t, value4.Value(5));
        addpoints(an5, t, value5.Value(6));
        addpoints(an6, t, value6.Value(7));
        
    end
    drawnow
    pause(0.05)
end

calllib('ClipXApi', 'ClipX_stopMeasurement', h);
calllib('ClipXApi', 'ClipX_Disconnect', h);
