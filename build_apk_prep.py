import os, shutil

# Read and modify app.js for Cordova
with open('static/js/app.js','r',encoding='utf-8') as f:
    js = f.read()

api_line = "var API_BASE = 'http://192.168.11.138:5000';\n"
js = api_line + js
js = js.replace('resp=await fetch(path', 'resp=await fetch(API_BASE + path')

os.makedirs('android-app/www/js', exist_ok=True)
with open('android-app/www/js/app.js','w',encoding='utf-8') as f:
    f.write(js)
print('app.js adapted for Cordova')

# Copy CSS
os.makedirs('android-app/www/css', exist_ok=True)
shutil.copy2('static/css/style.css', 'android-app/www/css/style.css')
print('CSS copied')

# Copy manifest
shutil.copy2('static/manifest.json', 'android-app/www/manifest.json')
print('manifest copied')

# Create www/index.html from template
import subprocess
subprocess.run(['python', '-c', 'import shutil; shutil.copy2("templates/index.html", "android-app/www/index.html")'], check=True)
print('index.html copied')

# Update config.xml
config_path = 'android-app/config.xml'
with open(config_path,'r',encoding='utf-8') as f:
    config = f.read()

config = config.replace('''<?xml version='1.0' encoding='utf-8'?>
<widget id="com.example.hello" version="1.0.0" xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>HelloWorld</name>
    <description>Sample Apache Cordova App</description>
    <author email="dev@cordova.apache.org" href="https://cordova.apache.org">
        Apache Cordova Team
    </author>
    <content src="index.html" />
    <allow-navigation href="http://192.168.11.138:*" />
    <allow-navigation href="*" />''', '''<?xml version='1.0' encoding='utf-8'?>
<widget id="com.zhongyi.zhiban" version="1.0.0" xmlns="http://www.w3.org/ns/widgets" xmlns:cdv="http://cordova.apache.org/ns/1.0">
    <name>\u4e2d\u533b\u667a\u4f34</name>
    <description>\u4e2d\u533b\u6cbb\u7597\u65b9\u6848\u67e5\u8be2\u4e0e\u5206\u4eab\u5e73\u53f0</description>
    <author email="dev@zhongyi.app" href="https://zhongyi.app">
        \u4e2d\u533b\u667a\u4f34\u56e2\u961f
    </author>
    <content src="index.html" />
    <allow-navigation href="http://192.168.11.138:*" />
    <allow-navigation href="http://*" />
    <access origin="http://192.168.11.138:*" />''')

with open(config_path,'w',encoding='utf-8') as f:
    f.write(config)
print('config.xml updated')

# Copy icons to Cordova platforms/android
icon_dir = 'android-app/platforms/android/app/src/main/res'
if os.path.exists(icon_dir):
    for d in ['mipmap-mdpi', 'mipmap-hdpi', 'mipmap-xhdpi', 'mipmap-xxhdpi', 'mipmap-xxxhdpi']:
        os.makedirs(f'{icon_dir}/{d}', exist_ok=True)
    shutil.copy2('android-app/www/img/icon-192.png', f'{icon_dir}/mipmap-xhdpi/icon.png')
    shutil.copy2('android-app/www/img/icon-512.png', f'{icon_dir}/mipmap-xxxhdpi/icon.png')
    print('Android icons copied')

print()
print('=== Build preparation complete ===')
print('Run: cd android-app && cordova build android')
