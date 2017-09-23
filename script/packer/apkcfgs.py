APKCFG_TEMPLATE = '''\
<?xml version="1.0" encoding="UTF-8"?>
<config>
    <!--配置全局插件-->
    <global-plugins>
        <plugin name="pushsdk" desc="推送插件"/>
    </global-plugins>

    <!--源APK文件路径-->
    <srcapk>srcapks/AbchDemo.apk</srcapk>

    <!--生成的APK文件路径-->
    <finalname>AbchDemo</finalname>

    <!--渠道配置列表-->
    <channels>
        <channel>
            <!--基本参数-->
            <param name="suffix" value=""/> <!--包名后缀-->
            <param name="splash" value="0"/> <!--是否闪屏 1：闪屏，0：无闪屏-->
            <param name="unity_splash" value="0"/> <!--unity闪屏-->
            <param name="corner" value="rb"/> <!--角标-->
            <!--渠道SDK参数-->
            <sdk>
                <param name="id" value="10"/> <!--渠道ID-->
                <param name="name" value="ad"/> <!--渠道名字-->
                <param name="sdk" value="adsdk"/> <!--渠道路径-->
            </sdk>
            <!-- sdk-params 参数是写入到developer_config.properties中 -->
            <properties>
                <param name="countdown" value="5" desc="倒计时秒"/>
                <param name="splashimg" value="splash_img.png" desc="广告图片"/>
            </properties>
            <!--manifest参数会被写入到application下面的meta-data节点-->
            <manifest>
            </manifest>
            <!-- 渠道插件 -->
            <plugins>
            </plugins>
            <!--需要渠道单独处理的参数-->
            <spec-params>
            </spec-params>
            <!--中间件版本参数-->
            <sdk-version>
                <versionCode>1</versionCode>
                <versionName>1.0.0</versionName>
            </sdk-version>
        </channel>
    </channels>
</config>\
'''
print("打包配置模板 : ")
print(APKCFG_TEMPLATE)