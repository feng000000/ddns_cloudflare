# ddns_cloudflare

用于动态更新 cloudflare 上的 dns 解析记录到本地的 ipv6 地址

## Usage
1. 安装依赖
    ```bash
    # 下载 uv https://docs.astral.sh/uv/getting-started/installation/
    curl -LsSf https://astral.sh/uv/install.sh | sh

    uv sync
    ```
2. 填写 .env
    ```bash
    cp .env.example .env

    # vim .env
    ```
    - API_TOKEN: cloudflare 的账户令牌
    - DOMAIN_NAME: 要更新的域名
    - RECORD_NAME: 要更新的记录 (需要包含域名)
    - TEST_SERVER_PORT: 用于测试的web服务占用的端口
        - 启动后可通过 `http://{RECORD_NAME}:{TEST_SERVER_PORT}/ping` 来检验连通性
3. 运行 (建议在tmux 中运行)
    ```bash
    # 在项目文件夹下
    sudo ./.venv/bin/python main.py
    ```

4. 查看日志
    ```bash
    # 在项目文件夹下
    tail -f ./ddns_updater.log
    ```
