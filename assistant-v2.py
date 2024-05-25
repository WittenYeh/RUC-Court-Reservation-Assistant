
import requests
import json
from datetime import datetime, timedelta
from alive_progress import alive_bar
import time
from fake_useragent import UserAgent
import threading

# Readme will tell you how to set the value
config = {
    'wxkey': 'BE0D8A6BD35CB128088C98CC335C6EBAF3119F37382EA08D692663370C022EF60EB3ADE0230D237751E4CDED99BFAB9CB72BF4C5609308312EC196AB50307E66A0F5AFB149240C482271F454F94B85591A48770FFEAEE1A46A6DF9545891CDE10D930A606506A7C3A7FAA71A82338C14',
    'num_threads': 5,
    'num_attempts': 30, 
    'attempt_interval': 0.5,
    'multi_thread': False,
    'begin_time' : '2024-5-24-07:58:03',  # with format '%Y-%m-%d-%H:%M:%S'
    'court_id': 10,  # id of target court
    'target_date': '2024-5-24',      # with format '%Y-%m-%d"
    'target_start_time': '19:00',        # with format '%H:%M'
    'target_end_time': '21:00',          # with format '%H:%M'
}

def generate_headers(user_agent: str):
# requests headers
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': user_agent,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'http://33301.koksoft.com',
        'Referer': 'http://33301.koksoft.com/weixinordernewv7.aspx?wxkey=' + config['wxkey'] + '&lxbh=Y',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    return headers

def send_order(court_id: int, date_str: str, start_hour_str: str, end_hour_str: str, headers):
    searchparam = {
        "datestring": date_str,
        "cdstring": "Y:" + str(court_id) + "," + start_hour_str + "-" + end_hour_str + ";",
        "paytype": "W"
    }
    
    data = {
        'searchparam': json.dumps(searchparam),
        'wxkey': config['wxkey'],
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

def send_confirm(order_id: str, money: str, headers, thread_id: int):
    data = {
        'wxkey': config['wxkey'],
        'attach': 'guestorder|001|33301',
        'out_trade_no': order_id,
        'payje': money,
        'goodsshuoming': '预订付费'
    }
    response = requests.post(
        url='http://33301.koksoft.com/GetWxPayParam.aspx', 
        headers=headers,
        data=data,
        verify=False
    )
    print("tid<", thread_id, ">: confirm request has been sent! ")
    return response

def delegate(user_agent: str, ip: str, thread_id: int):
    headers = generate_headers(user_agent)
    response_text = send_order(config['court_id'], config['target_date'], config['target_start_time'], config['target_end_time'], headers).text
    print("tid<{}>: response: ".format(thread_id), response_text)
    response_arr = response_text.split(",")
    
    if len(response_arr) < 3:
        print("tid<{}>: get unusual response!".format(thread_id))
        return
    
    order_id = response_arr[1].strip('\"')
    money = response_arr[2]
    print("tid<{}>: order_id: ".format(thread_id), order_id, "money: ", money)
    response_text = send_confirm(order_id, money, headers, thread_id).text
    print(response_text)

def thread_func(user_agent: str, ip: str, thread_id: int):
    delegate(user_agent, ip, thread_id)

current_date = datetime.now().date()
# target_time is the time to sent request
target_time = datetime.combine(current_date, datetime.strptime(config['begin_time'], "%Y-%m-%d-%H:%M:%S").time())
current_time = datetime.now()
time_difference = target_time - current_time
print("current time: ", current_time, "target time: ", target_time)

if int(time_difference.total_seconds()) > 60:
    with alive_bar(int(time_difference.total_seconds() - 60), title="Coundown to " + config['begin_time']) as bar:
        while datetime.now() < target_time - timedelta(30):
            time.sleep(1)
            bar()

user_agent_list = []
ip_list = []

print("Only 1 minutes left, begin to generate fake ip and user agent")
    
for i in range(config['num_threads']):
    ua_generator = UserAgent(browsers='chrome')
    user_agent = ua_generator.random
    print("generate user_agent: ", user_agent)
    user_agent_list.append(user_agent)
    
while datetime.now() < target_time - timedelta(seconds=15):        
    pass
print("Only 15 seconds left, ready to launch requests!!!!!!")        

while datetime.now() < target_time:
    pass

if config['multi_thread']:
    attempt_times = 0
    threads = []
    while attempt_times < config['num_attempts']:
        for i in range(config['num_threads']):
            user_agent = user_agent_list[i % len(user_agent_list)]
            ip = None # TODO: generate fake ip 
            thread = threading.Thread(target=thread_func, args=(user_agent, ip, i))
            thread.start()
            threads.append(thread)
        for thread in threads:
            thread.join()    
        time.sleep(config['attempt_interval'])
        attempt_times += 1

else:
    delegate(user_agent[0], None, 0)