import logging
import websockets
import numpy as np
import json

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components import stt

from .config_flow import (DOMAIN, NAME, WS_URL)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([ConversationSttEntity(config_entry)])

class ConversationSttEntity(stt.SpeechToTextEntity):

    def __init__(self, config_entry: ConfigEntry):
        self._attr_name = DOMAIN
        self._attr_unique_id = f"{config_entry.entry_id}-stt"
        self._wsurl = config_entry.data[WS_URL]

    @property
    def supported_languages(self):
        return ["zh-cn"]

    @property
    def supported_formats(self) -> list[stt.AudioFormats]:
        """Return a list of supported formats."""
        return [stt.AudioFormats.WAV]

    @property
    def supported_codecs(self) -> list[stt.AudioCodecs]:
        """Return a list of supported codecs."""
        return [stt.AudioCodecs.PCM]

    @property
    def supported_bit_rates(self) -> list[stt.AudioBitRates]:
        """Return a list of supported bitrates."""
        return [stt.AudioBitRates.BITRATE_16]

    @property
    def supported_sample_rates(self) -> list[stt.AudioSampleRates]:
        """Return a list of supported samplerates."""
        return [stt.AudioSampleRates.SAMPLERATE_16000]

    @property
    def supported_channels(self) -> list[stt.AudioChannels]:
        """Return a list of supported channels."""
        return [stt.AudioChannels.CHANNEL_MONO]

    async def async_process_audio_stream(self, metadata: stt.SpeechMetadata, stt_stream) -> stt.SpeechResult:
        try:
            audio_data = bytes()
            async for chunk in stt_stream:
                audio_data += chunk
            
            decoding_results = ""
            async with websockets.connect(self._wsurl) as websocket:
                sample_rate = 16000
                
                samples = np.frombuffer(audio_data, dtype=np.int16)
                samples_float32 = samples.astype(np.float32) / 32768

                buf = sample_rate.to_bytes(4, byteorder="little")  # 4 bytes
                buf += (samples_float32.size * 4).to_bytes(4, byteorder="little")
                buf += samples_float32.tobytes()

                payload_len = 10240
                while len(buf) > payload_len:
                    await websocket.send(buf[:payload_len])
                    buf = buf[payload_len:]

                if buf:
                    await websocket.send(buf)

                decoding_results = await websocket.recv()
                # to signal that the client has sent all the data
                await websocket.send("Done")


            python_dict = json.loads(decoding_results)
            return stt.SpeechResult(python_dict["text"], stt.SpeechResultState.SUCCESS)

        except Exception as err:
            _LOGGER.exception("Error processing audio stream: %s", err)
            return stt.SpeechResult('识别出现异常', stt.SpeechResultState.ERROR)
