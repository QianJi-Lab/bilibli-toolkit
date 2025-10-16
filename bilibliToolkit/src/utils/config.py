import os 
from pathlib import Path 
from typing import Optional 


def load_env_file (env_path :Optional [Path ]=None )->dict :
    if env_path is None :

        project_root =Path (__file__ ).parent 
        env_path =project_root /'.env'

    if not env_path .exists ():
        print (f"警告：未找到 .env 文件：{env_path }")
        print (f"提示：请复制 .env.example 为 .env 并填入真实的配置信息")
        return {}

    env_vars ={}

    try :
        with open (env_path ,'r',encoding ='utf-8')as f :
            for line in f :

                line =line .strip ()


                if not line or line .startswith ('#'):
                    continue 


                if '='in line :
                    key ,value =line .split ('=',1 )
                    key =key .strip ()
                    value =value .strip ()


                    if value .startswith ('"')and value .endswith ('"'):
                        value =value [1 :-1 ]
                    elif value .startswith ("'")and value .endswith ("'"):
                        value =value [1 :-1 ]

                    env_vars [key ]=value 

        print (f"✓ 成功加载配置文件：{env_path }")

    except Exception as e :
        print (f"错误：读取 .env 文件失败：{e }")
        return {}

    return env_vars 


class Config :
    def __init__ (self ):

        self .env_vars =load_env_file ()


        for key ,value in self .env_vars .items ():
            if key not in os .environ :
                os .environ [key ]=value 

    def get (self ,key :str ,default :Optional [str ]=None )->Optional [str ]:
        return os .environ .get (key )or self .env_vars .get (key )or default 

    @property 
    def zhipuai_api_key (self )->str :
        api_key =self .get ('ZHIPUAI_API_KEY')
        if not api_key or api_key =='your_api_key_here':
            raise ValueError (
            "未配置 ZHIPUAI_API_KEY！\n"
            "请在 .env 文件中设置有效的 API Key。\n"
            "如果没有 .env 文件，请复制 .env.example 为 .env"
            )
        return api_key 

    @property 
    def bilibili_cache_dir (self )->str :
        return self .get ('BILIBILI_CACHE_DIR',r'xxx')

    @property 
    def temp_output_file (self )->str :
        return self .get ('TEMP_OUTPUT_FILE',r'xxx')

    @property 
    def final_output_file (self )->str :
        return self .get ('FINAL_OUTPUT_FILE',r'xxx')

    @property 
    def zhipuai_model (self )->str :
        return self .get ('ZHIPUAI_MODEL','glm-4-flash')

    @property 
    def zhipuai_temperature (self )->float :
        temp_str =self .get ('ZHIPUAI_TEMPERATURE','0.2')
        try :
            return float (temp_str )
        except ValueError :
            return 0.2 

    @property 
    def video_output_dir (self )->str :
        return self .get ('BILIBILI_DOWNLOAD_DIR',r'xxx')

config =Config ()

if __name__ =='__main__':
    print ("="*60 )
    print ("配置信息测试")
    print ("="*60 )

    try :
        print (f"智谱AI API Key: {config .zhipuai_api_key [:20 ]}... (已隐藏)")
        print (f"Bilibili 缓存目录: {config .bilibili_cache_dir }")
        print (f"临时输出文件: {config .temp_output_file }")
        print (f"最终输出文件: {config .final_output_file }")
        print (f"视频输出目录: {config .video_output_dir }")
        print (f"智谱AI 模型: {config .zhipuai_model }")
        print (f"温度参数: {config .zhipuai_temperature }")
        print ("\n✓ 所有配置加载成功！")
    except ValueError as e :
        print (f"\n✗ 配置错误：{e }")
