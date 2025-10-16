#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
from pathlib import Path 

project_root =Path (__file__ ).parent .parent 
sys .path .insert (0 ,str (project_root ))

from src .core .converter import BilibiliVideoConverter 
from src .utils .config import config 


def main ():
    print ("="*60 )
    print ("Bilibili 缓存视频转换工具")
    print ("="*60 )

    try :
        cache_dir =Path (config .bilibili_cache_dir )

        output_dir =Path (config .video_output_dir )

        print (f"\n配置信息:")
        print (f"  缓存目录: {cache_dir }")
        print (f"  输出目录: {output_dir }")
        print (f"\n文件命名规则: groupTitle_title.mp4")
        print (f"提示: 所有视频将保存在同一目录下")
        print ()

        response =input ("是否开始转换? (y/n): ").strip ().lower ()
        if response !='y':
            print ("已取消")
            return 

        converter =BilibiliVideoConverter ()
        success ,fail =converter .convert_batch (
        cache_root =cache_dir ,
        output_root =output_dir ,
        keep_structure =False 
        )

        print ("\n"+"="*60 )
        print ("转换完成!")
        print (f"  成功: {success } 个")
        print (f"  失败: {fail } 个")
        print (f"  输出目录: {output_dir }")
        print ("="*60 )

    except Exception as e :
        print (f"\n错误: {e }")
        import traceback 
        traceback .print_exc ()


if __name__ =="__main__":
    main ()
