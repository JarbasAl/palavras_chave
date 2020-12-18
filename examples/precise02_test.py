import pyaudio
from palavras_chave.modules.precise_ww import PreciseHotword
from palavras_chave.utils import CyclicAudioBuffer

# NOTES:
# - you need to manually install precise_runner
#   - pip install precise-runner==0.2.1
# - binary path can be set in config
#   - "binary_path": full/path/to/precise_executable
# - if not set binary is automatically downloaded on first run (v0.2 and v0.3 only)
# - by default precise v0.2 is used
# - see example for precise version 0.3 for more customization details
# - this example uses the bundled wakeword for "hey mycroft"

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
    "sensitivity": 0.5,
    "trigger_level": 3
}
engine = PreciseHotword("hey mycroft", config=config)

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
