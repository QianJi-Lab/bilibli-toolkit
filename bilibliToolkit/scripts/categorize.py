#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys 
from pathlib import Path 

project_root =Path (__file__ ).parent .parent 
sys .path .insert (0 ,str (project_root ))

from src .core .categorizer import categorize_with_llm 
from src .utils .config import config 


def main ():
    print ("="*60 )
    print ("Bilibili 缓存视频智能分类工具")
    print ("="*60 )

    try :
        temp_input_md =config .temp_output_file 
        final_output_md =config .final_output_file 
        api_key =config .zhipuai_api_key 

        print (f"\n读取配置：")
        print (f"  输入文件: {temp_input_md }")
        print (f"  输出文件: {final_output_md }")
        print (f"  使用模型: {config .zhipuai_model }")
        print (f"  温度参数: {config .zhipuai_temperature }")
        print ()

        categorize_with_llm (temp_input_md ,final_output_md ,api_key )

    except ValueError as e :
        print (f"\n配置错误：{e }")
        print ("\n请检查 .env 文件是否存在并包含有效的配置信息。")
    except Exception as e :
        print (f"\n未知错误：{e }")
        import traceback 
        traceback .print_exc ()


if __name__ =="__main__":
    main ()
