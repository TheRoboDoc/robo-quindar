import pymumble_py3
import subprocess
import time
import argparse

from pymumble_py3.callbacks import PYMUMBLE_CLBK_SOUNDRECEIVED as PCS

parser: argparse.ArgumentParser = argparse.ArgumentParser(
    prog="robo-quindar",
    description="Quindar beeping sound player bot for Mumble",
)

parser.add_argument("--server",
                    "-s",
                    default="127.0.0.1",
                    help="Default '127.0.0.1'",
                    dest="IP_ADDRESS")

parser.add_argument("--port", "-P",
                    type=int,
                    default=64738,
                    help="Default '64738'",
                    dest="PORT")

parser.add_argument("--name",
                    "-n",
                    default="robo-quindar",
                    help="Default 'robo-quindar'",
                    dest="NAME")

parser.add_argument("--passwd",
                    "-p",
                    default="",
                    help="Default ''",
                    dest="PASSWORD")

args: argparse.Namespace = parser.parse_args()

SERVER: str = args.IP_ADDRESS
NAME: str = args.NAME
PASSWORD: str = args.PASSWORD
PORT: int = args.PORT
FILE: str = "Quindar_tones.ogg"

is_playing: bool = False
do_play: bool = False


def sound_received(user, soundchunk) -> None:
    global do_play

    do_play = True


def play_audio() -> None:
    global is_playing
    global do_play

    if is_playing:
        return

    is_playing = True

    print("Start processing")

    command: list[str] = ["ffmpeg", "-i", FILE,
                          "-acodec", "pcm_s16le", "-f", "s16le", "-ab", "192k", "-ac", "1", "-ar", "48000", "-"]

    sound: subprocess.Popen[bytes] = subprocess.Popen(command,
                                                      stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=1024)

    print("playing")

    while True:
        raw_music: bytes = sound.stdout.read(1024)

        if not raw_music:
            break

        mumble.sound_output.add_sound(raw_music)

    print("finished")

    while mumble.sound_output.get_buffer_size() > 0.5:
        time.sleep(0.01)

    is_playing = False
    do_play = False


mumble = pymumble_py3.Mumble(SERVER, NAME, PORT, PASSWORD, reconnect=True)

mumble.callbacks.set_callback(PCS, sound_received)

mumble.set_receive_sound(1)
mumble.set_application_string(NAME)

print(f"Connecting to Mumble server at {SERVER}:{PORT}")

mumble.start()
mumble.is_ready()

channel: dict = mumble.my_channel()

print(f"Connected as '{NAME}' in '{channel['name']}' (ID: {channel['channel_id']})")

try:
    while True:
        if do_play:
            play_audio()

        time.sleep(1)

except KeyboardInterrupt:
    mumble.stop()

    print("\nShutting down")
