from zhipuai import ZhipuAI 
from pathlib import Path 
from src .utils .config import config 

def categorize_with_llm (input_file ,output_file ,api_key ):
    input_path =Path (input_file )
    output_path =Path (output_file )

    if not input_path .is_file ():
        print (f"错误：输入文件 '{input_file }' 不存在。请先运行第一步的脚本。")
        return 



    try :
        with open (input_path ,'r',encoding ='utf-8')as f :
            video_list_content =f .read ()
    except Exception as e :
        print (f"错误：读取文件 '{input_path }' 失败: {e }")
        return 



    print ("\n"+"="*20 +" 调试信息：准备发送的内容 "+"="*20 )
    print (video_list_content )
    print ("="*60 +"\n")



    prompt =f"""
你是一个专业的内容分类助手。我将提供一个 Markdown 格式的 Bilibili 视频缓存列表。列表的每一行都遵循 '[合集标题] - [共有多少集] - [合集总时长] 分钟' 的格式。

请你根据视频的合集标题，对这些视频进行分类。请严格遵循以下两级分类结构输出：

## 第一级：根据视频合集话题进行分类
你需要根据自己的知识，创建合适的话题分类，例如：编程开发、技术前沿、游戏娱乐、影视杂谈、生活记录、美食探店、知识科普、音乐舞蹈等，特别是对于技术方面请你进一步细分。

## 第二级：在每个话题分类下，根据视频时长进行二次分类
- **短视频** (15分钟及以下)
- **中视频** (15到60分钟)
- **长视频** (60分钟以上)

你的最终输出必须是一个结构清晰的 Markdown 多级列表，无需任何额外的解释或前言。

这是需要你分类的视频列表：
---
{video_list_content }
---
"""

    print ("正在调用大语言模型进行分类，请稍候...")


    try :
        client =ZhipuAI (api_key =api_key )
        response =client .chat .completions .create (
        model =config .zhipuai_model ,
        messages =[
        {"role":"user","content":prompt }
        ],
        temperature =config .zhipuai_temperature ,
        )



        print ("\n"+"="*20 +" 调试信息：API返回的完整响应 "+"="*20 )
        print (response )
        print ("="*60 +"\n")

        categorized_content =response .choices [0 ].message .content 



        print ("\n"+"="*20 +" 调试信息：提取到的分类内容 "+"="*20 )

        print (repr (categorized_content ))
        print ("="*60 +"\n")


    except Exception as err :
        print (f"\n错误：调用API失败: {err }")
        print (f"错误类型: {type (err ).__name__ }")
        import traceback 
        traceback .print_exc ()
        return 


    try :
        with open (output_path ,'w',encoding ='utf-8')as f :
            f .write ("# Bilibili 缓存视频分类报告\n\n")
            f .write (categorized_content )
        print (f"分类完成！最终结果已保存到: {output_path }")

    except Exception as e :
        print (f"错误：无法写入最终文件到 '{output_path }'. 错误信息: {e }")

