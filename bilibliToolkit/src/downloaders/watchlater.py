import os 
import sys 
import json 
import time 
import subprocess 
from pathlib import Path 
from typing import List ,Dict ,Optional 
from datetime import datetime 
import requests 


if sys .platform =='win32':
    import io 
    sys .stdout =io .TextIOWrapper (sys .stdout .buffer ,encoding ='utf-8',errors ='replace')
    sys .stderr =io .TextIOWrapper (sys .stderr .buffer ,encoding ='utf-8',errors ='replace')


class BilibiliWatchLaterDownloader :
    # 感谢b站前辈留下的api
    WATCHLATER_API ="https://api.bilibili.com/x/v2/history/toview"
    VIDEO_INFO_API ="https://api.bilibili.com/x/web-interface/view"

    def __init__ (self ,
    sessdata :str ,
    download_dir :str ,
    quality :str ="best",
    concurrent :int =1 ,
    use_aria2 :bool =False ):

        self .sessdata =sessdata 
        self .download_dir =Path (download_dir )
        self .quality =quality 
        self .concurrent =concurrent 
        self .use_aria2 =use_aria2 

        self .download_dir .mkdir (parents =True ,exist_ok =True )

        self .download_record_file =self .download_dir /".download_history.json"
        self .download_history =self ._load_download_history ()

        self .stats ={
        "total":0 ,
        "downloaded":0 ,
        "skipped":0 ,
        "failed":0 ,
        "errors":[]
        }

    def _load_download_history (self )->Dict :
        if self .download_record_file .exists ():
            try :
                with open (self .download_record_file ,'r',encoding ='utf-8')as f :
                    return json .load (f )
            except Exception as e :
                print (f"⚠️  加载下载历史失败: {e }")
                return {}
        return {}

    def _save_download_history (self ):
        try :
            with open (self .download_record_file ,'w',encoding ='utf-8')as f :
                json .dump (self .download_history ,f ,ensure_ascii =False ,indent =2 )
        except Exception as e :
            print (f"⚠️  保存下载历史失败: {e }")

    def _get_cookies (self )->str :
        return f"SESSDATA={self .sessdata }"

    def _check_ytdlp_installed (self )->bool :
        try :
            result =subprocess .run (
            ["yt-dlp","--version"],
            capture_output =True ,
            text =True ,
            timeout =5 
            )
            return result .returncode ==0 
        except (subprocess .TimeoutExpired ,FileNotFoundError ):
            return False 

    def get_watchlater_list (self )->List [Dict ]:
        print ("📡 正在获取稍后再看列表...")

        headers ={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Cookie":f"SESSDATA={self .sessdata }",
        "Referer":"https://www.bilibili.com"
        }

        try :
            response =requests .get (
            self .WATCHLATER_API ,
            headers =headers ,
            timeout =10 
            )
            response .raise_for_status ()

            data =response .json ()

            if data .get ("code")!=0 :
                error_msg =data .get ("message","未知错误")
                print (f"❌ 获取列表失败: {error_msg }")
                if "未登录"in error_msg or "登录"in error_msg :
                    print ("💡 提示: 请检查 SESSDATA 是否有效")
                return []

            videos =data .get ("data",{}).get ("list",[])
            print (f"✅ 成功获取 {len (videos )} 个视频")

            return videos 

        except requests .RequestException as e :
            print (f"❌ 网络请求失败: {e }")
            return []
        except Exception as e :
            print (f"❌ 获取列表时发生错误: {e }")
            return []

    def _format_video_info (self ,video :Dict )->Dict :
        return {
        "bvid":video .get ("bvid",""),
        "aid":video .get ("aid",0 ),
        "title":video .get ("title","未知标题").replace ("/","-").replace ("\\","-"),
        "owner":video .get ("owner",{}).get ("name","未知UP主"),
        "duration":video .get ("duration",0 ),
        "pic":video .get ("pic",""),
        "desc":video .get ("desc",""),
        "pubdate":video .get ("pubdate",0 ),
        "url":f"https://www.bilibili.com/video/{video .get ('bvid','')}"
        }

    def _is_already_downloaded (self ,bvid :str )->bool :
        return bvid in self .download_history 

    def _sanitize_filename (self ,filename :str )->str :
        import re 
        filename =''.join (char for char in filename if ord (char )>=32 and ord (char )!=127 )

        illegal_chars ='<>:"/\\|?*'
        for char in illegal_chars :
            filename =filename .replace (char ,"_")

        filename =filename .strip ('. _')

        filename =re .sub (r'\s+',' ',filename )

        if not filename :
            filename ='untitled'

        if len (filename )>200 :
            filename =filename [:200 ].strip ('. _')

        return filename 

    def _rename_and_cleanup (self ,bvid :str ,temp_filename_base :str )->Optional [Path ]:
        try :

            json_file =self .download_dir /f"{temp_filename_base }.info.json"
            mp4_file =self .download_dir /f"{temp_filename_base }.mp4"

            if not mp4_file .exists ():
                print (f"    ⚠️  未找到下载的 MP4 文件")

                self ._cleanup_temp_files (temp_filename_base )
                return None 

            group_title =""
            title =""

            if json_file .exists ():
                try :
                    with open (json_file ,'r',encoding ='utf-8')as f :
                        video_data =json .load (f )

                        title =video_data .get ('title','').strip ()

                        group_title =video_data .get ('uploader','').strip ()

                        if not group_title :
                            group_title =video_data .get ('channel','').strip ()

                        if not group_title :
                            group_title =video_data .get ('uploader_id','').strip ()
                except Exception as e :
                    print (f"    ⚠️  读取 JSON 失败: {e }")

            if group_title and title :
                if group_title ==title :

                    new_filename =f"{self ._sanitize_filename (title )}.mp4"
                else :

                    new_filename =f"{self ._sanitize_filename (group_title )}_{self ._sanitize_filename (title )}.mp4"
            elif group_title :

                new_filename =f"{self ._sanitize_filename (group_title )}.mp4"
            elif title :

                new_filename =f"{self ._sanitize_filename (title )}.mp4"
            else :

                print (f"    ⚠️  未找到标题信息，使用 BVID: {bvid }")
                new_filename =f"{bvid }.mp4"

            new_filepath =self .download_dir /new_filename 


            counter =1 
            original_filename =new_filename 
            while new_filepath .exists ()and new_filepath !=mp4_file :
                name_without_ext =original_filename .rsplit ('.mp4',1 )[0 ]
                new_filename =f"{name_without_ext }_{counter }.mp4"
                new_filepath =self .download_dir /new_filename 
                counter +=1 


            if mp4_file !=new_filepath :
                mp4_file .rename (new_filepath )
                print (f"    ✅ 重命名为: {new_filename }")
            else :
                print (f"    ✅ 文件名: {new_filename }")


            self ._cleanup_temp_files (temp_filename_base )

            return new_filepath 

        except Exception as e :
            print (f"    ⚠️  重命名和清理失败: {e }")
            import traceback 
            traceback .print_exc ()

            try :
                self ._cleanup_temp_files (temp_filename_base )
            except :
                pass 
            return None 

    def _cleanup_temp_files (self ,temp_filename_base :str ):

        cleanup_patterns =[
        f"{temp_filename_base }.info.json",
        f"{temp_filename_base }.description",
        f"{temp_filename_base }.annotations.xml",
        f"{temp_filename_base }.jpg",
        f"{temp_filename_base }.png",
        f"{temp_filename_base }.webp",
        f"{temp_filename_base }.jpeg",
        f"{temp_filename_base }.live_chat.json",
        f"{temp_filename_base }.*.jpg",
        f"{temp_filename_base }.*.png",
        f"{temp_filename_base }.*.webp",
        ]

        cleaned_count =0 
        for pattern in cleanup_patterns :

            if '*'in pattern :

                for file_to_remove in self .download_dir .glob (pattern ):
                    try :
                        file_to_remove .unlink ()
                        cleaned_count +=1 
                    except Exception as e :
                        print (f"    ⚠️  删除 {file_to_remove .name } 失败: {e }")
            else :

                file_to_remove =self .download_dir /pattern 
                if file_to_remove .exists ():
                    try :
                        file_to_remove .unlink ()
                        cleaned_count +=1 
                    except Exception as e :
                        print (f"    ⚠️  删除 {pattern } 失败: {e }")

        if cleaned_count >0 :
            print (f"    🧹 已清理 {cleaned_count } 个无用文件")

    def download_video (self ,video_info :Dict )->bool :

        bvid =video_info ["bvid"]
        title =video_info ["title"]
        url =video_info ["url"]

        if self ._is_already_downloaded (bvid ):
            print (f"⏭️  跳过已下载: {title }")
            self .stats ["skipped"]+=1 
            return True 

        temp_filename_base =f"temp_{bvid }"
        output_template =str (self .download_dir /f"{temp_filename_base }.%(ext)s")

        print (f"\n📥 正在下载: {title }")
        print (f"    链接: {url }")

        cmd =[
        "yt-dlp",
        "--add-header",f"Cookie: SESSDATA={self .sessdata }",
        "--add-header","Referer: https://www.bilibili.com",
        "--output",output_template ,
        "--merge-output-format","mp4",
        "--write-thumbnail",
        "--write-description",
        "--write-info-json",
        "--no-playlist",
        ]

        if self .quality =="best":
            cmd .extend (["--format","bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"])
        elif self .quality =="1080p":
            cmd .extend (["--format","bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]"])
        elif self .quality =="720p":
            cmd .extend (["--format","bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"])
        elif self .quality =="480p":
            cmd .extend (["--format","bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"])
        if self .use_aria2 :
            cmd .extend (["--external-downloader","aria2c"])

        cmd .append (url )

        try :
            result =subprocess .run (
            cmd ,
            capture_output =True ,
            text =True ,
            encoding ='utf-8',
            errors ='replace'
            )

            if result .returncode ==0 :
                print (f"✅ 下载成功: {title }")


                final_file =self ._rename_and_cleanup (bvid ,temp_filename_base )

                if final_file :

                    self .download_history [bvid ]={
                    "title":title ,
                    "filename":final_file .name ,
                    "download_time":datetime .now ().isoformat (),
                    "url":url 
                    }
                    self ._save_download_history ()

                    self .stats ["downloaded"]+=1 
                    return True 
                else :
                    print (f"    ⚠️  下载成功但重命名失败")
                    self .stats ["downloaded"]+=1 
                    return True 
            else :
                error_msg =result .stderr if result .stderr else result .stdout 
                print (f"❌ 下载失败: {title }")
                print (f"    错误信息: {error_msg [:200 ]}")

                self .stats ["failed"]+=1 
                self .stats ["errors"].append ({
                "title":title ,
                "error":error_msg [:500 ]
                })
                return False 

        except subprocess .SubprocessError as e :
            print (f"❌ 下载过程出错: {e }")
            self .stats ["failed"]+=1 
            self .stats ["errors"].append ({
            "title":title ,
            "error":str (e )
            })
            return False 
        except Exception as e :
            print (f"❌ 未知错误: {e }")
            self .stats ["failed"]+=1 
            self .stats ["errors"].append ({
            "title":title ,
            "error":str (e )
            })
            return False 

    def download_all (self ,limit :Optional [int ]=None ):
        if not self ._check_ytdlp_installed ():
            print ("❌ 错误: 未检测到 yt-dlp")
            print ("💡 请先安装 yt-dlp:")
            print ("   pip install yt-dlp")
            print ("   或者: winget install yt-dlp")
            return 

        videos =self .get_watchlater_list ()

        if not videos :
            print ("⚠️  没有找到稍后再看视频")
            return 


        if limit and limit >0 :
            videos =videos [:limit ]
            print (f"⚙️  限制下载数量: {limit }")

        self .stats ["total"]=len (videos )

        print (f"\n{'='*60 }")
        print (f"开始批量下载 (共 {len (videos )} 个视频)")
        print (f"下载目录: {self .download_dir }")
        print (f"视频质量: {self .quality }")
        print (f"{'='*60 }\n")


        for idx ,video in enumerate (videos ,1 ):
            print (f"\n[{idx }/{len (videos )}] ",end ="")

            video_info =self ._format_video_info (video )
            self .download_video (video_info )


            if idx <len (videos ):
                time .sleep (2 )


        self ._generate_report ()

    def _generate_report (self ):
        print (f"\n{'='*60 }")
        print ("下载完成统计")
        print (f"{'='*60 }")
        print (f"总计: {self .stats ['total']} 个视频")
        print (f"✅ 成功下载: {self .stats ['downloaded']} 个")
        print (f"⏭️  跳过(已下载): {self .stats ['skipped']} 个")
        print (f"❌ 下载失败: {self .stats ['failed']} 个")

        if self .stats ['errors']:
            print (f"\n失败详情:")
            for idx ,error in enumerate (self .stats ['errors'][:10 ],1 ):
                print (f"  {idx }. {error ['title']}")
                print (f"     错误: {error ['error'][:100 ]}")


        report_file =self .download_dir /f"download_report_{datetime .now ().strftime ('%Y%m%d_%H%M%S')}.txt"
        try :
            with open (report_file ,'w',encoding ='utf-8')as f :
                f .write (f"下载报告 - {datetime .now ().strftime ('%Y-%m-%d %H:%M:%S')}\n")
                f .write ("="*60 +"\n\n")
                f .write (f"总计: {self .stats ['total']} 个视频\n")
                f .write (f"成功下载: {self .stats ['downloaded']} 个\n")
                f .write (f"跳过: {self .stats ['skipped']} 个\n")
                f .write (f"失败: {self .stats ['failed']} 个\n\n")

                if self .stats ['errors']:
                    f .write ("失败详情:\n")
                    for idx ,error in enumerate (self .stats ['errors'],1 ):
                        f .write (f"{idx }. {error ['title']}\n")
                        f .write (f"   错误: {error ['error']}\n\n")

            print (f"\n📄 详细报告已保存: {report_file }")
        except Exception as e :
            print (f"⚠️  保存报告失败: {e }")

