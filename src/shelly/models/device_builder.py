from src.shelly.models.base_device import ShellyBaseDevice
from src.shelly.models.shelly_1pm import Shelly1PM
from src.shelly.models.shelly_25 import Shelly25
from src.shelly.models.shelly_uni import ShellyUni


def build_device(name: str, **kwargs) -> ShellyBaseDevice:
    if "shellyswitch25-" in name:
        return Shelly25(name=name, **kwargs)
    elif "shelly1pm-" in name:
        return Shelly1PM(name=name, **kwargs)
    elif "shellyuni-" in name:
        return ShellyUni(name=name, **kwargs)
    else:
        return ShellyBaseDevice(name=name, **kwargs)
