import os
import random
from PIL import Image, ImageOps

# --- 配置参数 ---

# 1. 图片所在的文件夹名称
IMAGE_DIRECTORY = 'images'

# 2. 输出的拼贴图文件名
OUTPUT_FILENAME = 'my_mixed_grid_collage.jpg'

# 3. 网格布局：行数和列数
GRID_ROWS = 14
GRID_COLS = 11

# 4. 单个网格单元的基础尺寸（宽度, 高度），单位像素
#    大图 (2x2) 的尺寸将是这个尺寸的两倍。
#    建议使用方形尺寸，如 (200, 200) 或 (250, 250)。
CELL_SIZE = (460, 215)

# 5. 【关键参数】要生成多少张占据 4 格 (2x2) 的大图？
#    可以根据喜好调整这个数字。
NUM_LARGE_IMAGES = 8

# 6. 是否在拼接前随机打乱图片顺序？ (强烈建议为 True)
SHUFFLE_IMAGES = True

# 7. 输出图片的质量 (1-100, 仅对JPEG格式有效)
IMAGE_QUALITY = 90

# --- 脚本主逻辑 ---

def create_mixed_grid_collage():
    """主函数，用于创建混合尺寸的网格拼贴图"""
    
    # --- 1. 图片准备和数量检查 ---
    try:
        all_image_paths = [os.path.join(IMAGE_DIRECTORY, f) for f in os.listdir(IMAGE_DIRECTORY) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]
    except FileNotFoundError:
        print(f"错误：找不到名为 '{IMAGE_DIRECTORY}' 的文件夹。")
        return

    # 计算需要的图片总数
    # 每张大图用掉1张图片，但占据4个单元格，相当于替换了4张小图。
    # 所以每增加一张大图，总图片数就减少 3。
    total_images_needed = (GRID_ROWS * GRID_COLS) - (NUM_LARGE_IMAGES * 3)
    
    print(f"配置：{GRID_ROWS}x{GRID_COLS} 网格，包含 {NUM_LARGE_IMAGES} 张大图 (2x2)。")
    print(f"共需要 {total_images_needed} 张图片。")
    print(f"在 '{IMAGE_DIRECTORY}' 文件夹中找到了 {len(all_image_paths)} 张图片。")

    if len(all_image_paths) < total_images_needed:
        print(f"错误：图片数量不足！请提供至少 {total_images_needed} 张图片。")
        return

    if SHUFFLE_IMAGES:
        random.shuffle(all_image_paths)
        print("图片顺序已随机打乱。")
        
    # 截取所需数量的图片
    image_paths_to_use = all_image_paths[:total_images_needed]
    
    # 分配给大图和小图
    large_image_paths = image_paths_to_use[:NUM_LARGE_IMAGES]
    small_image_paths = image_paths_to_use[NUM_LARGE_IMAGES:]

    # --- 2. 网格布局规划 ---
    # 创建一个虚拟网格来追踪被占用的单元格
    grid_map = [[None for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
    placements = []

    # 优先放置大图 (2x2)
    print("\n正在为大图寻找随机位置...")
    for img_path in large_image_paths:
        placed = False
        # 为了避免死循环，设置尝试次数
        for _ in range(100): # 尝试100次寻找一个位置
            # 随机选择一个可能的左上角
            row = random.randint(0, GRID_ROWS - 2)
            col = random.randint(0, GRID_COLS - 2)
            
            # 检查这个 2x2 区域是否都为空
            if (grid_map[row][col] is None and grid_map[row+1][col] is None and
                grid_map[row][col+1] is None and grid_map[row+1][col+1] is None):
                
                # 预定位置
                placement_info = {'path': img_path, 'pos': (row, col), 'size': (2, 2)}
                placements.append(placement_info)
                
                # 在虚拟网格中标记这4个单元格已被占用
                grid_map[row][col] = placement_info
                grid_map[row+1][col] = placement_info
                grid_map[row][col+1] = placement_info
                grid_map[row+1][col+1] = placement_info
                
                placed = True
                break
        if not placed:
            print(f"警告：无法为图片 {os.path.basename(img_path)} 找到一个 2x2 的空位。它将被跳过。")

    # 填充剩余的小图 (1x1)
    print("正在填充剩余的单元格...")
    small_image_idx = 0
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid_map[r][c] is None: # 如果此单元格为空
                if small_image_idx < len(small_image_paths):
                    img_path = small_image_paths[small_image_idx]
                    placement_info = {'path': img_path, 'pos': (r, c), 'size': (1, 1)}
                    placements.append(placement_info)
                    grid_map[r][c] = placement_info # 标记
                    small_image_idx += 1
                else:
                    print(f"警告：规划错误，没有足够的小图来填充位置 ({r},{c})")

    # --- 3. 绘制最终拼贴图 ---
    cell_width, cell_height = CELL_SIZE
    total_width = GRID_COLS * cell_width
    total_height = GRID_ROWS * cell_height
    
    print(f"\n布局规划完成。开始绘制 {total_width}x{total_height} 的最终图像...")
    
    final_collage = Image.new('RGB', (total_width, total_height), 'white')

    for item in placements:
        try:
            img = Image.open(item['path']).convert('RGB')
            
            rows, cols = item['size']
            target_size = (cols * cell_width, rows * cell_height)
            
            # 使用 ImageOps.fit 进行居中裁剪和缩放
            processed_img = ImageOps.fit(img, target_size, Image.Resampling.LANCZOS)
            
            paste_r, paste_c = item['pos']
            paste_pos = (paste_c * cell_width, paste_r * cell_height)
            
            final_collage.paste(processed_img, paste_pos)
        except Exception as e:
            print(f"警告：处理图片 {item['path']} 时出错，跳过。错误: {e}")

    # --- 4. 保存结果 ---
    try:
        final_collage.save(OUTPUT_FILENAME, quality=IMAGE_QUALITY, optimize=True)
        print(f"\n成功！拼贴图已保存为 '{OUTPUT_FILENAME}'")
    except Exception as e:
        print(f"错误：保存文件失败。{e}")

if __name__ == '__main__':
    create_mixed_grid_collage()