#pragma once
#ifdef _WIN32
	#ifdef ClipXApi_EXPORTS
	#define ClipX_API __declspec(dllexport)
	#else
	#define ClipX_API __declspec(dllimport)
	#endif
#else
	#define ClipX_API __attribute__((visibility("default")))
#endif
struct sClipX {
	void *obj;
};

#ifdef __cplusplus
extern "C" {
#endif

	typedef struct sClipX * MHandle;
	ClipX_API MHandle __stdcall ClipX_Connect(const char *);
	ClipX_API void __stdcall ClipX_SDORead(MHandle m, int idx, int subidx, char* val, int size);
	ClipX_API void __stdcall ClipX_SDOWrite(MHandle m, int idx, int subidx, char* val);
	ClipX_API int __stdcall ClipX_startMeasurement(MHandle m);
	ClipX_API int __stdcall ClipX_AvailableLines(MHandle m);
	ClipX_API int __stdcall ClipX_ReadNextLine(MHandle m,double* MVLine);
	ClipX_API int __stdcall ClipX_ReadNextBlock(MHandle m, int maxreads, double* time, double* value1, double* value2, double* value3, double* value4, double* value5, double* value6);
	ClipX_API int __stdcall ClipX_stopMeasurement(MHandle m);
	ClipX_API void __stdcall ClipX_Disconnect(MHandle m);
	ClipX_API bool __stdcall ClipX_isConnected(MHandle m);

	

#ifdef __cplusplus
}
#endif
