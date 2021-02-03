import requests

import urllib.parse as urlparse

user = ""
password = ""
sc_key = ""
flag = "0"  # 上班卡0，下班卡1


def get_url_query(url, query):
    """
    获取URL里面的参数值
    """
    queries = urlparse.parse_qs(url.split("?")[1])
    if not queries.get(query):
        return None
    return "".join(queries.get(query))


class JiFen:
    def __init__(self, user, password, sc_key=""):
        self.user = str(user)
        self.password = str(password)
        self.sc_key = sc_key
        self.message = ""
        self.user_info = {}
        self.unread_ann = []

        self.get_user_info()

    def get_user_info(self):
        url = "https://auth.jifenzhi.info/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/3.14.0",
            "Authorization": "Basic bXBtMjRfYW5kcm9pZDpHOEo5NXQ1aWtMaXdEZnU5UWdQT0k5d3RsNVFvNTJ2cA==",
        }
        data = f"username=local%3A{self.user}&password={self.password}&grant_type=password"
        response = requests.post(url, data=data, headers=headers)
        if response.status_code != 200:
            raise Exception("账号/密码错误！")
        else:
            self.user_info = response.json()

    def punch(self, flag):
        url = "https://api.jifenzhi.com/attendance/api/workScheduleConfig/base/card?onOffFlag=" + flag
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36mpm24_android",
            "authorization": "Bearer " + self.user_info["access_token"],
            "comomorgid": "15859861422091740001",
        }
        response = requests.get(url, headers=headers).text
        self.message += f"\n{response}"
        print(response)

    def read_announcement(self):  # 标记已读
        self._get_unread_announcement()
        if not self.unread_ann:
            msg = "没有未读公告。"
            self.message += f"\n{msg}"
            print(msg)
            return
        for unread in self.unread_ann:
            message_id = "".join(i for i in unread.keys())
            click_url = unread[message_id]
            url = "https://pushcenter.jifenzhi.com/pushServer/siteUpdateStatus"
            headers = {
                "Authorization": "Bearer " + self.user_info["access_token"],
                "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36mpm24_android",
            }
            data = f'{{"messageId":"{message_id}","msgType":2,"orgId":"15859861422091740001","memberId":"15859861448881740002","fromClientId":"mpm3.0,workflowx,odms,meritpoint,mpm-crm,taskClock,notice3,tasklist,ACTaskBusiness","userId":"{self.user_info["user_id"]}"}}'
            response = requests.post(url, data=data, headers=headers).json()
            if response.get("code") == "200":
                msg = f"公告已阅读, id:{message_id}"
                self.message += f"\n{msg}"
                print(msg)
                self._get_points(message_id, click_url)

    def _get_unread_announcement(self):
        """
        获取未读公告
        :return: [{id: click2url},...]
        """
        url = "https://pushcenter.jifenzhi.com/pushServer/pushResult"
        params = {
            "channel": "site",
            "msgType": "2",
            "pageSize": "5",
            "pageNum": "1",
            "fromClientId": "mpm3.0,workflowx,odms,meritpoint,mpm-crm,taskClock,notice3,tasklist,ACTaskBusiness",
            "userId": self.user_info["user_id"],
        }
        response = requests.get(url, params=params).json()
        if response.get("code") == "200":
            for l in response["resultData"]["list"]:
                if l["readStatus"] == 0:
                    self.unread_ann.append({l["id"]: l["click2url"]})  #
        return self.unread_ann

    def _get_points(self, message_id, click_url):  # 获取阅读分
        url = "https://api.jifenzhi.info/notice3/api/information/award?memberId=15859861448881740002&orgId=15859861422091740001&informationId=" + message_id
        headers = {
            "Authorization": "Bearer " + self.user_info["access_token"],
            "User-Agent": "Mozilla/5.0 (Linux; Android 5.1.1; MI 9 Build/NMF26X; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36mpm24_android",
            "Content-Type": "application/json;charset=UTF-8",
            "Referer": click_url,
        }
        data = f'{{"memberId":"15859861448881740002","orgId":"15859861422091740001","informationId":"{message_id}"}}'
        response = requests.post(url, data=data, headers=headers)
        msg = f"获取公告阅读分, id:{message_id}, {response.text}"
        self.message += f"\n{msg}"
        print(msg)

    def push_wx(self):
        if not self.sc_key:
            print("没有提供secret key.")
            return
        server_url = f"https://sc.ftqq.com/{sc_key}.send"
        params = {
            "text": f'打卡成功',
            "desp": self.message
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
    flag = input()
    sc_key = input()
    jf = JiFen(user, password, sc_key)
    jf.punch(flag)
    jf.read_announcement()
    jf.push_wx()
