import streamlit as st
from vosk import Model, KaldiRecognizer, SetLogLevel
import waveCob.cutCob as cb
from waveCob.voiceWave import AudioContorol
from pydub import AudioSegment
import pandas as pd
from moviepy.video.io.VideoFileClip import VideoFileClip, AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.audio.fx.audio_fadeout import audio_fadeout
import subprocess
import os
import wave
import json

SETINGJSON = "../include/userdic.json"

def setSoundEffectFile() -> str:
    #もし、選択された効果音ファイルがあれば、そのファイルパスを渡す。
    pass

def start_exec(ngword:list, soundEfect:str="../sounds/beep.wav",select_lang="日本語", output_wave:bool=True):
    #!/usr/bin/env python3
    AUDIO = "../include/inputVoice.wav"
    OUTPUTFILE = '../output/output.wav'
    EFFECTFILE = soundEfect
    NGWORD = ngword
    selected_model_dic = {"日本語":"../include/model_jpn", "English":"../include/model_en"}
    selected_model = selected_model_dic[select_lang]
    if not os.path.exists(selected_model):
        print ("Please download the model from https://alphacephei.com/vosk/models and unpack as 'model' in the current folder.")
        exit (1)


    # w = AudioContorol(AUDIO,seconds=RECODETIME)
    # st.write("record start")
    # w.record() #レコード終了
    # st.write("record finish")

    wf = wave.open(AUDIO, "rb")
    # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    #     print ("Audio file must be WAV format mono PCM.")
    #     exit (1)

    model = Model(selected_model)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    sound = AudioSegment.from_wav(AUDIO)
    bar = st.progress(0)
    cnt:int = 0
    while True:
        data = wf.readframes(4000)
        if len(data) <= 0:
            # print(json.loads(rec.Result()))
            break
        if rec.AcceptWaveform(data):
            output = rec.Result()
            json_dict = json.loads(output)

            try:
                for word in json_dict['result']:
                    
                    if word['word'] in NGWORD:
                        print('NG wordが検出されました')
                        print(f'{word["start"]}から{word["end"]}の範囲を書き換えました。')
                        # st.dataframe(json_dict)
                        json_dict['text'] = json_dict['text'].replace(word['word'],f"<span style='background-color:yellow'>{word['word']}</span>")
                        sound = cb.chain(waveAudioSegment=sound,effectfile=EFFECTFILE,start=round(word['start'],2),end=round(word['end'],2))
                    print('word:', word['word'])
                    print('単語の開始:',word['start'])
                    print('単語の終了:',word['end'])
                    print()

                st.markdown(json_dict['text'],unsafe_allow_html=True)
            except:
                pass
        cnt += 1
        if cnt > 99:continue
        bar.progress(cnt)
    bar.progress(100)

    if output_wave:
        sound.export(OUTPUTFILE,format='wav')

    print(json.loads(rec.FinalResult())['text'])


def save_wav(upload:st.file_uploader) -> None:
    with open("../include/tempInputVoice.wav", "wb") as f:
        f.write(upload.read())
        
    input_file = "../include/tempInputVoice.wav"
    output_file = "../include/inputVoice.wav"

    command = f"ffmpeg -i {input_file} -ar 16000 -ac 1 -acodec pcm_s16le -y {output_file}"

    subprocess.call(command, shell=True)


# def save_mp3_to_wav(upload:st.file_uploader) -> None:
#     with open("../include/temp_mp3_data.mp3", "wb") as f:
#         f.write(upload.read())
#     audio = cb.AudioSegment.from_mp3("../include/temp_mp3_data.mp3")
#     audio.export("../include/inputVoice.wav",format="wav")
    
def save_mp4_to_cut_wav(upload:st.file_uploader) -> None:
    bar = st.progress(0)
    # mp4ファイルのパス
    video_file = "../include/video.mp4"
    video_output = "../include/video_no_audio.mp4"
    audio_output = "../include/inputVoice.wav"

    #mp4を一旦保存
    with open(video_file, "wb") as f:
        f.write(upload.read())
    bar.progress(20)

    
    # MP4から音声を抽出
    audio_extract_command = f"ffmpeg  -y -i {video_file} -ar 16000 -ac 1 -acodec pcm_s16le -y {audio_output}"
    subprocess.call(audio_extract_command, shell=True)

    # MP4から動画を抽出
    video_extract_command = f"ffmpeg -y -i {video_file} -c:v libx264 -preset slow -crf 22 -c:a copy {video_output}"
    subprocess.call(video_extract_command, shell=True)


    
    bar.progress(60)
    
    bar.progress(80)

    bar.progress(100)

#音声なし動画とフィルタリング音声を合成
def chain_mp4_wave():
    #問題あり
    video_file = "../include/video_no_audio.mp4"
    audio_file = "../output/output.wav"
    output_file = "../output/output.mp4"
    # 動画と音声を合成
    merge_command = f"ffmpeg -y -i {video_file} -i {audio_file} -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 {output_file}"
    subprocess.call(merge_command, shell=True)



def main():
    """概要"""
    
    st.title("コンプライアンスを防ぐアプリ")
    st.write("""本アプリケーションは、圧倒的なコンプライアンス抵触を防ぐ効果があります。
                コンプライアンスチェック及び、再生ファイル内で抽出される音声にbeep音による加工を施すことができます。
             """)
    
    """"""
    #宣言
    if 'upload_data' not in st.session_state:
        st.session_state['upload_data'] = None
    if 'upload' not in st.session_state:
        st.session_state['upload'] = False
    if 'upload_True' not in st.session_state:
        st.session_state['upload_True'] = False
    if 'first_upload' not in st.session_state:
        st.session_state['first_upload'] = True
    if 'extension' not in st.session_state:
        st.session_state['extension'] = None
    try:
        with open(SETINGJSON) as f:
            NG = json.load(f)
        if NG['ユーザー辞書'] == []:
            NG = {"ユーザー辞書":["嫌い","あほ"],"config":{"snow":True,"wordlog":True}}
            st.warning("辞書が空だったため、適当に補いました。")
            
    except:
        NG = {"ユーザー辞書":["嫌い","あほ"],"config":{"snow":True,"wordlog":True}}
        st.warning("辞書が空だったため、適当に補いました。")
    NG_list = NG['ユーザー辞書']
    tab1,tab2 = st.tabs(['実行',"settings"])

    
    with tab2:
        st.write("ここでは、コンプライアンスワードを登録することができます。")
        ipt = st.text_input("write word",key="setword") 
        
        def convert_to_wide_characters(input_str):
            wide_characters = "".join([chr(ord(c) + 65248) if ord(c) >= 33 and ord(c) <= 126 else c for c in input_str])
            return wide_characters
        ipt = convert_to_wide_characters(ipt)
        
        add_column, del_column = st.columns(2)
        with add_column:
            if st.button("追加"):
                if ipt == "":st.warning("追加したい単語をテキストボックスに入力してください。")
                if ipt not in NG['ユーザー辞書'] and ipt != "":
                    if len(ipt) > 20:
                        st.error("単語が長すぎます。")
                    else:
                        NG['ユーザー辞書'].append(ipt)
                        with open(SETINGJSON, "w") as f:
                            json.dump(NG, f, indent=4)
                        st.info("登録しました。")
                else:
                    if ipt != "":st.error("すでに登録されています。")
                

        with del_column:
            if st.button("削除"):
                if ipt == "":
                    st.warning("削除したい単語をテキストボックスに入力してください。")
                elif ipt not in NG["ユーザー辞書"]:
                    st.error("該当の単語は存在しません。")
                else:
                    NG['ユーザー辞書'].remove(ipt)
                    with open(SETINGJSON,"w") as f:
                        json.dump(NG, f, indent=4)
                        st.info("正常に削除しました。")
                
        st.dataframe(pd.DataFrame(NG['ユーザー辞書']))
        NG["config"]["snow"] = st.checkbox("snowエフェクトをオフにする",value=NG['config']['snow'])

    with tab1:

        #アップローダーを配置
        if not st.session_state.upload:
            st.session_state.upload_data = st.file_uploader('ファイルのアップロード',type=['wav','mp4'],help='動画ファイルまたは音声ファイルがアップロードできます。')

        if st.session_state.upload_True:
            st.success("実行の準備ができました。")
            input_file_name, play_demo = st.columns(2)

            with input_file_name:
                if st.button("ファイルを選択する",help="ファイルを選択しなおすことができます。"):
                    st.session_state.upload = False
                    st.session_state.upload_True = False
                    st.session_state.upload_data = None
                    st.session_state.first_upload = True
                    st.experimental_rerun()
            with play_demo:
                play = st.button("ファイルを再生する",key="play_demo")
            if play:
                # play_flag = True
                if st.session_state.upload_data.name[:-3] == 'wav':
                    st.audio(st.session_state.upload_data, format = "audio")
                else:
                    st.video(st.session_state.upload_data, format = "video")

        #ファイルがアップロードされた場合の処理
        if st.session_state.upload_data is not None and st.session_state.first_upload:
            st.session_state.first_upload = False
            st.session_state.upload = True
            st.session_state.upload_True = True
            #アップロードされたファイルの拡張子を取得
            st.session_state.extension = os.path.splitext(st.session_state.upload_data.name)[1]
            #wav ../include/inputVoice.wavに保存
            if st.session_state.extension == '.wav':
                save_wav(st.session_state.upload_data)

            #mp3 wavに変換後に上と同じ操作を実行
            # elif extension == '.mp3':
            #     save_mp3_to_wav(upload_data)
            #mp4 動画と音声に分けた後にそれぞれを指定のフォルダに格納

            elif st.session_state.extension == '.mp4':
                save_mp4_to_cut_wav(st.session_state.upload_data)
            else:
                st.error(f'拡張子『{st.session_state.extension}』はサポートしていません。')
            st.experimental_rerun()
        
        ngdefault = None
        # if st.button("全選択",help="次のセレクトボックスを全選択します。"):
        #     ngdefault = NG_list
        select_model = "日本語" #st.selectbox("言語選択",["日本語","English"],index=0)
        ngword = st.multiselect(
        '遮断する言葉を選んでください', NG_list,default=ngdefault
        )
        NGWORD = [str(word) for word in ngword]

        if st.button("実行",help='ファイルにフィルタリングを行う処理を実行します。'):
            if st.session_state.upload_True:
                st.write('実行中です。少々お待ちください。')
                if st.session_state.extension != '.mp4':
                    start_exec(NGWORD,select_lang=select_model)
                    st.subheader("NGワードを削除しました✨")
                    st.audio("../output/output.wav", format="audio/wav", start_time=0, sample_rate=None)
                    with open("../output/output.wav", "rb") as f:
                        st.download_button("Download",data=f,file_name="output.wav")
                else:
                    start_exec(NGWORD,select_lang=select_model)
                    chain_mp4_wave() #動画の結合
                    st.subheader("NGワードを削除しました✨")
                    st.video('../output/output.mp4', format="mp4")
                    with open("../output/output.mp4", "rb") as f:
                        st.download_button("Download",data=f,file_name="output.mp4")
                if not NG['config']['snow']:
                    st.snow()
            else:
                st.error('ファイルをアップロードしてください。')
    with open(SETINGJSON, "w") as f:
        json.dump(NG, f, indent=4)

if __name__ == '__main__':
    main()