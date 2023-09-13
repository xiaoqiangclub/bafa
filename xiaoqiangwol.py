# _*_ coding : UTF-8 _*_
# 开发人员： Xiaoqiang
# 微信公众号: xiaoqiangclub
# 开发时间： 2023/9/13 17:22
# 文件名称： bafa.py
# 项目描述： 通过巴法开放平台实现小爱语音控制电脑的开关机
# 开发工具： PyCharm
import os
import paho.mqtt.client as mqtt  # 参考文档：https://www.python100.com/html/Y85X610X1BYV.html
from wakeonlan import send_magic_packet
from config import Config


class BaFa:
    def __init__(self, client_id: str, topic: str, mac: str):
        """
        通过巴法开放平台实现小爱语音控制电脑的开关机
        :param client_id: 巴法开放平台的秘钥：https://cloud.bemfa.com/tcp/index.html
        :param topic: 巴法开放平台创建的主题：https://cloud.bemfa.com/docs/#/?id=_111-%e6%8e%a5%e5%85%a5%e4%bb%8b%e7%bb%8d
        :param mac: 要唤醒电脑的mac地址
        """
        self._HOST = "bemfa.com"
        self._PORT = 9501
        self.client_id = client_id
        self.topic = topic
        # 要唤醒电脑的mac地址
        self.mac = mac

    def on_connect(self, client, userdata, flags, rc):
        """
        定义回调函数
        """
        if rc == 0:
            print("恭喜您，您已成功连接到巴法平台!")
        else:
            print(f"链接失败，错误代码：{rc}")
        # 订阅主题，client.subscribe()可以订阅多个主题，只需要用英文逗号分隔即可
        client.subscribe(topic=self.topic)

    def wake_on_lan(self):
        """ 唤醒电脑"""
        print("唤醒电脑...")
        send_magic_packet(self.mac)  # 使用你的目标设备的MAC地址替换'mac-address'

    def on_message(self, client, userdata, msg):
        """消息接收，并处理收到的消息"""
        data = msg.payload.decode('utf-8')
        print("主题:" + msg.topic + " 消息:" + data)

        if "on" == data:
            print("打开电脑")
            self.wake_on_lan()
        elif "off" == data:
            print("关闭电脑")
            # 休眠
            # print(os.system('ssh -n Ethan@192.168.2.23 "shutdown -h" > /dev/null 2>&1 &'))
            # 关机
            os.system('ssh -n xiaoqiang@192.168.1.88 "shutdown -s -t 000" > /dev/null 2>&1 &')

    # 订阅成功
    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"订阅成功: qos = {granted_qos}")

    # 失去连接
    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            print(f"警告！已断开连接，错误代码：{rc}")

    def connect_mqtt(self):
        """实例化client类并连接MQTT服务器"""
        client = mqtt.Client(self.client_id)
        client.username_pw_set("userName", "passwd")
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_subscribe = self.on_subscribe
        client.on_disconnect = self.on_disconnect
        client.connect(self._HOST, self._PORT, 60)
        # 循环执行消息循环，保持MQTT连接
        client.loop_forever()


def run():
    BaFa(
        client_id=Config.CLIENT_ID,
        topic=Config.TOPIC,
        mac=Config.MAC
    ).connect_mqtt()


if __name__ == '__main__':
    run()
