from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class GetVolume(object):
    def __init__(self, ):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = interface.QueryInterface(IAudioEndpointVolume)
        self.audio_range = self.volume.GetVolumeRange()
        self.current_volume = self.volume.GetMasterVolumeLevel()

    def set_volume(self, volume):
        self.volume.SetMasterVolumeLevel(volume, None)
        self.current_volume = self.volume.GetMasterVolumeLevel()
