import os

# --- 配置区 ---

# 定义一个常见的可作为文本打开的文件扩展名列表
TEXT_FILE_EXTENSIONS = {
    # Web开发
    '.html', '.htm', '.css', '.js', '.jsx', '.ts', '.tsx', '.json', '.vue', '.svelte',
    '.xml', '.svg', '.md', '.markdown', '.yaml', '.yml', '.toml',
    # 脚本与编程
    '.py', '.java', '.c', '.cpp', '.h', '.cs', '.go', '.php', '.rb', '.sh', '.bat',
    # 数据与配置
    '.txt', '.ini', '.cfg', '.conf', '.log', '.sql', '.csv', 
    '.env', '.development', # <--- 【修改点1】新增.env和.development，以包含其内容
    # 其他
    '.gitignore', '.dockerfile', 'license', # 无扩展名的特殊文件
}

def is_text_file(filepath):
    """根据文件扩展名或文件名判断是否为文本文件。"""
    if os.path.basename(filepath).lower() in TEXT_FILE_EXTENSIONS:
        return True
    return os.path.splitext(filepath)[1].lower() in TEXT_FILE_EXTENSIONS


def generate_tree_recursive(dir_path, prefix, output_file, exclude_set):
    """
    使用递归来构建和写入具有连接线的文件树。
    返回在该目录及子目录下找到的文件数量。
    """
    try:
        items = [item for item in os.listdir(dir_path) if item not in exclude_set]
    except FileNotFoundError:
        return 0

    dirs = sorted([d for d in items if os.path.isdir(os.path.join(dir_path, d))])
    files = sorted([f for f in items if os.path.isfile(os.path.join(dir_path, f))])
    
    all_items = dirs + files
    file_count = len(files)

    for i, name in enumerate(all_items):
        is_last = (i == len(all_items) - 1)
        connector = "└── " if is_last else "├── "
        full_path = os.path.join(dir_path, name)

        if os.path.isdir(full_path):
            output_file.write(f"{prefix}{connector}{name}/\n")
            new_prefix = prefix + ("    " if is_last else "│   ")
            file_count += generate_tree_recursive(full_path, new_prefix, output_file, exclude_set)
        else:
            output_file.write(f"{prefix}{connector}{name}\n")
    
    return file_count


def append_files_content(root_dir, output_file, exclude_set):
    """遍历并写入所有文本文件的内容。"""
    output_file.write("\n\n--- 文件内容详情 ---\n")
    
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in exclude_set]
        
        for filename in sorted(filenames):
            full_path = os.path.join(dirpath, filename)
            
            # 【修改点2】新增一个条件，如果文件名是'package-lock.json'则跳过写入内容
            if is_text_file(full_path) and filename != 'PrintPathTxt.py' and filename != 'package-lock.json' and filename != 'PrintData.py':
                relative_path = os.path.relpath(full_path, root_dir)
                header = f"\n\n===================================package-lock.json=====\n📄 文件路径: {relative_path}\n========================================\n\n"
                output_file.write(header)
                
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as content_file:
                        output_file.write(content_file.read())
                except Exception as e:
                    output_file.write(f"[无法读取文件内容: {e}]")

# --- 使用说明 ---

if __name__ == "__main__":
    # 1. 设置你的目标路径
    target_path = os.path.dirname(os.path.abspath(__file__))

    # 2. 设置你想要排除的文件夹名称列表
    folders_to_exclude = ["node_modules", ".git", ".vscode", "dist", "__pycache__", "venv", "output","data",'env','Lib']

    # 3. 动态生成输出文件名
    output_filename = f"{os.path.basename(os.path.abspath(target_path))}_structure_and_content.txt"
    exclude_set = set(folders_to_exclude)

    print(f"正在分析路径: {target_path}")
    print(f"即将生成报告文件: {output_filename}")
    print("这可能需要一些时间，请稍候...")

    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(f"项目路径: {os.path.abspath(target_path)}\n")
            f.write(f"排除的文件夹: {folders_to_exclude}\n")
            f.write("-" * 40 + "\n\n")
            f.write(f"{os.path.basename(os.path.abspath(target_path))}/\n")
            
            total_files = generate_tree_recursive(target_path, "", f, exclude_set)
            
            f.write(f"\n\n---\n分析完毕，共找到 {total_files} 个文件。\n---")
            
            append_files_content(target_path, f, exclude_set)
            
        print(f"\n✅ 成功！项目结构和文件内容已完整写入到: {os.path.abspath(output_filename)}")

    except Exception as e:
        print(f"\n❌ 发生错误: {e}")