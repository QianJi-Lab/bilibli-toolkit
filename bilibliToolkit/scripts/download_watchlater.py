#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
from pathlib import Path 

project_root =Path (__file__ ).parent .parent 
sys .path .insert (0 ,str (project_root ))

from src .downloaders .watchlater import BilibiliWatchLaterDownloader 
from src .utils .config import config 


def main ():
    print ("="*60 )
    print ("哔哩哔哩 - 稍后再看自动下载工具")
    print ("="*60 )

    try :
        sessdata =config .get ('BILIBILI_SESSDATA')
        if not sessdata or sessdata =='your_sessdata_here':
            print ("\n❌ 错误: 未配置 BILIBILI_SESSDATA")
            print ("\n💡 获取 SESSDATA 的方法:")
            print ("1. 登录 bilibili.com")
            print ("2. 按 F12 打开开发者工具")
            print ("3. 切换到 Application/存储 标签")
            print ("4. 在 Cookies 中找到 SESSDATA")
            print ("5. 复制其值到 .env 文件中")
            print ("\n或者在浏览器中:")
            print ("1. 登录后访问任意B站页面")
            print ("2. 在地址栏输入: javascript:alert(document.cookie.match(/SESSDATA=([^;]+)/)[1])")
            print ("3. 复制弹出的 SESSDATA 值")
            return 

        download_dir =config .get ('BILIBILI_DOWNLOAD_DIR','downloads/bilibili_watchlater')
        quality =config .get ('BILIBILI_VIDEO_QUALITY','best')
        limit =config .get ('BILIBILI_DOWNLOAD_LIMIT')
        use_aria2 =config .get ('BILIBILI_USE_ARIA2','false').lower ()=='true'

        limit_int =None 
        if limit :
            try :
                limit_int =int (limit )
            except ValueError :
                pass 

        print (f"\n⚙️  配置信息:")
        print (f"   下载目录: {download_dir }")
        print (f"   视频质量: {quality }")
        print (f"   下载限制: {'全部'if not limit_int else f'{limit_int } 个'}")
        print (f"   使用 aria2: {'是'if use_aria2 else '否'}")

        downloader =BilibiliWatchLaterDownloader (
        sessdata =sessdata ,
        download_dir =download_dir ,
        quality =quality ,
        use_aria2 =use_aria2 
        )

        print ("\n"+"="*60 )
        input ("按 Enter 键开始下载...")

        downloader .download_all (limit =limit_int )

        print (f"\n{'='*60 }")
        print ("所有任务完成!")
        print (f"{'='*60 }")

    except KeyboardInterrupt :
        print ("\n\n⚠️  用户中断下载")
    except Exception as e :
        print (f"\n❌ 程序错误: {e }")
        import traceback 
        traceback .print_exc ()


if __name__ =="__main__":
    main ()
