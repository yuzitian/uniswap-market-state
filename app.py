import os
from flask import Flask, render_template

app = Flask(__name__)  # 创建1个Flask实例

@app.route('/')  # 路由系统生成 视图对应url,1. decorator=app.route() 2. decorator(first_flask)
def first_flask():  # 视图函数
    #os.system("python uniswap_sta.py")
    os.system("python /root/yq/pythonProject001/uniswap_sta.py")
    return render_template('uniswap.html')  # response

if __name__ == '__main__':
    app.run(host='0.0.0.0')  # 启动socket