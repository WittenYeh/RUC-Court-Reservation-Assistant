import requests
import json

wxkey = 'your_wx_key'

headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) XWEB/9115 Flue',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://33301.koksoft.com',
    'Referer': 'http://33301.koksoft.com/weixinordernewv7.aspx?wxkey=' + wxkey + '&lxbh=Y',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive'
}

def send_order(court_id: int, date_str: str, start_hour_str: str, end_hour_str: str):
    searchparam = {
        "datestring": date_str,
        "cdstring": "Y:" + str(court_id) + "," + start_hour_str + "-" + end_hour_str + ";",
        "paytype": "W"
    }
    
    data = {
        'searchparam': json.dumps(searchparam),
        'wxkey': wxkey,
        'classname': 'saasbllclass.CommonFuntion',
        'funname': 'MemberOrderfromWx'
    }
    
    response = requests.post(
        url='http://33301.koksoft.com/HomefuntionV2json.aspx', 
        headers=headers, 
        data=data,
        verify=False
    )
    print("order request has been sent!")
    return response

def send_confirm(order_id: str, money: str):
    data = {
        'wxkey': wxkey,
        'attach': 'guestorder|001|33301',
        'out_trade_no': order_id,
        'payje': money,
        'goodsshuoming': '预订付费'
    }
    response = requests.post(
        url='http://33301.koksoft.com/HomefuntionV2json.aspx', 
        headers=headers, 
        data=data,
        verify=False
    )
    print("confirm request has been sent! ")
    return response

resp_text = send_order(7, "2024-5-13", "9:00", "10:00").text
resp_arr = resp_text.split(",")
order_id = resp_arr[1].strip('\"')
money = resp_arr[2]
print("order_id: ", order_id, "money: ", money)
resp_text = send_confirm(order_id, money).text
print(resp_text)