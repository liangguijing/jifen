import requests

user = ""
password = ""
sc_key = ""


def punch():
    token = get_token()
    if not token:
        print("登录失败!")
        return "登录失败!"
    url = "https://api.jifenzhi.com/attendance/api/workScheduleConfig/base/card?onOffFlag=0"
    headers = {
        "Host": "api.jifenzhi.com",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "comomorgid": "15859861422091740001",
        "Origin": "https://kq.jifenzhi.info",
        "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36mpm24_android",
        "authorization": "Bearer " + token,
        "content-type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "Referer": "https://kq.jifenzhi.info/webFrontend/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "X-Requested-With": "com.jifenzhi.android"
    }
    response = requests.get(url, params=None, headers=headers).text
    print(response)
    if sc_key:
        push_wx(sc_key, response)


def get_token():
    url = "https://auth.jifenzhi.info/oauth/token"
    headers = {
        "Connection": "keep - alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "okhttp/3.14.0",
        "Authorization": "Basic bXBtMjRfYW5kcm9pZDpHOEo5NXQ1aWtMaXdEZnU5UWdQT0k5d3RsNVFvNTJ2cA=="
    }
    data = f"username=local%3A{user}&password={password}&grant_type=password"
    response = requests.post(url, data=data, headers=headers).json()

    if response.get("access_token"):
        token = response.get("access_token")
        print("Got Token successfully:" + token)
        return token


def push_wx(sc_key, desp=""):
    server_url = f"https://sc.ftqq.com/{sc_key}.send"
    params = {
        "text": f'打卡成功',
        "desp": desp
    }
    response = requests.get(server_url, params=params)
    json_data = response.json()
    if json_data['errno'] == 0:
        print(f"推送成功。")
    else:
        print(f"推送失败：{json_data['errno']}({json_data['errmsg']})")


if __name__ == '__main__':
    user = input()
    password = input()
    sc_key = input()
    punch()
