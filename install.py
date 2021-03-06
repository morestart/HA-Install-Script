import getopt
import subprocess
import sys
import time
import os
from pathlib import Path
import getpass

username = getpass.getuser()


class Logger:
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[31m'
    END = '\033[0m'

    @staticmethod
    def info(info):
        try:
            print(Logger.OK + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font")

    @staticmethod
    def warn(info):
        try:
            print(Logger.WARNING + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not")

    @staticmethod
    def error(info):
        try:
            print(Logger.FAIL + info + Logger.END)
        except UnicodeEncodeError:
            Logger.warn("[ERROR] Not found chinese font, you must install chinese font, if not")


# 公共服务 各系统兼容的部分
class BaseService:
    def __init__(self):
        self.username = username
        self.haAutoStartPath = "/etc/systemd/system/home-assistant@{}.service".format(self.username)

    # 获取当前Python版本
    def get_python_version(self):
        try:
            Logger.info("[INFO] Python3 版本")
            subprocess.run("python3 -V", shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 未找到Python3")

        try:
            Logger.info("[INFO] Python2 版本")
            subprocess.run("python -V", shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 未找到Python2")

    # 更新Python3版本
    def upgrade_python3(self):
        return

    # 更新源与软件
    def prepare(self):
        try:
            Logger.info("[INFO] 准备更新软件包列表")

            subprocess.run("sudo apt-get update", shell=True, check=True)

            Logger.info("[INFO] 软件包列表更新完毕")
            Logger.info("\n")
            Logger.info("[INFO] 是否更新软件?(y or n) 默认为n")

            confirm = input("(不输入可直接回车使用默认值)>")
            if confirm == "y" or confirm == "Y":
                subprocess.run("sudo apt-get upgrade", shell=True, check=True)
                Logger.info("[INFO] 更新软件完毕")

        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 更新失败,请检查网络连接,两秒后准备重新更新")
            time.sleep(2)
            self.prepare()

    # 获取当前HA版本
    def get_ha_version(self):
        try:
            subprocess.run("hass --version", shell=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 未安装HomeAssistant")

    def install_ha(self):
        try:
            Logger.info("[INFO] 准备安装HomeAssistant")
            subprocess.run("sudo pip3 install homeassistant", shell=True, check=True)
            Logger.info("[INFO] HomeAssistant安装成功")
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装失败,2s后准备重试...")
            time.sleep(2)
            self.install_ha()

    # 更新HomeAssistant
    def upgrade_ha(self):
        try:
            Logger.info("[INFO] 准备更新HomeAssistant")

            subprocess.run("sudo pip3 install -U homeassistant", shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 更新HomeAssistant失败,请检查网络, 两秒后准备重新安装...")
            time.sleep(2)
            self.upgrade_ha()

    # 更新指定版本HA
    def upgrade_specific_ha(self):
        Logger.info("[INFO] 请输入HA版本号")

        ha_version = input(">")
        try:
            subprocess.run("sudo pip3 install -U homeassistant=={}".format(ha_version), shell=True, check=True)
            Logger.info("[INFO] 安装{}版本HomeAssistant成功".format(ha_version))
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装{}版本HomeAssistant失败,请检查版本号与网络连接,"
                         "两秒后准备重新安装...".format(ha_version))
            time.sleep(2)
            self.upgrade_specific_ha()

    def start_ha(self):
        try:
            subprocess.run("sudo systemctl start home-assistant@{}.service".format(username), shell=True, check=True)
            Logger.info("[INFO] HA启动成功")
        except subprocess.CalledProcessError:
            Logger.error("[INFO] HA启动失败")

    def restart_ha(self):
        try:
            subprocess.run("sudo systemctl restart home-assistant@{}.service".format(username), shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 重启失败")

    def stop_ha(self):
        try:
            subprocess.run("sudo systemctl stop home-assistant@{}.service".format(username), shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 终止HA失败")

    def print_ha_log(self):
        try:
            subprocess.run("sudo journalctl -f -u home-assistant@{}".format(username), shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 查询日志失败")

    def auto_start_ha(self):
        Logger.info("[INFO] 准备配置HomeAssistant自启动")

        try:
            with open(self.haAutoStartPath, "w+") as f:
                f.write("[Unit]\n"
                        "Description=Home Assistant\n"
                        "After=network.target\n\n"
                        "[Service]\n"
                        "Type=simple\n"
                        "User=%i\n"
                        "ExecStart=/usr/local/bin/hass\n\n"
                        "[Install]\n"
                        "WantedBy=multi-user.target\n")
            try:
                subprocess.run("sudo systemctl daemon-reload", shell=True, check=True)
                Logger.info("[INFO] HomeAssistant自启动建立成功")
                subprocess.run("sudo systemctl enable home-assistant@{}.service".format(username), shell=True)
            except subprocess.CalledProcessError:
                Logger.error("[ERROR] 自启动重载失败")
        except FileNotFoundError:
            Logger.error("[ERROR] 自启动建立失败,请检查自启动配置路径.")

    def install_mqtt_broker(self):
        return

    def set_wifi(self):
        return

    def change_pip_source(self):
        return

    def change_apt_source(self):
        return

    def install_samba(self):
        return

    def install_docker(self):
        return


class UbuntuService(BaseService):
    def __init__(self):
        super().__init__()

    def get_python_version(self):
        super().get_python_version()

    def prepare(self):
        super().prepare()
        try:
            subprocess.run("sudo apt install python3-pip", shell=True, check=True)
            Logger.info("[INFO] 安装pip3成功")
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装pip3失败，2s后准备重试...")
            time.sleep(2)
            self.prepare()

    def get_ha_version(self):
        super().get_ha_version()

    def install_ha(self):
        self.prepare()
        super().install_ha()

    def upgrade_ha(self):
        self.prepare()
        super().upgrade_ha()

    def upgrade_specific_ha(self):
        self.prepare()
        super().upgrade_specific_ha()

    def start_ha(self):
        super().start_ha()

    def restart_ha(self):
        super().restart_ha()

    def stop_ha(self):
        super().stop_ha()

    def print_ha_log(self):
        super().print_ha_log()

    def auto_start_ha(self):
        super().auto_start_ha()

    def install_mqtt_broker(self):
        Logger.info("[INFO] 准备安装Mosquitto Broker")
        try:
            subprocess.run("sudo apt install mosquitto mosquitto-clients", shell=True, check=True)
            mqtt_user_name = input("请输入MQTT用户名:")
            subprocess.run("sudo mosquitto_passwd -c /etc/mosquitto/passwd " + mqtt_user_name, shell=True, check=True)
            try:
                with open("/etc/mosquitto/conf.d/default.conf", "w+") as f:
                    f.write("allow_anonymous false\n"
                            "password_file /etc/mosquitto/pwfile\n"
                            "listener 1883\n")
                    Logger.info("[INFO] 写入MQTT配置成功!")
            except FileNotFoundError:
                Logger.error("[ERROR] 未发现mqtt配置文件,请重新安装...")
        except subprocess.CalledProcessError:
            Logger.error("安装失败,请重新安装")
        finally:
            subprocess.run("sudo systemctl restart mosquitto", shell=True, check=True)

    def change_pip_source(self):
        Logger.warn("[WARNING] 暂不支持Ubuntu")

    def change_apt_source(self):
        Logger.warn("[WARNING] 暂不支持Ubuntu")

    def upgrade_python3(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        Logger.info("[INFO] 准备更新Ubuntu Python3版本")
        self.prepare()
        Logger.info("[INFO] 准备安装依赖")
        try:
            subprocess.run(
                "sudo apt install wget && sudo apt install zlib* && sudo apt install libffi-dev "
                "&& sudo apt install openssl && sudo apt install libssl-dev && sudo apt install make",
                shell=True, check=True)
            Logger.info("[INFO] 安装依赖成功")
            Logger.info("[INFO] 准备下载Python3")
            try:
                subprocess.run("wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tgz", shell=True, check=True)
                Logger.info("[INFO] 下载Python3成功")
                Logger.info("[INFO] 准备安装GCC")
                try:
                    subprocess.run("sudo apt install gcc", shell=True, check=True)
                    Logger.info("[INFO] 安装gcc成功")
                    Logger.info("[INFO] 准备解压python")
                    subprocess.run("tar -xvzf Python-3.7.4.tgz", shell=True)
                    os.chdir("{}/Python-3.7.4".format(base_dir))
                    subprocess.run("./configure", shell=True)
                    subprocess.run("sudo make && sudo make install", shell=True)
                    Logger.info("[INFO] Python3升级完成")
                    subprocess.run("ln -s /usr/python3.7/bin/python3 /usr/bin/python3", shell=True)
                except subprocess.CalledProcessError:
                    Logger.error("[ERROR] 安装gcc失败,准备重新安装...")
                    self.upgrade_python3()
            except subprocess.CalledProcessError:
                Logger.error("[ERROR] 下载Python3失败,准备重新下载...")
                self.upgrade_python3()
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装依赖失败")
            self.upgrade_python3()

    def set_wifi(self):
        Logger.warn("[WARNING] 暂不支持Ubuntu")

    def install_samba(self):
        Logger.warn("[WARNING] 暂不支持Ubuntu")

    def install_docker(self):
        Logger.info("[INFO] 准备移除旧版本Docker")

        subprocess.run("sudo apt remove docker docker-engine docker.io", check=True, shell=True)

        Logger.info("[INFO] 准备安装docker依赖")
        try:
            subprocess.run("sudo apt install apt-transport-https ca-certificates curl software-properties-common",
                           shell=True, check=True)
            Logger.info("[INFO] 准备添加GPG密钥")
            subprocess.run("curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu/gpg | sudo apt-key add -",
                           shell=True, check=True)
            Logger.info("[INFO] 准备添加Docker软件源")
            subprocess.run(
                "sudo add-apt-repository \"deb [arch=amd64] https://mirrors.ustc.edu.cn/docker-ce/linux/ubuntu $(lsb_release -cs)  stable\"",
                shell=True, check=True)
            Logger.info("[INFO] 准备安装Docker CE")
            self.prepare()
            try:
                subprocess.run("sudo apt install docker-ce", shell=True, check=True)
                Logger.info("[INFO] 准备建立docker用户组")
                subprocess.run("sudo groupadd docker", shell=True)
                Logger.info("[INFO] 将当前用户加入docker组")
                subprocess.run("sudo usermod -aG docker $USER", shell=True)
                Logger.info("[INFO] 准备测试是否安装成功")
                subprocess.run("docker run hello-world", shell=True)
                Logger.info("[INFO] 准备启动docker ce")
                subprocess.run("sudo systemctl enable docker", shell=True)
                subprocess.run("sudo systemctl start docker", shell=True)

                Logger.info("[INFO] 准备安装Docker图形管理界面")
                try:
                    subprocess.run("sudo docker volume create portainer_data", shell=True, check=True)
                    subprocess.run("sudo docker run -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer", shell=True, check=True)
                except subprocess.CalledProcessError:
                    Logger.error("[ERROR] 安装Docker图形管理界面失败,准备重新安装")
                    time.sleep(2)
                    self.install_docker()
            except subprocess.CalledProcessError:
                Logger.error("[ERROR] Docker CE安装失败，准备重新安装")
                time.sleep(2)
                self.install_docker()

        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 依赖安装失败，准备重新安装")
            time.sleep(2)
            self.install_docker()


# 树莓派
class DebianService(BaseService):
    def __init__(self):
        super().__init__()
        self.pip_source_path = "/etc/pip.conf"
        self.apt_source_path = "/etc/apt/sources.list"
        self.smb_conf_path = "/etc/samba/smb.conf"
        self.wifi_conf_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
        self.mosquitto_config_path = "/etc/mosquitto/mosquitto.conf"
        self.docker_mirror_path = "/etc/docker/daemon.json"
        self.flag = 0

    # 配置wifi
    def set_wifi(self):
        Logger.info("[INFO] 增加wifi配置,请输入你的用户名和密码...")
        SSID = input("SSID>")
        PASSWORD = input("PASSWORD>")

        if SSID != "":
            Logger.info("[INFO] 确认你的wifi配置.(y or n)")
            confirm = input(">")
            if confirm == "y" or confirm == "Y":
                with open(self.wifi_conf_path, "w+") as f:
                    f.write("country=CN\n"
                            "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n"
                            "update_config=1\n"
                            "network={\n"
                            "\tssid=\"" + SSID + "\"\n" +
                            "\tpsk=\"" + PASSWORD + "\"\n" +
                            "\tkey_mgmt=WPA-PSK\n"
                            "\tpriority=1}")
                    Logger.info("[INFO] 配置成功!")
            elif confirm == "n" or confirm == "N":
                self.set_wifi()
        else:
            Logger.warn("[WARNING] SSID不能为空")
            self.set_wifi()

    def get_python_version(self):
        super().get_python_version()

    def get_ha_version(self):
        super().get_ha_version()

    # 换源 更换清华源 pip同步时间 5min
    def change_pip_source(self):
        try:
            subprocess.run("sudo mv /etc/pip.conf /etc/pip.conf.bak", shell=True, check=True)
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                Logger.info("[INFO] 写入pip文件成功")
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 没有找到pip文件,准备建立pip文件")
            with open(self.pip_source_path, 'w+') as f:
                f.write("[global]\n"
                        "index-url = https://pypi.tuna.tsinghua.edu.cn/simple")
                Logger.info("[INFO] 写入pip文件成功")

    def change_apt_source(self):
        try:
            subprocess.run("sudo mv /etc/apt/sources.list /etc/apt/sources.list.bak", shell=True, check=True)
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ buster main non-free contrib")
                Logger.info("[INFO] 写入apt文件成功")
            subprocess.run("sudo rm -rf /etc/apt/sources.list.d/raspi.list", shell=True)
            with open('/etc/apt/sources.list.d/raspi.list', 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspberrypi/ buster main ui")
        except subprocess.CalledProcessError:
            Logger.error("[INFO] 找不到apt文件,准备建立apt文件")
            time.sleep(2)
            with open(self.apt_source_path, 'w+') as f:
                f.write("deb http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib\n"
                        "deb-src http://mirrors.tuna.tsinghua.edu.cn/raspbian/raspbian/ stretch main non-free contrib")
                Logger.info("[INFO] 写入apt文件成功")
        self.prepare()

    def prepare(self):
        super().prepare()

    def upgrade_ha(self):
        super().upgrade_ha()

    def upgrade_specific_ha(self):
        super().upgrade_specific_ha()

    def install_ha(self):
        super().install_ha()

    def auto_start_ha(self):
        super().auto_start_ha()

    # samba安装 TODO
    def install_samba(self):
        Logger.info("[INFO] 准备安装Samba")

        try:
            subprocess.run("sudo apt-get install samba samba-common", shell=True, check=True)
        except subprocess.CalledProcessError:
            Logger.error("ERROR] samba安装失败...准备重新安装")
            self.install_samba()
        subprocess.run("sudo smbpasswd -a {}".format(username), shell=True)
        subprocess.run("sudo rm " + self.smb_conf_path, shell=True)
        with open(self.smb_conf_path, "w") as f:
            f.write("[global]\n"
                    "netbios name = raspberrypi\n"
                    "server string = The Pi File Center\n"
                    "workgroup = WORKGROUP\n"
                    "hosts allow =\n"
                    "remote announce =\n"
                    "remote browse sync =\n"
                    "[HOME ASSISTANT]\n"
                    "path = /home/pi\n"
                    "comment = No comment\n"
                    "browsable = yes\n"
                    "read only = no\n"
                    "valid users =\n"
                    "writable = yes\n"
                    "guest ok = yes\n"
                    "public = yes\n"
                    "create mask = 0777\n"
                    "directory mask = 0777\n"
                    "force user = root\n"
                    "force create mode = 0777\n"
                    "force directory mode = 0777\n"
                    "hosts allow =\n")
        subprocess.run("sudo systemctl restart smbd", shell=True)
        Logger.info("[INFO] 安装Samba成功")

    # 安装 mosquitto
    def install_mqtt_broker(self):
        Logger.info("[INFO] 准备安装Mosquitto")

        self.prepare()
        try:
            subprocess.run("sudo apt-get install mosquitto", shell=True, check=True)
            try:
                with open(self.mosquitto_config_path, "w+") as f:
                    f.write("allow_anonymous false\n"
                            "password_file /etc/mosquitto/pwfile\n"
                            "listener 1883\n")
                    Logger.info("[INFO] 写入MQTT配置成功!")

            except FileNotFoundError:
                Logger.error("[ERROR] 未发现mqtt配置文件,请重新安装...")
            mqtt_user_name = input("请输入MQTT用户名:")
            subprocess.run("sudo mosquitto_passwd -c /etc/mosquitto/pwfile {}".format(mqtt_user_name), shell=True)
            subprocess.run("sudo systemctl start mosquitto.service", shell=True)
            Logger.info("[INFO] MQTT安装配置成功")
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装mosquitto失败,请检查网络连接,两秒后准备重新安装")
            time.sleep(2)
            self.install_mqtt_broker()

    def restart_ha(self):
        super().restart_ha()

    def start_ha(self):
        super().start_ha()

    def stop_ha(self):
        super().stop_ha()

    def print_ha_log(self):
        super().print_ha_log()

    # 更新Python3版本
    def upgrade_python3(self):
        base_dir = os.path.abspath(os.path.dirname(__file__))
        pv = 'Python-3.7.2'
        Logger.info("[INFO] 准备安装{}".format(pv))

        Logger.info("[INFO] 准备卸载冲突, 如果有请选择y")
        subprocess.run("sudo pip3 uninstall homeassistant", shell=True)
        Logger.info("[INFO] 开始安装依赖")
        try:
            subprocess.run("sudo apt-get install build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev",
                           shell=True, check=True)
            try:
                subprocess.run("sudo apt-get install wget", shell=True, check=True)
                file_dir = base_dir + '/'.format(pv) + '.tgz'
                file = Path(file_dir)
                if file.is_file():
                    Logger.info("[INFO] 开始解压安装包")
                    time.sleep(2)
                    subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                    os.chdir("{}/{}".format(base_dir, pv))
                    Logger.info("[INFO] 开始编译{}".format(pv))
                    time.sleep(2)
                    subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                    Logger.info("[INFO] 已完成{}安装".format(pv))
                else:
                    Logger.info("[INFO] 下载Python安装包")
                    time.sleep(2)
                    try:
                        subprocess.run("sudo wget https://www.python.org/ftp/python/3.7.2/{}.tgz".format(pv),
                                       shell=True, check=True)
                        Logger.info("[INFO] 开始解压安装包")
                        time.sleep(2)
                        subprocess.run("sudo tar -zvxf {}.tgz".format(pv), shell=True)
                        os.chdir("{}/{}".format(base_dir, pv))
                        Logger.info("[INFO] 开始编译{}".format(pv))
                        time.sleep(2)
                        subprocess.run("sudo ./configure && sudo make && sudo make install", shell=True)
                        Logger.info("[INFO] 已完成{}安装".format(pv))
                    except subprocess.CalledProcessError:
                        Logger.error("[ERROR] 下载Python失败,请检查网络连接,两秒后准备重新安装")
                        time.sleep(2)
                        self.upgrade_python3()
            except subprocess.CalledProcessError:
                Logger.error("[ERROR] 下载wget失败,请检查网络连接,两秒后准备重新安装")
                time.sleep(2)
                self.prepare()
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装依赖失败,请检查网络连接,两秒后准备重新安装")
            time.sleep(2)
            self.upgrade_python3()
        self.get_python_version()

    #  安装docker ce
    def install_docker(self):

        Logger.info("[INFO] 准备安装docker CE")
        if self.flag == 0:
            self.prepare()
            self.flag = 1
        Logger.info("[INFO] 准备安装docker CE依赖")
        try:
            subprocess.run(
                "sudo apt-get install apt-transport-https ca-certificates gnupg2 lsb-release software-properties-common",
                shell=True, check=True)

            Logger.info("[INFO] 准备添加GPG秘钥")
            try:
                subprocess.run("curl -fsSL https://mirrors.ustc.edu.cn/docker-ce/linux/raspbian/gpg | sudo apt-key "
                               "add -", shell=True, check=True)
                Logger.info("[INFO] 准备添加国内镜像源")
                with open(self.apt_source_path, 'a') as f:
                    f.write("deb https://download.docker.com/linux/raspbian stretch stable")
                self.prepare()
                try:
                    subprocess.run("sudo apt-get install docker-ce", shell=True, check=True)
                    Logger.info("[INFO] 准备建立用户组")
                    # 建立docker 用户组
                    subprocess.run("sudo groupadd docker", shell=True)
                    # 当前用户加入用户组
                    subprocess.run("sudo usermod -aG docker $USER", shell=True)
                    # 测试docker是否安装成功
                    Logger.info("[INFO] 验证docker是否安装成功")
                    subprocess.run("docker run arm32v7/hello-world", shell=True)
                    Logger.info("[INFO] 准备启动docker CE")
                    subprocess.run("sudo systemctl enable docker", shell=True)
                    subprocess.run("sudo systemctl start docker", shell=True)
                except subprocess.CalledProcessError:
                    Logger.error("[ERROR] docker CE安装失败,准备重新安装...")
                    self.install_docker()
            except subprocess.CalledProcessError:
                Logger.error("[ERROR] 添加秘钥失败,2s后准备重新添加")
                time.sleep(2)
                self.install_docker()
        except subprocess.CalledProcessError:
            Logger.error("[ERROR] 安装依赖失败,2s后准备重新安装...")
            time.sleep(2)
            self.install_docker()


class Install:
    def __init__(self, os_name):
        self.os_name = os_name
        self.service = None

    @staticmethod
    def help_info():
        Logger.info("-h 显示帮助")
        Logger.info("-w 添加wifi配置")
        Logger.info("-p 更新软件包列表与软件")
        Logger.info("-s 安装samba服务")
        Logger.info("--im 安装MQTT Broker")
        Logger.info("-" * 30)
        Logger.info("--cps 更换pip源")
        Logger.info("--cas 更换apt源")
        Logger.info("-" * 30)
        Logger.info("--ih 安装HomeAssistant")
        Logger.info("--uh 更新HomeAssistant")
        Logger.info("--has 配置HomeAssistant自启动")
        Logger.info("--sh 运行HomeAssistant实例")
        Logger.info("--sth 停止HomeAssistant实例")
        Logger.info("--rh 重启HomeAssistant")
        Logger.info("--phl 查看HomeAssistant日志")
        Logger.info("--hv 查看HomeAssistant版本")
        Logger.info("-" * 30)
        Logger.info("--pv 查看Python版本")
        Logger.info("--up 更新Python3版本")
        Logger.info("-" * 30)
        Logger.info("--id 安装docker CE")

    def install(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "-w-p-s-h", ["pv", "hv", "cas", "cps",
                                                                  "uh", "usp", "ih", "has", "im",
                                                                  "rh", "phl", "up", "ush", "sh", "sth", "id"])

            if self.os_name == "Windows":
                raise Exception("[ERROR] 不支持Windows操作系统")
            elif self.os_name == "Linux":
                out = subprocess.check_output("cat /etc/os-release", shell=True)
                out = out.decode("utf-8")
                if "Ubuntu" in out:
                    Logger.info("[INFO] 检测到Ubuntu系统")
                    # TODO: 这里要做一点系统判断 -h没必要执行更新代码
                    self.service = UbuntuService()
                    # self.service.prepare()
                elif "Debian" or "debian" in out:
                    Logger.info("[INFO] 检测到Debian操作系统")
                    self.service = DebianService()
                    # self.service.prepare()
                else:
                    Logger.warn("[WARNING] 没有检测到操作系统版本")

            for opt, value in opts:
                if opt == "-h" or opt == "--help":
                    self.help_info()
                elif opt == "-w":
                    self.service.set_wifi()
                elif opt == "-p":
                    self.service.prepare()
                elif opt == "-s":
                    self.service.install_samba()
                elif opt == "--pv":
                    self.service.get_python_version()
                elif opt == "--hv":
                    self.service.get_ha_version()
                elif opt == "--cps":
                    self.service.change_pip_source()
                elif opt == "--cas":
                    self.service.change_apt_source()
                elif opt == "--uh":
                    self.service.upgrade_ha()
                elif opt == "--usp":
                    self.service.upgrade_specific_ha()
                elif opt == "--ih":
                    self.service.install_ha()
                elif opt == "--has":
                    self.service.auto_start_ha()
                elif opt == "--im":
                    self.service.install_mqtt_broker()
                elif opt == "--rh":
                    self.service.restart_ha()
                elif opt == "--phl":
                    self.service.print_ha_log()
                elif opt == "--up":
                    self.service.upgrade_python3()
                elif opt == "--sh":
                    self.service.start_ha()
                elif opt == "--sth":
                    self.service.stop_ha()
                elif opt == "--id":
                    self.service.install_docker()

        except getopt.GetoptError:
            self.help_info()
            raise Exception("[ERROR] 没有这个选项, 请查看可用选项")


if __name__ == '__main__':
    try:
        import platform

        system = platform.system()
        Install(system).install()
    except PermissionError:
        Logger.error("[ERROR] 权限不足,请使用sudo权限运行此程序")
