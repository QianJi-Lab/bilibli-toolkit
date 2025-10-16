#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
from pathlib import Path 

project_root =Path (__file__ ).parent .parent 
sys .path .insert (0 ,str (project_root ))

from src .core .scanner import scan_bilibili_cache 
from src .utils .config import config 


def main ():
    print ("="*60 )
    print ("Bilibili 缓存视频扫描工具")
    print ("="*60 )

    try :
        bilibili_root_dir =config .bilibili_cache_dir 
        temp_output_md =config .temp_output_file 

        print (f"\n读取配置：")
        print (f"  缓存目录: {bilibili_root_dir }")
        print (f"  输出文件: {temp_output_md }")
        print ()

        scan_bilibili_cache (bilibili_root_dir ,temp_output_md )

    except Exception as e :
        print (f"\n错误：{e }")
        import traceback 
        traceback .print_exc ()


if __name__ =="__main__":
    main ()
