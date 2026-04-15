import os
import stat

def list_files(directory):
    """
    列出目录下的文件及其基本属性
    Args:
        directory: 目录路径
    Returns:
        包含文件信息的列表
    """
    if not os.path.exists(directory):
        return f"错误：目录 '{directory}' 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：'{directory}' 不是一个目录"
    
    files_info = []
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        item_stat = os.stat(item_path)
        
        # 获取文件类型
        if os.path.isdir(item_path):
            file_type = "目录"
        elif os.path.isfile(item_path):
            file_type = "文件"
        else:
            file_type = "其他"
        
        # 获取文件大小（字节）
        file_size = item_stat.st_size
        
        # 获取权限信息
        file_mode = stat.filemode(item_stat.st_mode)
        
        # 获取修改时间
        mod_time = item_stat.st_mtime
        
        files_info.append({
            "name": item,
            "type": file_type,
            "size": file_size,
            "mode": file_mode,
            "modified": mod_time
        })
    
    return files_info

def rename_file(directory, old_name, new_name):
    """
    修改目录下文件的名字
    Args:
        directory: 目录路径
        old_name: 旧文件名
        new_name: 新文件名
    Returns:
        操作结果
    """
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, new_name)
    
    if not os.path.exists(old_path):
        return f"错误：文件 '{old_name}' 不存在"
    
    if os.path.exists(new_path):
        return f"错误：文件 '{new_name}' 已存在"
    
    try:
        os.rename(old_path, new_path)
        return f"成功：文件 '{old_name}' 已重命名为 '{new_name}'"
    except Exception as e:
        return f"错误：重命名失败 - {str(e)}"

def delete_file(directory, filename):
    """
    删除目录下的文件
    Args:
        directory: 目录路径
        filename: 文件名
    Returns:
        操作结果
    """
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        return f"错误：文件 '{filename}' 不存在"
    
    if not os.path.isfile(file_path):
        return f"错误：'{filename}' 不是一个文件"
    
    try:
        os.remove(file_path)
        return f"成功：文件 '{filename}' 已删除"
    except Exception as e:
        return f"错误：删除失败 - {str(e)}"

def create_file(directory, filename, content):
    """
    在目录下新建文件并写入内容
    Args:
        directory: 目录路径
        filename: 文件名
        content: 文件内容
    Returns:
        操作结果
    """
    if not os.path.exists(directory):
        return f"错误：目录 '{directory}' 不存在"
    
    if not os.path.isdir(directory):
        return f"错误：'{directory}' 不是一个目录"
    
    file_path = os.path.join(directory, filename)
    
    if os.path.exists(file_path):
        return f"错误：文件 '{filename}' 已存在"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功：文件 '{filename}' 已创建并写入内容"
    except Exception as e:
        return f"错误：创建文件失败 - {str(e)}"

def read_file(directory, filename):
    """
    读取目录下文件的内容
    Args:
        directory: 目录路径
        filename: 文件名
    Returns:
        文件内容或错误信息
    """
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        return f"错误：文件 '{filename}' 不存在"
    
    if not os.path.isfile(file_path):
        return f"错误：'{filename}' 不是一个文件"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"错误：读取文件失败 - {str(e)}"
