import pyaudio
from palavras_chave.modules.psphinx_ww import PocketsphinxHotWord
from palavras_chave.utils import CyclicAudioBuffer

# NOTES:
# - you need to pip install pocketsphinx, it is an optional requirement
# - if lang is english (default)
#   - phonemes are optional and automatically derived from keyword
#       - else you need to set them in the config according to the hmm model
#   - if SpeechRecognition is installed it's acoustic model will be used
#       - else you need to set "hmm" in the config


# pyaudio params
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
MAX_RECORD_SECONDS = 20
SAMPLE_WIDTH = pyaudio.get_sample_size(FORMAT)
audio = pyaudio.PyAudio()

# Wake word initialization

config = {
    "threshold": 1e-90,
    "phonemes": "HH EY . M AY K R AO F T",
    "sample_rate": RATE
}
engine = PocketsphinxHotWord("hey mycroft", config=config)

# used for non-streaming wakewords
audio_buffer = CyclicAudioBuffer(engine.expected_duration,
                                 sample_rate=RATE,
                                 sample_width=SAMPLE_WIDTH)

# start Recording
stream = audio.open(
    channels=CHANNELS,
    format=FORMAT,
    rate=RATE,
    frames_per_buffer=CHUNK,
    input=True,  # stream is an input stream
)

found = False
for i in range(0, int(RATE / CHUNK * MAX_RECORD_SECONDS)):
    data = stream.read(CHUNK)

    # add data to rolling buffer, used by non-streaming engines
    audio_buffer.append(data)

    # feed data directly to streaming prediction engines
    engine.update(data)

    # streaming engines return result here
    # non streaming engines check the byte_data in audio_buffer
    audio_data = audio_buffer.get()
    found = engine.found_wake_word(audio_data)

    if found:
        break

if found:
    print("Found wake word!")
else:
    print("No wake word found")


# stop everything
engine.stop()
stream.stop_stream()
stream.close()
audio.terminate()

