from pydub import AudioSegment
import numpy as np

CONSTTME = 1000
#これがないとだめ。
AudioSegment.converter = '/usr/local/Cellar/ffmpeg/4.2.1_2/bin/ffmpeg'

def chain(wavefile:str=None,waveAudioSegment:object=None, effectfile:str=None, start:float=0.0, end:float=0.0) -> object:
    _waveList = [None,None,None] #ここには、:start,end:の時間を格納する。
    if waveAudioSegment is None:
        sourceAudio = AudioSegment.from_wav(wavefile)
    else:
        sourceAudio = waveAudioSegment
    #:startを切り取る
    _waveList[0] = sourceAudio[:start*CONSTTME]
    #end:を切り取る
    _waveList[1] = sourceAudio[end*CONSTTME:]
    #startとendの間に効果音を挿入する
    _waveList[2] = effectCreate(effectfile=effectfile,start=start,end=end)

    return _waveList[0] + _waveList[2] + _waveList[1]
    

def effectCreate(effectfile:str=None, start:float=None, end:float=None) -> object:
    tdiff = end - start
    audio = AudioSegment.from_wav(effectfile)
    #配列の取り出し
    if audio.duration_seconds >= (tdiff):
        return audio[:(tdiff)*CONSTTME]
    else:
        while True:
            if audio.duration_seconds > (tdiff):
                return audio[:tdiff*CONSTTME]
            audio += audio

        

if __name__ == "__main__":
    sound = chain(wavefile='nakanoVoice.wav',effectfile='beep.wav',start=3,end=5)
    print(len(sound))
    sound.export('second.wav',format='wav')