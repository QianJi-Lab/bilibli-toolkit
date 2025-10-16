import json 
from pathlib import Path 
from src .utils .config import config 

def scan_bilibili_cache (root_directory ,output_file ):
    root_path =Path (root_directory )
    output_path =Path (output_file )

    if not root_path .is_dir ():
        print (f"错误：目录 '{root_directory }' 不存在或不是一个有效的目录。")
        return 

    grouped_data ={}

    print (f"开始遍历目录: {root_path }")
    for item in root_path .iterdir ():
        if item .is_dir ()and item .name .isdigit ():
            video_info_file =item /'videoInfo.json'

            if video_info_file .is_file ():
                try :
                    with open (video_info_file ,'r',encoding ='utf-8')as f :
                        data =json .load (f )

                        group_title =data .get ('groupTitle','').strip ()


                        if not group_title :

                            group_title =data .get ('title','未命名独立视频')

                        duration_sec =data .get ('duration',0 )

                        duration_min =duration_sec /60 


                        if group_title in grouped_data :

                            grouped_data [group_title ]['total_duration']+=duration_min 
                            grouped_data [group_title ]['count']+=1 
                        else :

                            grouped_data [group_title ]={
                            'total_duration':duration_min ,
                            'count':1 
                            }
                        print (f"已处理: {group_title }")

                except json .JSONDecodeError :
                    print (f"警告：文件 '{video_info_file }' JSON 格式错误，已跳过。")
                except Exception as e :
                    print (f"警告：处理文件 '{video_info_file }' 时发生未知错误: {e }")


    final_output_list =[]
    print ("\n开始聚合统计结果...")
    for title ,data in grouped_data .items ():
        p_count =data ['count']

        total_minutes =round (data ['total_duration'],1 )

        formatted_string =f"{title } - {p_count }集 - {total_minutes } 分钟"
        final_output_list .append (formatted_string )
        print (f"聚合结果: {formatted_string }")

    try :
        with open (output_path ,'w',encoding ='utf-8')as f :
            f .write ("# Bilibili 缓存视频合集统计\n\n")

            for info in sorted (final_output_list ):
                f .write (f"- {info }\n")
        print (f"\n处理完成！结果已成功保存到: {output_path }")

    except Exception as e :
        print (f"错误：无法写入文件到 '{output_path }'. 错误信息: {e }")