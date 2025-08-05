import os
import random
from PIL import Image, ImageOps

# --- 配置参数 ---

# 1. 图片所在的文件夹名称
IMAGE_DIRECTORY = 'images'

# 2. 输出的拼贴图文件名
OUTPUT_FILENAME = 'my_grid_collage.jpg'

# 3. 网格布局：行数和列数
#    您的要求是 14 行 11 列
GRID_ROWS = 14
GRID_COLS = 11

# 4. 每个网格单元的尺寸（宽度, 高度），单位是像素
#    所有图片都会被裁剪成这个尺寸。您可以根据需要调整。
#    例如 (300, 300) 会产生方形单元格，(400, 300) 会产生长方形单元格。
CELL_SIZE = (460, 215)

# 5. 是否在拼接前随机打乱图片顺序？
#    True 会让每次生成的拼贴图都不同。
#    False 会按照文件名顺序拼接。
SHUFFLE_IMAGES = True

# 6. 输出图片的质量 (1-100, 仅对JPEG格式有效)
IMAGE_QUALITY = 90

def create_grid_collage():
    """主函数，用于创建网格拼贴图"""
    
    # 检查图片数量是否匹配
    total_cells = GRID_ROWS * GRID_COLS
    
    # 获取所有图片文件的路径
    try:
        image_paths = [os.path.join(IMAGE_DIRECTORY, f) for f in os.listdir(IMAGE_DIRECTORY) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
    except FileNotFoundError:
        print(f"错误：找不到名为 '{IMAGE_DIRECTORY}' 的文件夹。请确保脚本旁边有这个文件夹，并且里面放了图片。")
        return

    print(f"找到了 {len(image_paths)} 张图片，网格需要 {total_cells} 张。")

    if len(image_paths) < total_cells:
        print(f"警告：图片数量不足！网格需要 {total_cells} 张，但只找到 {len(image_paths)} 张。剩余的单元格将为空白。")
        # 填充空白路径以匹配单元格总数
        image_paths += [None] * (total_cells - len(image_paths))
    elif len(image_paths) > total_cells:
        print(f"提示：图片数量超出网格所需。将只使用前 {total_cells} 张图片。")
        image_paths = image_paths[:total_cells]

    if SHUFFLE_IMAGES:
        random.shuffle(image_paths)
        print("图片顺序已随机打乱。")
    
    # 计算最终拼贴图的总尺寸
    cell_width, cell_height = CELL_SIZE
    total_width = GRID_COLS * cell_width
    total_height = GRID_ROWS * cell_height
    
    print(f"将创建一张 {total_width}x{total_height} 像素的拼贴图...")

    # 创建一个白色背景的画布
    final_collage = Image.new('RGB', (total_width, total_height), 'white')
    
    # 遍历网格并填充图片
    image_index = 0
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            img_path = image_paths[image_index]
            image_index += 1
            
            if img_path is None:
                continue # 如果图片路径为None，则跳过，保留白色背景

            try:
                # 打开图片
                img = Image.open(img_path).convert('RGB')
                
                # 使用 ImageOps.fit 来实现“居中裁剪”
                # 它会自动缩放并从中心裁剪图片，以精确匹配 CELL_SIZE
                # 这是实现规整网格布局最简单高效的方法
                cropped_img = ImageOps.fit(img, CELL_SIZE, Image.Resampling.LANCZOS)
                
                # 计算粘贴位置
                paste_x = col * cell_width
                paste_y = row * cell_height
                
                # 将裁剪好的图片粘贴到画布上
                final_collage.paste(cropped_img, (paste_x, paste_y))
                
            except Exception as e:
                print(f"警告：无法处理图片 {img_path}。该单元格将为空白。错误: {e}")

        print(f"已完成第 {row + 1}/{GRID_ROWS} 行的处理...")

    # 保存最终的拼贴图
    try:
        final_collage.save(OUTPUT_FILENAME, quality=IMAGE_QUALITY, optimize=True)
        print(f"\n成功！拼贴图已保存为 '{OUTPUT_FILENAME}'")
    except Exception as e:
        print(f"错误：保存文件失败。{e}")


if __name__ == '__main__':
    create_grid_collage()