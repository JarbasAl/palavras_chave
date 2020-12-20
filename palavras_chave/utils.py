def msec_to_sec(msecs):
    """Convert milliseconds to seconds.

    Arguments:
        msecs: milliseconds

    Returns:
        int: input converted from milliseconds to seconds
    """
    return msecs / 1000


class CyclicAudioBuffer:
    """A Cyclic audio buffer for storing binary data.

    TODO: The class is still unoptimized and performance can probably be
    enhanced.

    Arguments:
        size (int): size in bytes
        initial_data (bytes): initial buffer data
    """

    def __init__(self, duration=0.98, initial_data=None,
                 sample_rate=16000, sample_width=2):
        self.size = self.duration_to_bytes(duration, sample_rate, sample_width)
        initial_data = initial_data or self.get_silence(self.size)
        # Get at most size bytes from the end of the initial data
        self._buffer = initial_data[-self.size:]

    @staticmethod
    def duration_to_bytes(duration, sample_rate=16000, sample_width=2):
        return int(duration * sample_rate) * sample_width

    @staticmethod
    def get_silence(num_bytes):
        return b'\0' * num_bytes

    def append(self, data):
        """Add new data to the buffer, and slide out data if the buffer is full

        Arguments:
            data (bytes): binary data to append to the buffer. If buffer size
                          is exceeded the oldest data will be dropped.
        """
        buff = self._buffer + data
        if len(buff) > self.size:
            buff = buff[-self.size:]
        self._buffer = buff

    def get(self):
        """Get the binary data."""
        return self._buffer

    def get_last(self, size):
        """Get the last entries of the buffer."""
        return self._buffer[-size:]

    def __getitem__(self, key):
        return self._buffer[key]

    def __len__(self):
        return len(self._buffer)

