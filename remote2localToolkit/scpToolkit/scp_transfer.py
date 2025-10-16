#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict

if sys.platform == 'win32':
    try:
        os.system('chcp 65001 > nul')
    except:
        pass


def clear_screen():
    os.system('cls' if sys.platform == 'win32' else 'clear')


def load_env_file(env_path: str = '.env') -> Dict[str, str]:
    config = {}
    
    if not os.path.exists(env_path):
        print("错误: 找不到 .env 配置文件!")
        print("请确保 .env 文件存在于脚本目录中")
        sys.exit(1)
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
    except Exception as e:
        print(f"错误: 读取配置文件失败: {e}")
        sys.exit(1)
    
    return config


def check_config(config: Dict[str, str]) -> bool:
    required = ['SERVER_IP', 'SERVER_PORT', 'SERVER_USER', 
                'SERVER_PASSWORD', 'LOCAL_PATH', 'SERVER_PATH']
    missing = [key for key in required if not config.get(key)]
    
    if missing:
        print("错误: 以下必需配置项未设置:")
        for item in missing:
            print(f"  - {item}")
        return False
    
    return True


def show_menu(config: Dict[str, str]):
    print()
    print("================================")
    print("    SCP 文件传输工具")
    print("================================")
    print()
    print("当前配置:")
    print(f"  服务器: {config['SERVER_USER']}@{config['SERVER_IP']}:{config['SERVER_PORT']}")
    print(f"  本地路径: {config['LOCAL_PATH']}")
    print(f"  服务器路径: {config['SERVER_PATH']}")
    print()
    print("请选择操作:")
    print("  1. 从服务器下载文件到本地")
    print("  2. 从本地上传文件到服务器")
    print("  3. 退出")
    print()


def check_scp_available() -> Optional[str]:
    if shutil.which('scp'):
        return 'scp'
    if shutil.which('pscp'):
        return 'pscp'
    return None


def transfer_with_scp(source: str, destination: str, config: Dict[str, str], 
                      direction: str) -> bool:
    scp_tool = check_scp_available()
    
    if not scp_tool:
        print("错误: 未找到 scp 或 pscp 命令")
        return False
    
    print("提示: scp 命令需要手动输入密码")
    print(f"密码: {config['SERVER_PASSWORD']}")
    print()
    
    if scp_tool == 'scp':
        cmd = [
            'scp',
            '-P', config['SERVER_PORT'],
            '-r',
            '-v'
        ]
    else:
        cmd = [
            'pscp',
            '-P', config['SERVER_PORT'],
            '-pw', config['SERVER_PASSWORD'],
            '-r'
        ]
    
    if direction == 'download':
        remote_path = f"{config['SERVER_USER']}@{config['SERVER_IP']}:{source}"
        cmd.append(remote_path)
        cmd.append(destination)
    else:
        remote_path = f"{config['SERVER_USER']}@{config['SERVER_IP']}:{destination}"
        cmd.append(source)
        cmd.append(remote_path)
    
    cmd_str = ' '.join(cmd if scp_tool == 'scp' else [c for c in cmd if c != config['SERVER_PASSWORD']])
    print(f"执行命令: {cmd_str}")
    print()
    print("正在传输文件...")
    print("-----------------------------------")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'
        )
        
        for line in process.stdout:
            print(line.rstrip())
        
        return_code = process.wait()
        
        print("-----------------------------------")
        
        if return_code == 0:
            print("传输完成!")
            return True
        else:
            print("传输失败!")
            return False
            
    except KeyboardInterrupt:
        print("\n传输被用户中断")
        return False
    except Exception as e:
        print(f"传输失败: {e}")
        return False


def execute_transfer(direction: str, config: Dict[str, str]):
    if direction == 'download':
        source = config['SERVER_PATH']
        destination = config['LOCAL_PATH']
        print("\n开始从服务器下载文件...")
    else:
        source = config['LOCAL_PATH']
        destination = config['SERVER_PATH']
        print("\n开始上传文件到服务器...")
    
    print(f"源: {source}")
    print(f"目标: {destination}")
    print()
    
    success = False
    
    scp_tool = check_scp_available()
    if scp_tool:
        print(f"使用 {scp_tool.upper()} 进行传输...")
        success = transfer_with_scp(source, destination, config, direction)
    else:
        print("\n错误: 所有传输方法均失败")
        print("请安装以下工具之一:")
        print("  1. OpenSSH Client (scp)")
        print("  2. PuTTY (pscp.exe)")
    
    print()
    input("按 Enter 键返回菜单...")


def main():
    config = load_env_file()
    
    if not check_config(config):
        sys.exit(1)
    
    while True:
        clear_screen()
        show_menu(config)
        
        try:
            choice = input("请输入选项 (1-3): ").strip()
            
            if choice == '1':
                execute_transfer('download', config)
            elif choice == '2':
                execute_transfer('upload', config)
            elif choice == '3':
                print("退出程序...")
                sys.exit(0)
            else:
                print("无效选项，请重新选择")
                input("按 Enter 继续...")
                
        except KeyboardInterrupt:
            print()
            print("程序被用户中断")
            sys.exit(0)
        except Exception as e:
            print(f"发生错误: {e}")
            input("按 Enter 继续...")


if __name__ == '__main__':
    main()
