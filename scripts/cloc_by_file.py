#!/usr/bin/env python3
#!/usr/bin/env python3
import os
import subprocess
import sys

def cloc_directories(root_path, max_depth=1, exclude_dirs=None, include_lang=None):
    """
    统计一级目录下的代码量，支持排除文件夹和指定语言
    
    Args:
        root_path: 根目录路径
        max_depth: 扫描深度（目前固定为1）
        exclude_dirs: 要排除的文件夹名称列表
        include_lang: 只包含的语言（如 'python'）
    """
    if exclude_dirs is None:
        exclude_dirs = ['node_modules', '.git', 'venv', '__pycache__', 'dist', 'build']
    
    for entry in os.scandir(root_path):
        if (entry.is_dir() and 
            not entry.name.startswith('.') and 
            entry.name not in exclude_dirs):
            
            print(f"\n=== {entry.name} ===")
            
            # 构建 cloc 命令
            cmd = ['cloc', entry.path]
            
            # 添加语言过滤
            if include_lang:
                cmd.extend(['--include-lang', include_lang])
            
            # 添加排除目录（如果需要）
            # cloc 原生支持 --exclude-dir，但这里我们在 Python 层面过滤
            
            # 执行命令
            subprocess.run(cmd, check=False)

# 使用示例
if __name__ == "__main__":
    # 定义要排除的文件夹
    exclude_list = [
        'node_modules',
        '.git',
        'venv',
        '__pycache__',
        'dist',
        'build',
        '.vscode',
        'resources',
        'site',
        'log',
        'styles',
        'manual_tests',
        'exp',
        'docs',
        'test'
    ]
    
    # 调用函数
    cloc_directories(
        root_path='.',
        exclude_dirs=exclude_list,
        include_lang='python'
    )
