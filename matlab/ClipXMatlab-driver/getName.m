function [name] = getName(signalid)
switch signalid
    case 0
        name = 'ADC Value';
    case 1
        name = 'Filtered ADC Value';
    case 2
        name = 'Field Value';
    case 3
        name = 'Gross Value';
    case 4
        name = 'Net Value';
    case 5
        name = 'Min Value';
    case 6
        name = 'Max Value';
    case 7
        name = 'Peak Peak Value';
    case 8
        name = 'Captured Value 1';
    case 9
        name = 'Captured Value 2';
    case 10
        name = 'ClipX Bus Value 1';
    case 11
        name = 'ClipX Bus Value 2';
    case 12
        name = 'ClipX Bus Value 3';
    case 13
        name = 'ClipX Bus Value 4';
    case 14
        name = 'ClipX Bus Value 5';
    case 15
        name = 'ClipX Bus Value 6';
    case 16
        name = '';
    case 17
        name = '';
    case 18
        name = '';
    case 19
        name = '';
    case 20
        name = '';
    case 21
        name = 'Calculated Value 1';
    case 22
        name = 'Calculated Value 2';
    case 23
        name = 'Calculated Value 3';
    case 24
        name = 'Calculated Value 4';
    case 25
        name = 'Calculated Value 5';
    case 26
        name = 'Calculated Value 6';
    case 27
        name = 'Ethernet API 1';
    case 28
        name = 'Ethernet API 2';
    case 29
        name = 'Fieldbus Value 1';
    case 30
        name = 'Fieldbus Value 2';
    case 31
        name = 'Analog Out Value';
    case 32
        name = 'Constant -1';
    case 33
        name = 'Constant 0';
    case 34
        name = 'Constant 1';
    case 35
        name = 'Constant PI/2';
    case 36
        name = 'Constant PI';
    case 37
        name = 'Constant 2*PI';
    case 38
        name = 'User Constant 1';
    case 39
        name = 'User Constant 2';
    case 40
        name = 'User Constant 3';
    case 41
        name = 'User Constant 4';
    case 42
        name = 'User Constant 5';
    case 43
        name = 'User Constant 6';
    case 44
        name = 'User Constant 7';
    case 45
        name = 'User Constant 8';
    case 46
        name = 'User Constant 9';
    case 47
        name = 'User Constant 10';
end        