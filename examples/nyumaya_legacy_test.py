import pyaudio
from palavras_chave.modules.nyumaya_legacy_ww import NyumayaLegacyWakeWord
from palavras_chave.utils import CyclicAudioBuffer

# NOTE this is for nyumaya_legacy v0.3.4 , this is a legacy engine,
# only bundled models are available
# you should use nyumaya_legacy premium which is v1.0.0

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
    # bundled model name or full path
    # bundled models: alexa, marvin, sheila, alexa_big, marvin_big, sheila_big
    "model": "alexa",
    "sensitivity": 0.5,
    "extractor_gain": 1.0
}
engine = NyumayaLegacyWakeWord("alexa", config=config)

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

print("Waiting for wake word")

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
