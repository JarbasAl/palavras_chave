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
from palavras_chave.exceptions import NoModelAvailable
from palavras_chave.res.snowboy.lib.snowboydecoder import get_detector, \
    find_model


class SnowboyHotWord(HotWordEngine):
    def __init__(self, key_phrase="snowboy", config=None, lang="en-us"):
        super().__init__(key_phrase, config, lang)

        # load models
        models = self.config.get("models") or [{"model_path": key_phrase}]
        if not len(models):
            raise NoModelAvailable
        paths = []
        sensitivities = []
        for model in models:
            path = model.get("model_path", key_phrase)
            sensitivity = model.get("sensitivity", 0.5)
            paths.append(find_model(path))
            sensitivities.append(sensitivity)

        # load snowboy
        self.snowboy = get_detector(paths, sensitivity=sensitivities)

    def found_wake_word(self, frame_data):
        wake_word = self.snowboy.RunDetection(frame_data)
        return wake_word >= 1

