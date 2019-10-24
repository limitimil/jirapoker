# FakeBackEndServer

## Deploy on IIS
### Enable wfastcgi
1. To enable fastcgi: See https://pypi.org/project/wfastcgi/
2. After the above step succeed, you will receive a message like: 
```text
C:\Python34\Scripts> wfastcgi-enable
Applied configuration changes to section "system.webServer/fastCgi" for "MACHINE/WEBROOT/APPHOST" at configuration commit path "MACHINE/WEBROOT/APPHOST"
"C:\Python34\python.exe|C:\Python34\lib\site-packages\wfastcgi.py" can now be used as a FastCGI script processor
```
Copy your (this is just an example)
```
"C:\Python34\python.exe|C:\Python34\lib\site-packages\wfastcgi.py"
```
and replace
**"xxxxxxxxxxxxx" of scriptProcessor="xxxxxxxxxxxxx"** in the **web.config**

### Install IIS
Reference to Deployment section of https://cybersoft4u.atlassian.net/wiki/spaces/TEIS/pages/530318494/Testing+-+Mock+MiniTIS
to see how to install IIS and related tools

### Setup IIS website
1. Open IIS manager
2. Right click **sites** --> **Add Website...** --> Type **Site name** --> Choose **Physical Path** to your app folder --> Select the **port** you want to expose --> Click **OK**
3. Finish FakeBackEndServer setup