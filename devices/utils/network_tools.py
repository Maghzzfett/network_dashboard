import subprocess # For executing system commands
import platform # for detecting the running OS
from datetime import datetime # For timestamping logs

def ping_device(ip_address):
    """
    Ping a device and return True if reachable, else False.
    """
    param = '-n' if platform.system().lower()=='windows' else '-c'
    command = ['ping', param, '1', ip_address]

    try:
        output = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return output.returncode == 0
    except Exception:
        return False