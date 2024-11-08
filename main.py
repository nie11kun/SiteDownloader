import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import mimetypes

class WebpageDownloader:
    def __init__(self, proxy=None):
        """
        初始化下载器
        
        Args:
            proxy: 代理地址，格式如 'http://127.0.0.1:7890' 或 'socks5://127.0.0.1:1080'
        """
        self.session = requests.Session()
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
    
    def download_webpage(self, url, output_dir):
        """
        下载完整网页及其资源到本地
        
        Args:
            url: 要下载的网页URL
            output_dir: 输出目录路径
        """
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 下载主页面
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"下载主页面失败: {str(e)}")
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 创建资源目录
        resources_dir = os.path.join(output_dir, 'resources')
        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)
        
        # 下载并替换图片
        for img in soup.find_all('img'):
            if img.get('src'):
                img_url = urljoin(url, img['src'])
                try:
                    img_response = self.session.get(img_url, timeout=30)
                    img_response.raise_for_status()
                    
                    # 获取文件扩展名
                    content_type = img_response.headers.get('content-type')
                    ext = mimetypes.guess_extension(content_type) or '.jpg'
                    
                    # 生成本地文件名
                    filename = f"img_{hash(img_url)}{ext}"
                    filepath = os.path.join(resources_dir, filename)
                    
                    # 保存图片
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    
                    # 更新HTML中的图片路径
                    img['src'] = os.path.join('resources', filename)
                    print(f"已下载图片: {img_url}")
                except Exception as e:
                    print(f"下载图片失败 {img_url}: {str(e)}")
        
        # 下载并替换CSS
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                css_url = urljoin(url, link['href'])
                try:
                    css_response = self.session.get(css_url, timeout=30)
                    css_response.raise_for_status()
                    
                    filename = f"style_{hash(css_url)}.css"
                    filepath = os.path.join(resources_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(css_response.text)
                    
                    link['href'] = os.path.join('resources', filename)
                    print(f"已下载CSS: {css_url}")
                except Exception as e:
                    print(f"下载CSS失败 {css_url}: {str(e)}")
        
        # 下载并替换JavaScript
        for script in soup.find_all('script', src=True):
            if script.get('src'):
                js_url = urljoin(url, script['src'])
                try:
                    js_response = self.session.get(js_url, timeout=30)
                    js_response.raise_for_status()
                    
                    filename = f"script_{hash(js_url)}.js"
                    filepath = os.path.join(resources_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(js_response.text)
                    
                    script['src'] = os.path.join('resources', filename)
                    print(f"已下载JavaScript: {js_url}")
                except Exception as e:
                    print(f"下载JavaScript失败 {js_url}: {str(e)}")
        
        # 保存修改后的HTML
        html_filepath = os.path.join(output_dir, 'index.html')
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        return html_filepath

if __name__ == '__main__':
    url = input("请输入要下载的网页URL: ")
    output_dir = input("请输入保存目录路径: ")
    proxy = input("请输入代理地址(为空则不使用代理): ").strip()
    
    try:
        downloader = WebpageDownloader(proxy if proxy else None)
        saved_path = downloader.download_webpage(url, output_dir)
        print(f"\n下载完成！网页已保存到: {saved_path}")
    except Exception as e:
        print(f"下载失败: {str(e)}")