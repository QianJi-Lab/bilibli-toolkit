import json 
import subprocess 
from pathlib import Path 
from typing import Optional ,Tuple ,List ,Dict 
from src .utils .config import config 


class BilibiliVideoConverter :
    def __init__ (self ,ffmpeg_path :str ="ffmpeg"):
        self .ffmpeg_path =ffmpeg_path 
        self ._check_ffmpeg ()

    def _check_ffmpeg (self )->bool :
        try :
            result =subprocess .run (
            [self .ffmpeg_path ,"-version"],
            capture_output =True ,
            text =True ,
            encoding ='utf-8',
            errors ='replace',
            check =True 
            )
            print (f"✓ FFmpeg 已就绪: {result .stdout .split ()[2 ]}")
            return True 
        except (subprocess .CalledProcessError ,FileNotFoundError ):
            print ("✗ 错误: 未找到 FFmpeg")
            print ("\n请安装 FFmpeg:")
            print ("  方法1: 使用 winget 安装 (推荐)")
            print ("    winget install Gyan.FFmpeg")
            print ("\n  方法2: 使用 Chocolatey 安装")
            print ("    choco install ffmpeg")
            print ("\n  方法3: 手动下载")
            print ("    https://www.gyan.dev/ffmpeg/builds/")
            raise RuntimeError ("FFmpeg 未安装或未添加到系统PATH")

    def find_video_audio_files (self ,cache_dir :Path )->Tuple [Optional [Path ],Optional [Path ]]:
        m4s_files =list (cache_dir .glob ("*.m4s"))

        if len (m4s_files )<2 :
            return None ,None 


        m4s_files .sort (key =lambda f :f .stat ().st_size ,reverse =True )

        video_file =m4s_files [0 ]
        audio_file =m4s_files [1 ]

        return video_file ,audio_file 

    def get_video_info (self ,cache_dir :Path )->Optional [Dict ]:
        video_info_file =cache_dir /"videoInfo.json"

        if not video_info_file .exists ():
            return None 

        try :
            with open (video_info_file ,'r',encoding ='utf-8')as f :
                return json .load (f )
        except Exception as e :
            print (f"警告: 读取视频信息失败: {e }")
            return None 

    def _remove_bilibili_header (self ,m4s_file :Path ,output_file :Path )->bool :
        try :
            with open (m4s_file ,'rb')as f :

                header =f .read (16 )


                if header [:9 ]==b'000000000':

                    f .seek (9 )
                    with open (output_file ,'wb')as out :
                        out .write (f .read ())
                    return True 
                else :

                    f .seek (0 )
                    with open (output_file ,'wb')as out :
                        out .write (f .read ())
                    return True 
        except Exception as e :
            print (f"警告: 处理文件头失败: {e }")
            return False 

    def convert_single_video (
    self ,
    cache_dir :Path ,
    output_dir :Path ,
    keep_structure :bool =False 
    )->Optional [Path ]:
        video_file ,audio_file =self .find_video_audio_files (cache_dir )

        if not video_file or not audio_file :
            print (f"✗ 跳过 {cache_dir .name }: 未找到完整的视频/音频文件")
            return None 


        video_info =self .get_video_info (cache_dir )

        if not video_info :

            output_filename =f"{cache_dir .name }.mp4"
            target_dir =output_dir 
        else :

            title =video_info .get ('title',cache_dir .name )
            group_title =video_info .get ('groupTitle','')
            p_num =video_info .get ('p',1 )


            title =self ._sanitize_filename (title )
            group_title =self ._sanitize_filename (group_title )


            if group_title and title :
                if group_title ==title :

                    output_filename =f"{group_title }.mp4"
                else :

                    if p_num and p_num >1 :

                        output_filename =f"{group_title }_{title }_P{p_num }.mp4"
                    else :
                        output_filename =f"{group_title }_{title }.mp4"
            elif group_title :
                output_filename =f"{group_title }.mp4"
            elif title :
                output_filename =f"{title }.mp4"
            else :
                output_filename =f"{cache_dir .name }.mp4"


            target_dir =output_dir 


        target_dir .mkdir (parents =True ,exist_ok =True )
        output_file =target_dir /output_filename 


        if output_file .exists ():
            print (f"⊙ 跳过 {output_filename }: 文件已存在")
            return output_file 


        print (f"⚙ 正在转换: {output_filename }")
        print (f"  视频流: {video_file .name } ({video_file .stat ().st_size /1024 /1024 :.1f} MB)")
        print (f"  音频流: {audio_file .name } ({audio_file .stat ().st_size /1024 /1024 :.1f} MB)")


        temp_video =target_dir /f"temp_video_{cache_dir .name }.m4s"
        temp_audio =target_dir /f"temp_audio_{cache_dir .name }.m4s"

        try :

            print (f"  处理文件头...")
            if not self ._remove_bilibili_header (video_file ,temp_video ):
                print (f"✗ 处理视频文件头失败")
                return None 
            if not self ._remove_bilibili_header (audio_file ,temp_audio ):
                print (f"✗ 处理音频文件头失败")
                return None 


            cmd =[
            self .ffmpeg_path ,
            "-i",str (temp_video ),
            "-i",str (temp_audio ),
            "-c","copy",
            "-y",
            str (output_file )
            ]

            result =subprocess .run (
            cmd ,
            capture_output =True ,
            text =True ,
            encoding ='utf-8',
            errors ='replace',
            check =True 
            )

            print (f"✓ 转换成功: {output_file }")
            return output_file 

        except subprocess .CalledProcessError as e :
            print (f"✗ 转换失败: {e }")
            print (f"  错误信息: {e .stderr }")

            if output_file .exists ():
                output_file .unlink ()
            return None 
        finally :

            if temp_video .exists ():
                temp_video .unlink ()
            if temp_audio .exists ():
                temp_audio .unlink ()

    def convert_batch (
    self ,
    cache_root :Path ,
    output_root :Path ,
    keep_structure :bool =True 
    )->Tuple [int ,int ]:
        cache_root =Path (cache_root )
        output_root =Path (output_root )

        if not cache_root .is_dir ():
            raise ValueError (f"缓存目录不存在: {cache_root }")

        output_root .mkdir (parents =True ,exist_ok =True )


        cache_dirs =[d for d in cache_root .iterdir ()if d .is_dir ()and d .name .isdigit ()]

        print (f"\n发现 {len (cache_dirs )} 个缓存视频目录")
        print ("="*60 )

        success_count =0 
        fail_count =0 

        for i ,cache_dir in enumerate (cache_dirs ,1 ):
            print (f"\n[{i }/{len (cache_dirs )}] 处理: {cache_dir .name }")

            result =self .convert_single_video (cache_dir ,output_root ,keep_structure )

            if result :
                success_count +=1 
            else :
                fail_count +=1 

        return success_count ,fail_count 

    @staticmethod 
    def _sanitize_filename (filename :str )->str :
        import re 
        filename =''.join (char for char in filename if ord (char )>=32 and ord (char )!=127 )

        invalid_chars ='<>:"/\\|?*'
        for char in invalid_chars :
            filename =filename .replace (char ,'_')

        filename =filename .strip ('. _')

        filename =re .sub (r'\s+',' ',filename )

        if not filename :
            filename ='untitled'

        if len (filename )>200 :
            filename =filename [:200 ].strip ('. _')

        return filename 


