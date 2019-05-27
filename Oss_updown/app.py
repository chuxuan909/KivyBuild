#!/usr/bin/env python
# -*- coding:utf-8 -*-
import win32timezone #pyinstaller打包不会自动添加此包，需要在源文件中载入
import os,platform,sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase,DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.config import Config   #kivy全局配置模块
from kivy.lang.builder import Builder
'''
环境变量添加
'''
if platform.system() == "Windows":
    BASE_DIR = '\\'.join(os.path.abspath(os.path.dirname(__file__)).split('\\')[:-1]) #for windos
    #print (BASE_DIR)
else:
    BASE_DIR = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])  #for linux
sys.path.append(BASE_DIR)
'''
加载oss上传下载模块
'''
from oss_python import oss_upload
oss_oper=oss_upload.oss2_python() #实例化模块中的类,连接到oss的bucket
'''
kivy的全局设置
'''
Config.set('input', 'mouse', 'mouse,disable_multitouch')  #右键单击红色圆圈擦除
resource_add_path('C:/Users/Administrator/AppData/Roaming/com.wonderidea.focusky/Local Store/fonts') #字体
LabelBase.register(DEFAULT_FONT, 'droidsansfallback.ttf')
#如何自定义加载kv文件,优先级低于同名小写APP子类的.kv文件
Builder.load_file('kvs/file_mains.kv')

class File_Windows(BoxLayout):
    cwdir = ObjectProperty(None)
    load=ObjectProperty(None)
    cancle_popup=ObjectProperty(None)

    def __init__(self,cwdir,load,cancle_popup):
        super(File_Windows,self).__init__()
        self.cwdir = cwdir
        self.load = load
        self.cancle_popup = cancle_popup


class Main_UI(BoxLayout):
    def show_popup(self):
        '''
        弹出文件选择窗口
        Popup为窗口弹出控件类，里面需要一个布局类实例
        :return:
        '''
        file_boxlayout = File_Windows(cwdir=os.getcwd(),load=self.load_file,cancle_popup=self.do_popup_cancle)
        self.popup=Popup(title="Load files", content=file_boxlayout,size_hint=(0.9, 0.9))
        self.popup.open()

    def do_popup_cancle(self):
        '''
        关闭文件选择窗口
        :return:
        '''
        self.popup.dismiss()

    def load_file(self,fileselects):
        '''
        将选择的文件上传到oss
        :param fileselects: 选择的文件列表，列表第一个元素为路径，不是选择的文件
        :return:None
        '''
        if platform.system() == "Windows":
            fileselects=oss_oper.str_replace(fileselects)

        for chose_file in fileselects[1:]:
            if os.path.isdir(chose_file):
                oss_oper.upload_dir(chose_file) #第二个参数为上传目标bucket的目录。省略时,默认路径设置在config/setting.py文件中
            else:
                oss_oper.upload(chose_file)     #第二个参数为上传目标bucket的目录。省略时,默认路径设置在config/setting.py文件中
        print('选择的文件为:',fileselects)

class File_main(App):
    def build(self):
        return  Main_UI()

if __name__=='__main__':
    File_main().run()