import requests
from datetime import datetime, timedelta
from alive_progress import alive_bar
import sys
import re
import json
import time
from gzhlogin import gzhlogin
    
class Assistant:
    def __init__(self, begin_time) -> None:
        self.is_init = False
        self.begin_time = begin_time # like 2024-5-20-8:00
        """_summary_
        @court_id: a single number between 1 to 10
        @start_time: start time stamp with format "%Y-%m-%d-%H"
        @end_time: end time stamp with format "%Y-%m-%d-%H"
        """
        self.session = gzhlogin()
        
    def check_params(self, court_id: int, start_time_str: str, end_time_str: str) -> None:
        if court_id < 1 or court_id > 10:
            raise Exception("invalid court id")
        try:
            format_str = "%Y-%m-%d-%H"
            start_time = datetime.strptime(start_time_str, format_str)
            end_time = datetime.strptime(end_time_str, format_str)
        except ValueError:
            raise Exception("invalid time string")
        cur_time = datetime.now()
        if start_time < cur_time or start_time > cur_time + timedelta(days=2):
            raise Exception("The system only allows a maximum of 2 days in advance for booking the court")
        elif start_time > end_time:
            raise Exception("end_time should be later than start_time")
        # only permitted to book court between 8:00 and 22:00
        elif start_time.hour < 8:
            raise Exception("too early start_time")
        elif end_time.hour > 22:
            raise Exception("too late end_time")
        return start_time.date().strftime("%Y-%m-%d"), start_time.hour, end_time.hour
        
    def get_wx_key(self):
        url = 'http://33301.koksoft.com/selectlxbh2.aspx'
        params = {
            'qgcode': '33301',
            'code': '071UWxFa1I8jqH06TpJa1U56ka0UWxFr', # need to custommed
            'state': '1'
        }
        headers = {
            'Host': '33301.koksoft.com',
            'Upgrade-Insecure-Request': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9115 Flue',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
        # request #0
        response = self.session.get(url, params=params, headers=headers, cookies=self.session.cookies)
        print("request #0 has been sent successfully! ")
        # extract wxkey 
        wxkey_pattern = r'var wxkey="(.*?)"'
        wxkey_match = re.search(wxkey_pattern, response.text)
        if wxkey_match:
            self.wxkey = wxkey_match.group(1).strip()
        else:
            raise Exception("html response does not contain wxkey")
        # extract params
        qgbh_pattern = r'qgbh : \'(.*?)\''
        qgbh_match = re.search(qgbh_pattern, response.text, re.DOTALL)
        if qgbh_match:
            self.qgbh = qgbh_match.group(1).strip()
        else:
            raise Exception("html response does not contain params")
        print("wxkey is ", self.wxkey, ", params is ", self.qgbh)
        
        # # headers of request #2
        # headers = {
        #     'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     'X-Requested-With': 'XMLHttpRequest',
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9115 Flue',
        #     'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     'Origin': 'http://33301.koksoft.com',
        #     'Referer': 'http://33301.koksoft.com/selectlxbh2.aspx?' + 'qgcode=' + params['qgcode'] + '&code=' + params['code'] + '&state=' + params['state'],
        #     'Accept-Encoding': 'gzip, deflate',
        #     'Accept-Language': 'zh-CN,zh;q=0.9',
        #     'Connection': 'keep-alive'
        # }
        
        # searchparams = {
        #     "qgbh": qgbh
        # }
        # data = {
        #     'searchparam': json.dumps(searchparams),
        #     'wxkey': wxkey,
        #     'classname': 'saasbllclass.CommonFuntion',
        #     'funname': 'GetWebsaleitem'
        # }
        # print(data)
        # # request #2
        # response = requests.post(url, headers=headers, data=data)
        # print(response.text)
        # print("request #1 has been sent successfully! ")
    
    def send_order(self, court_id: int, date_str: str, start_hour_str: str, end_hour_str: str):
        searchparam = {
            "datestring": date_str,
            "cdstring": "Y:" + str(court_id) + "," + start_hour_str + "-" + end_hour_str + ";",
            "paytype": "W"
        }
        
        data = {
            'searchparam': json.dumps(searchparam),
            'wxkey': 'BE0D8A6BD35CB128088C98CC335C6EBAF3119F37382EA08D692663370C022EF60EB3ADE0230D237751E4CDED99BFAB9CB72BF4C5609308312EC196AB50307E66A0F5AFB149240C482271F454F94B8559A176E464E674E6E6C574DB887C1796483258F2A15F6E4DA83AD81B0D453F598F',
            'classname': 'saasbllclass.CommonFuntion',
            'funname': 'MemberOrderfromWx'
        }
        
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9115 Flue',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://33301.koksoft.com',
            'Referer': 'http://33301.koksoft.com/weixinordernewv7.aspx?wxkey=' + self.wxkey + '&lxbh=Y',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive'
        }
        
        response = self.session.post(
            url='http://33301.koksoft.com/HomefuntionV2json.aspx', 
            headers=headers, 
            data=data,
            verify=False,
            cookies=self.session.cookies
        )
        print("order request has been sent!")
        return response
    
    def delegate(self, court_id: int, start_time_str: str, end_time_str: str):
        current_date = datetime.now().date()
        # target_time is the time to sent request
        target_time = datetime.combine(current_date, datetime.strptime(self.begin_time, "%Y-%m-%d-%H:%M").time())
        current_time = datetime.now()
        time_difference = target_time - current_time
        print("current time: ", current_time, "target time: ", target_time)
        
        with alive_bar(int(time_difference.total_seconds() * 100), title="Coundown to " + self.begin_time) as bar:
            while current_time < target_time:
                current_time = datetime.now()
                remaining_time = target_time - current_time
                if remaining_time.total_seconds() < 180 and not self.is_init:
                    self.is_init = True
                    self.get_wx_key()
                time.sleep(0.01)
                bar()
        date_str, start_hour, end_hour = self.check_params(court_id=court_id, start_time_str=start_time_str, end_time_str=end_time_str)
        response = self.send_order(court_id=court_id, date_str=date_str, start_hour_str=str(start_hour)+":00", end_hour_str=str(end_hour)+":00")
        print(response.text)
        
if __name__ == "__main__":
    assistant = Assistant("2024-5-12-20:49")
    assistant.delegate(8, "2024-5-14-8", "2024-5-14-9")