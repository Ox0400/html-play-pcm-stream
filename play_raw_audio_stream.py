#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: zhipeng
# @Date:   2024-06-18 17:05:42
# @Last Modified By:    zhipeng
# Play PCM(RAW) audio(http stream) use python.

import time
import requests
import threading
import pyaudio
from fire import Fire
# cmd = "/Applications/VLC.app/Contents/MacOS/VLC --demux=rawaud --rawaud-channels 1 --rawaud-samplerate 16000 bin.pcm"


def play_audio(file_name_list):
    py_player = pyaudio.PyAudio()
    # 16bit, 16k
    player_fp = py_player.open(format=pyaudio.paInt16, channels=1, rate=16000, output=True)
    while True:
        try:
            idx, binary = file_name_list.pop(0)
            if idx == '<STOP>':
                player_fp.close()
                py_player.terminate()
                break
            player_fp.write(binary)
        except IndexError:
            time.sleep(0.1)

def stream_from_server(url, window_size=0):
    print(f'Fetch stream audio from {url=}')
    st = time.time()
    response = requests.get(url, stream=True)
    prev = time.time()
    print(f'First package used: {prev - st:.2f}', )
    idx = -1
    file_name_list = []
    player = threading.Thread(target=play_audio, args=(file_name_list, ))
    for message in response.iter_content(chunk_size=1024*1024*2):
        idx += 1
        if idx == window_size:
            player.start()
        curr = time.time()
        add_time = curr - prev
        prev = curr
        use_time = prev - st
        print(f"[{idx=}] Total time: {use_time:.2f}, Incremental time: {add_time:.2f} Received size: {len(message)=}")
        file_name_list.append((idx, message))
    print("Fetch audio done, wating player ...")
    file_name_list.append(('<STOP>', b'STOP'))
    player.join()

if __name__ == "__main__":
    Fire(stream_from_server)
  
