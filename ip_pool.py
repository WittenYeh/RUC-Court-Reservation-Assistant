import requests
import time
from bs4 import BeautifulSoup

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36 Edg/81.0.416.64'
}

ip_dict = {}  # 保存能够使用的IP完整形式


def get_info(url):  # 请求网页
    r = requests.get(url, headers=header)
    r.raise_for_status()
    r.encoding = 'utf-8'
    return r
    


# <tr>
#     <td data-title="IP">36.249.49.38</td>
#     <td data-title="PORT">9999</td>
#     <td data-title="匿名度">高匿名</td>
#     <td data-title="类型">HTTP</td>
#     <td data-title="位置">福建省泉州市  联通</td>
#     <td data-title="响应速度">0.3秒</td>
#     <td data-title="最后验证时间">2020-04-29 10:31:01</td>
# </tr>
def get_ip_dict(url):
    soup = BeautifulSoup(get_info(url).text, 'html.parser')
    for info_list in soup.find_all('tr')[1:]:
        soup1 = BeautifulSoup(str(info_list), 'html.parser')
        IP = soup1.find('td', attrs={'data-title': "IP"}).string
        PORT = soup1.find('td', attrs={'data-title': "PORT"}).string
        TYPE = soup1.find('td', attrs={'data-title': "类型"}).string
        ip_dict[IP] = TYPE + '://' + IP + ':' + PORT
        time.sleep(0.1)


def check_ip():  # 检查IP是否可用
    for IP in list(ip_dict.keys()):
        try:
            r = requests.get('https://www.baidu.com/', proxies={'http': ip_dict[IP]}, headers=header, timeout=0.1)
            r.raise_for_status()
        except:
            del ip_dict[IP]
    print('已对所有IP进行检测，延时不超过 0.1 秒的有 {} 个。'.format(len(ip_dict)))


def get_main_url():  
    url = 'https://www.kuaidaili.com/free/'
    for page_num in range(1, 6):
        URL = url + 'inha/{}/'.format(page_num)
        get_ip_dict(URL)
        time.sleep(1)
    print('所有IP信息已准备就绪，共 {} 个。'.format(len(ip_dict)))


if __name__ == '__main__':
    get_main_url()
    check_ip()

