from ctypes import *
from os.path import join, dirname
import platform
import sys


def _get_lib():
    system = platform.system()
    if system == "Linux":
        machine = platform.machine()
        if machine == "x86_64":
            return join(dirname(__file__), "lib", "linux_x86_64",
                        "libnyumaya_premium.so")
        elif machine == "armv6l":
            return join(dirname(__file__), "lib", "armv6",
                        "libnyumaya_premium.so")
        elif machine == "armv7l":
            return join(dirname(__file__), "lib", "armv7",
                        "libnyumaya_premium.so")
        else:
            raise RuntimeError("Machine not supported")
    elif system == "Windows":
        raise RuntimeError("Windows is currently not supported")

    else:
        raise RuntimeError("Your OS is currently not supported")


class NyumayaDetector:
    def __init__(self, model):

        self._lib = cdll.LoadLibrary(_get_lib())

        print("Initialize Functions")
        self._lib.createAudioRecognition.argtypes = None
        self._lib.createAudioRecognition.restype = c_void_p

        self._lib.getVersionString.argtypes = [c_void_p]
        self._lib.getVersionString.restype = c_char_p

        self._lib.getInputDataSize.argtypes = [c_void_p]
        self._lib.getInputDataSize.restype = c_size_t

        self._lib.setSensitivity.argtypes = [c_void_p, c_float, c_int]
        self._lib.setSensitivity.restype = None

        self._lib.setActive.argtypes = [c_void_p, c_bool, c_int]
        self._lib.setActive.restype = c_int

        self._lib.runDetection.argtypes = [c_void_p, POINTER(c_uint8), c_int]
        self._lib.runDetection.restype = c_int

        self._lib.runRawDetection.argtypes = [c_void_p, POINTER(c_uint8),
                                              c_int]
        self._lib.runRawDetection.restype = POINTER(c_uint8)

        self._lib.addModel.argtypes = [c_void_p, c_char_p, c_float]
        self._lib.addModel.restype = c_int

        self._lib.addModelFromBuffer.argtypes = [c_void_p, POINTER(c_char_p),
                                                 c_int]
        self._lib.addModelFromBuffer.restype = c_int

        self._lib.deleteAudioRecognition.argtypes = [c_void_p]
        self._lib.deleteAudioRecognition.restype = None

        self.model = self._lib.createAudioRecognition()
        self.check_version()
        self.model_number = self.add_model(model)

    def __del__(self):
        self._lib.deleteAudioRecognition(self.model)

    def check_version(self):

        major = None
        minor = None
        rev = None

        if sys.version_info[0] < 3:
            major, minor, rev = self.version.split('.')
        else:
            version_string = self.version[2:]
            version_string = version_string[:-1]
            major, minor, rev = version_string.split('.')

        if major != "1":
            print("Your library version is not compatible with this API")

    def add_model(self, path, sensitivity=0.5):
        model_number = c_int()
        # modelNumberBuffer = pcm.from_buffer_copy(modelNumber)

        success = self._lib.addModel(self.model, path.encode('ascii'),
                                     sensitivity,
                                     byref(model_number))
        if success != 0:
            print("Libnyumaya: Failed to open model")
            return -1

        # FIXME: Throw error on failure

        return model_number.value

    def set_active(self, model_number, active):
        success = self._lib.setActive(self.model, active, model_number)
        if success != 0:
            print("Libnyumaya: Failed to set model active")

        return success

    def remove_model(self, model_number):
        success = self._lib.removeModel(self.model, model_number)
        if success != 0:
            print("Libnyumaya: Failed to remove model")

        return success

    def run_detection(self, data):
        datalen = int(len(data))
        pcm = c_uint8 * datalen
        pcmdata = pcm.from_buffer_copy(data)
        prediction = self._lib.runDetection(self.model, pcmdata, datalen)
        return prediction

    def run_raw_detection(self, data):
        datalen = int(len(data))
        pcm = c_uint8 * datalen
        pcmdata = pcm.from_buffer_copy(data)
        prediction = self._lib.runRawDetection(self.model, pcmdata, datalen)
        re = [prediction[i] for i in range(2)]
        return re

    def set_sensitivity(self, sens, model_number=None):
        model_number = model_number or self.model_number
        self._lib.setSensitivity(self.model, sens, model_number)

    @property
    def version(self):
        return str(self._lib.getVersionString(self.model))

    def get_input_data_size(self):
        return self._lib.getInputDataSize(self.model)


class FeatureExtractor:

    def __init__(self, nfft=512, melcount=40, sample_rate=16000,
                 lowerf=20, upperf=8000, window_len=0.03, shift=0.01):
        self.melcount = melcount
        self.shift = sample_rate * shift
        self.gain = 1

        self._lib = cdll.LoadLibrary(_get_lib())

        self._lib.createFeatureExtractor.argtypes = [
            c_int, c_int, c_int, c_int, c_int, c_float, c_float]
        self._lib.createFeatureExtractor.restype = c_void_p

        self._lib.getMelcount.argtypes = [c_void_p]
        self._lib.getMelcount.restype = c_int

        self._lib.signalToMel.argtypes = [
            c_void_p, POINTER(c_int16), c_int, POINTER(c_uint8), c_float]
        self._lib.signalToMel.restype = c_int

        self._lib.deleteFeatureExtractor.argtypes = [c_void_p]
        self._lib.deleteFeatureExtractor.restype = None

        self.feature_extractor = self._lib.createFeatureExtractor(
            nfft, melcount, sample_rate, lowerf, upperf, window_len, shift)

    def __del__(self):
        self._lib.deleteFeatureExtractor(self.feature_extractor)

    # Takes audio data in the form of bytes which are converted to int16
    def signal_to_mel(self, data, gain=1):
        datalen = int(len(data) / 2)
        pcm = c_int16 * datalen
        pcmdata = pcm.from_buffer_copy(data)

        number_of_frames = int(datalen / self.shift)
        melsize = self.melcount * number_of_frames

        result = (c_uint8 * melsize)()

        reslen = self._lib.signalToMel(self.feature_extractor, pcmdata,
                                       datalen,
                                       result, gain)

        if reslen != melsize:
            print("Bad: melsize mismatch")
            print("Expected: " + str(melsize))
            print("Got: " + str(reslen))

        return bytearray(result)

    def set_gain(self, gain):
        self.gain = gain

    def get_melcount(self):
        return self._lib.get_melcount(self.feature_extractor)
