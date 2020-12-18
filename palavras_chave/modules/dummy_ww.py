# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from palavras_chave.modules import HotWordEngine
from tempfile import gettempdir
from os.path import join, isfile
from os import remove


class DummyWakeWord(HotWordEngine):
    """Dummy Wake Word, only button presses trigger listening"""

    def __init__(self, hotword="dummy", config=None, lang="en-us"):
        super(DummyWakeWord, self).__init__(hotword, config or {}, lang)
        self.signal_file = self.config.get("signal_file") or \
                           join(gettempdir(), "trigger_wakeword")

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
        if isfile(self.signal_file):
            remove(self.signal_file)
            return True
        return False
