import pyaudio
from palavras_chave.modules.dummy_ww import DummyWakeWord
from palavras_chave.utils import CyclicAudioBuffer
from os.path import join, dirname

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
    # if this file exists, it will be deleted and wakeword triggered
    "signal_file": join(dirname(__file__), "wakeword_found")
}

engine = DummyWakeWord(config=config)

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

print("Waiting for signal")

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
