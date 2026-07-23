# ClipXForceRecorder

Recording and streaming ClipX Force Sensors with Python and Lab Streaming Layer (LSL).

## Requirements

- [ClipX API Library](https://www.hbm.com/de/7077/clipx-praeziser-leicht-integrierbarer-messverstaerker/?product_type_no=ClipX:%20der%20pr%C3%A4zise%20und%20leicht-integrierbare%20Messverst%C3%A4rke) windows DLL is shipped with this project
  - The required windows dll can be found in the folder `lib`
  - Copy `ClipXApi.dll` to Windows system folder ("C:\Windows\System\") or change the path to the correct location of the dll in the api module

- Lab Streaming Layer (LSL): [liblsl 1.16](https://github.com/sccn/liblsl/releases)


## License

- This project is licensed under the MIT License

(c) Oliver Lindemann



### Note

See also cpp and matlab branch for not tested examples in C++ and MATLAB.
