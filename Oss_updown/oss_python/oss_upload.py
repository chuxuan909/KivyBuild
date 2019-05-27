#!/usr/bin/env python
# __author__ = '陈捷'
# -*- coding:utf-8 -*-
# 上传文件到阿里云OSS
# 邮箱：305958872@qq.com
import os,sys,platform,shutil
import oss2
from  oss_python.config import settings  #加载oss认证相关的配置文件,所有oss认证相关信息被保存在settings.py文件中

#当前路径加入环境变量
if platform.system() == "Windows":
    BASE_DIR = '\\'.join(os.path.abspath(os.path.dirname(__file__)).split('\\')[:-1]) #for windos
    #print (BASE_DIR)
else:
    BASE_DIR = '/'.join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])  #for linux
sys.path.append(BASE_DIR)


class oss2_python(object):
    def __init__(self):
        # 设置oss的登陆相关信息的环境变量
        # 这些信息在你的oss控制台能获取到,详情见 https://help.aliyun.com/knowledge_detail/48699.html
        self.access_key_id = os.getenv('OSS_TEST_ACCESS_KEY_ID', settings.Params['access_key_id'])  #你的Accesskeyid
        self.access_key_secret = os.getenv('OSS_TEST_ACCESS_KEY_SECRET', settings.Params['access_key_secret'])  #你的AccessKeySecret
        self.bucket_name = os.getenv('OSS_TEST_BUCKET', settings.Params['bucket_name'])   #<你的Bucket>
        self.endpoint = os.getenv('OSS_TEST_ENDPOINT', settings.Params['endpoint'])  #你的endpoint，即你的Buckert所处的区域
        self.__Check_oss()
        self.__Create_Bucket()

    def __Check_oss(self):
        '''
        检测oss环境变量配置
        '''
        for param in (self.access_key_id, self.access_key_secret, self.bucket_name, self.endpoint):
            assert '<' not in param, '请设置参数：' + param  #零宽断言

    def __Create_Bucket(self):
        '''
        创建Bucket对象，所有Object相关的接口都可以通过Bucket对象来进行
        '''
        self.__bucket = oss2.Bucket(oss2.Auth(self.access_key_id, self.access_key_secret), self.endpoint, self.bucket_name,connect_timeout=30)

    def __percentage(self,consumed_bytes, total_bytes):
        '''
        获取当前上传/下载的百分比
        '''
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print('\r{0}%\n '.format(rate), end='')  #end='' 表示不换行
            sys.stdout.flush()  #强制刷新缓冲，为了linux下能正常的依次显示百分比

    def str_replace(self,path_list):
        '''
        # 用于将windos下文件夹路径'\\'符号的替换
        将路径符号'\\'替换为linux的路径符号'/'
        '''
        res_li=[]
        for index in path_list:
            res_li.append(index.replace('\\','/'))
        return res_li

    def upload(self,localpath,keys=settings.Params['default_bucket_upload_path']):
        '''
        断点续传上传
        '''
        # 断点续传一：文件比较小时（小于oss2.defaults.multipart_threshold）实际上用的是oss2.Bucket.put_object
        oss2.resumable_upload(self.__bucket,'%s/%s' % (keys, localpath.split('/')[-1:][0]), localpath, progress_callback=self.__percentage)

    def upload_dir(self,path,key_dir=settings.Params['default_bucket_upload_path']):
        '''
        上传目录到bucket的某个目录
        以断点续传的方式
        :param key_dir:
        :param path:
        :return:
        '''

        os.chdir(path)
        path_list=os.listdir('./')
        for path_file in path_list:
            if os.path.isfile(path_file):  #只有目录下的文件才会上传
                print('正在上传%s,进度: ' % path_file,end='') #end='' 表示不换行
                self.upload('%s/%s' % (path,path_file),key_dir)

    def download_file(self,keys,loaclpath):
        '''
        下载文件
        '''
        #data=bucket.get_object(key).read()
        try:
            file_down = self.__bucket.get_object_to_file(keys, loaclpath)  #下载文件到本地
        except oss2.exceptions.NoSuchKey as e:
            print('文件%s不存在' % keys)

    def show_info(self):
        '''
        显示bucket的详细信息
        '''
        bucket_info = self.__bucket.get_bucket_info()
        print('name: %s ' % bucket_info.name)
        print('storage class: %s ' % bucket_info.storage_class)
        print('creation date: %s  ' % bucket_info.creation_date)
        print('intranet_endpoint: %s  ' % bucket_info.intranet_endpoint)
        print('extranet_endpoint: %s ' % bucket_info.extranet_endpoint)
        print('owner: %s  ' % bucket_info.owner.id)
        print('grant: %s  ' % bucket_info.acl.grant)

    def add_contents(self,keys,contents):
        '''
       向bucket内的文件添加内容
       bucket内的文件可以存在也可以不存在
       当文件不存在时，则增加文件
       当文件存在时，则覆盖原来文件内容
        '''
        result = self.__bucket.put_object(keys, contents, progress_callback=self.__percentage)
        # HTTP返回码。
        # print('http status: {0}'.format(result.status))
        # 请求ID。请求ID是请求的唯一标识，强烈建议在程序日志中添加此参数。
        # print('request_id: {0}'.format(result.request_id))
        # ETag是put_object方法返回值特有的属性。
        # print('ETag: {0}'.format(result.etag))
        # HTTP响应头部。
        # print('date: {0}'.format(result.headers['date']))

    def append_contents(self,keys,contents_list):
        '''
        追加的形式向bucket内的文件添加内容
        bucket内的文件存在则会抛出异常
        当文件不存在时，则增加文件
        '''
        next_position = 0
        for contents in contents_list:
            result=self.__bucket.append_object(keys,next_position,contents)
            next_position = result.next_position

    def  stream_download(self,keys,download_path=settings.Params['default_download_path']):
        '''
        流试下载
        获取keys的文件流，赋给目标文件
        '''
        stream_obj=self.__bucket.get_object(keys)
        try:
            with open('%s/%s' % (download_path,keys.split('/')[-1:][0]),'wb') as file:
                shutil.copyfileobj(stream_obj,file)
        except FileNotFoundError:
                print('无法找到默认下载目录["%s"]，请确认是否存在' % settings.Params['default_download_path'])
                exit(901)

    def download(self,keys,download_path=settings.Params['default_download_path']):
        '''
        断点下载的方式下载
        下载的文件小于10M时，使用的是get_object方法
        '''
        oss2.resumable_download(self.__bucket,keys,'%s/%s' % (download_path,keys.split('/')[-1:][0]),progress_callback=self.__percentage)
