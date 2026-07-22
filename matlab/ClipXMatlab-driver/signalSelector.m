function [result] = signalSelector(signals, h)

%This function will set up the signals for the fifo storage to be monitored
%ClipX needs to be already connected

idx = 17448;
sidx1 = 5;
sidx2 = 7;

if(calllib('ClipXApi','ClipX_isConnected', h) == false)
    result = -1;
else
    for i = 1:6
        iin = num2str(i);
        sin = num2str(signals(i));
        calllib('ClipXApi', 'ClipX_SDOWrite', h, idx, sidx1, iin);
        calllib('ClipXApi', 'ClipX_SDOWrite', h, idx, sidx2, sin);
        result = 1;
    end
end

