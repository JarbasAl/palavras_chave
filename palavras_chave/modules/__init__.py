from palavras_chave.utils import msec_to_sec
from phoneme_guesser import get_phonemes
import time


class HotWordEngine:
    """Hotword/Wakeword base class to be implemented by all wake word plugins.

    Arguments:
        key_phrase (str): string representation of the wake word
        config (dict): Configuration block for the specific wake word
        lang (str): language code (BCP-47)
    """

    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        self.key_phrase = str(key_phrase).lower()

        config = config or {}
        self.config = config
        self.phonemes = config.get("phonemes") or get_phonemes(key_phrase, lang)
        num_phonemes = len(self.phonemes.split(" "))
        phoneme_duration = msec_to_sec(config.get('phoneme_duration', 120))
        self.expected_duration = self.config.get("expected_duration") or \
                                 num_phonemes * phoneme_duration
        # NOTE 0.98 was arbitrarily chosen because it corresponds to
        # nyumaya_legacy max buffer size, i don't think wakewords would fit
        # in less than this either way
        self.expected_duration = max(int(self.expected_duration), 0.98)
        self.lang = str(self.config.get("lang", lang)).lower()
        self.min_time_between_checks = self.config.get(
            "min_time_between_checks", 0.2)
        self.last_check = time.time()

    @property
    def is_time_to_check(self):
        return time.time() - self.last_check >= self.min_time_between_checks

    def check_for_wake_word(self, frame_data):
        """Check if wake word has been found.

        Checks if the wake word has been found. Should reset any internal
        tracking of the wake word state.

        Arguments:
            frame_data (binary data): Deprecated. Audio data for large chunk
                                      of audio to be processed. This should not
                                      be used to detect audio data instead
                                      use update() to incrementaly update audio
        Returns:
            bool: True if a wake word was detected, else False
        """
        return False

    def found_wake_word(self, frame_data):
        if self.is_time_to_check:
            self.last_check = time.time()
            return self.check_for_wake_word(frame_data)
        return False

    def update(self, chunk):
        """Updates the hotword engine with new audio data.

        The engine should process the data and update internal trigger state.

        Arguments:
            chunk (bytes): Chunk of audio data to process
        """

    def stop(self):
        """Perform any actions needed to shut down the wake word engine.

        This may include things such as unloading data or shutdown
        external processess.
        """
