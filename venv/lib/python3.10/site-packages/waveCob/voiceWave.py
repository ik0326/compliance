import pyaudio  #録音機能を使うためのライブラリ
import wave     #wavファイルを扱うためのライブラリ
 
class AudioContorol:
    def __init__(self,FILENAME:str="sample.wav",seconds:float=10):
        self.RECORD_SECONDS = seconds #録音する時間の長さ（秒）
        self.WAVE_OUTPUT_FILENAME = FILENAME #音声を保存するファイル名
        iDeviceIndex = 0 #録音デバイスのインデックス番号
        
        #基本情報の設定
        self.FORMAT = pyaudio.paInt16 #音声のフォーマット
        self.CHANNELS = 1             #モノラル
        self.RATE = 44100             #サンプルレート
        self.CHUNK = 2**11            #データ点数
        self.audio = pyaudio.PyAudio() #pyaudio.PyAudio()
 
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                rate=self.RATE, input=True,
                input_device_index = iDeviceIndex, #録音デバイスのインデックス番号
                frames_per_buffer=self.CHUNK)
 
    def record(self):
        #--------------録音開始---------------
        print ("recording...")
        frames = []
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            frames.append(data)
        
        
        print ("finished recording")
        
        #--------------録音終了---------------
        
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        
        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

if __name__ == '__main__':
    #--------------録音, wave作成テスト
    w = AudioContorol('audioTest1.wav',seconds=10)
    w.record()