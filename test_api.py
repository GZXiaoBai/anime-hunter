import requests
import sys
import os
import json

def search_anime(image_path):
    """
    使用 trace.moe API 搜索动漫截图
    """
    api_url = "https://api.trace.moe/search"
    
    if not os.path.exists(image_path):
        print(f"错误: 找不到文件 '{image_path}'")
        return

    print(f"正在上传图片: {image_path} ...")
    
    try:
        with open(image_path, "rb") as image_file:
            # trace.moe API 接受 'image' 字段
            files = {"image": image_file}
            response = requests.post(api_url, files=files)
            
            # 检查 HTTP 状态码
            response.raise_for_status()
            
            # 解析 JSON
            result = response.json()
            
            print("\n--- 搜索成功! ---")
            # 打印完整的返回结果用于调试
            # print(json.dumps(result, indent=4, ensure_ascii=False))
            
            if result.get("error"):
                print(f"API 返回错误: {result['error']}")
                return

            results = result.get("result", [])
            if not results:
                print("未找到匹配的动漫。")
                return

            # 打印相似度最高的前 3 个结果
            print(f"共找到 {len(results)} 个结果，显示前 3 个：\n")
            
            for i, item in enumerate(results[:3]):
                similarity = item.get('similarity', 0) * 100
                filename = item.get('filename', '未知')
                episode = item.get('episode', '未知')
                timestamp = item.get('from', 0)
                
                # 将秒转换为 mm:ss 格式
                minutes = int(timestamp // 60)
                seconds = int(timestamp % 60)
                
                print(f"[{i+1}] 相似度: {similarity:.2f}%")
                print(f"    文件名: {filename}")
                print(f"    集数: {episode}")
                print(f"    时间点: {minutes:02d}:{seconds:02d}")
                print(f"    预览视频: {item.get('video')}")
                print(f"    预览图片: {item.get('image')}")
                print("-" * 30)
                
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    # 检查命令行参数，如果没有提供，则默认寻找 test.jpg
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    else:
        img_path = "test.jpg"
        print("提示: 你可以在命令行运行 `python test_api.py <图片路径>`")
        print(f"当前默认寻找: {img_path}\n")

    search_anime(img_path)
