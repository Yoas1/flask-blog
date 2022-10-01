![](https://visitor-badge.glitch.me/badge?page_id=Yoas1.flask-blog)</br>
[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/Yoas1/flask-blog)</br>

# flask-blog

Blog build with flask.<br>

you can run on docker container with commands:<br>

**1** - For get telegram-bot messages:
        **docker run -it -e ID=</USER_OR_GROUP-ID/> -e TOKEN=</BOT-TOKEN/> -p 5000:5000 yoas1/flask-blog:1.0**
        OR
        **docker run -it -e ID=</USER_OR_GROUP-ID/> -e TOKEN=</BOT-TOKEN/> -p 5000:5000 ghcr.io/yoas1/flask-blog:1.0**
**2** - Without telegram-bot messages:
        **docker run -it -e ID=none -e TOKEN=none -p 5000:5000 yoas1/flask-blog:1.0**
        OR
        **docker run -it -e ID=none -e TOKEN=none -p 5000:5000 ghcr.io/yoas1/flask-blog:1.0**
<br><br>

You can show my blog --> [Dev-Docs-Ops](https://yoas1.pythonanywhere.com)
