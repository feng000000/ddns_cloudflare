import subprocess
import platform
import logging


logger = logging.getLogger("UTILS")


def disable_ipv6_temp_addresses():
    system = platform.system()

    try:
        if system == "Linux":
            logger.info("disable temp ipv6 address on Linux...")
            # 临时禁用
            subprocess.run(["sysctl", "-w", "net.ipv6.conf.all.use_tempaddr=0"], check=True)
            subprocess.run(["sysctl", "-w", "net.ipv6.conf.default.use_tempaddr=0"], check=True)

        elif system == "Darwin":  # macOS
            logger.info("disable temp ipv6 address on macOS...")
            # 写入 sysctl.conf
            command = 'echo "net.inet6.ip6.use_tempaddr=0" | sudo tee -a /etc/sysctl.conf'
            subprocess.run(command, shell=True, check=True)

            subprocess.run(["networksetup", "-setv6off", "Ethernet"], check=True)
            subprocess.run(["networksetup", "-setv6automatic", "Ethernet"], check=True)
        else:
            print(f"不支持的系统类型: {system}")

    except subprocess.CalledProcessError as e:
        print(f"执行失败，请确保具有 sudo 权限: {e}")
