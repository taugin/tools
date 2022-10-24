import subprocess
import sys
import os
from time import sleep
import zipfile
#引入别的文件夹的模块
DIR = os.path.dirname(sys.argv[0])
COM_DIR = os.path.join(DIR, "..", "common")
COM_DIR = os.path.normpath(COM_DIR)
sys.path.append(COM_DIR)
import Common
import Log
import Utils

SIGNAPK_FILE = os.path.normpath(os.path.join(os.path.dirname(sys.argv[0]), '..', 'base', "signapk.py"))

def decode_apk_resource(apk_file, decode_apk_dir):
    Log.out("[Logging...] 反编文件名称 : %s" % apk_file)
    if os.path.exists(decode_apk_dir):
        Log.out("[Logging...] 反编文件成功\n")
        return True
    cmdlist = [Common.JAVA, '-jar', Common.APKTOOL_JAR, 'd', apk_file, '--no-src', '-f', '-o', decode_apk_dir]
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 反编文件失败")
        return False
    else:
        Log.out("[Logging...] 反编文件成功\n")
        return True

def compile_resource(decode_apk_dir, compiled_resource_file):
    Log.out("[Logging...] 开始编译资源 : %s" % compiled_resource_file)
    if os.path.exists(compiled_resource_file):
        Log.out("[Logging...] 编译资源成功\n")
        return True
    cmdlist = [Common.AAPT2_BIN, 'compile', '--dir', os.path.join(decode_apk_dir, 'res'), '-o', compiled_resource_file]
    process = subprocess.Popen(cmdlist)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 编译资源失败")
        return False
    else:
        Log.out("[Logging...] 编译资源成功\n")
        return True
    pass

def fetch_apk_arguement(apk_file):
    apk_arguement = {}
    try:
        cmdlist = [Common.AAPT2_BIN, 'd', 'badging', apk_file]
        process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
        alllines = process.stdout.readlines()
        for line in alllines:
            tmp = Utils.parseString(line)
            tmp = tmp.replace("\r", "")
            tmp = tmp.replace("\n", "")
            tmp = tmp.strip()
            if tmp.startswith('package: '):
                tmp = tmp[len("package: "):]
                tmp = tmp.replace("'", '')
                tmpsplit = tmp.split(" ")
                if tmpsplit != None and len(tmpsplit) >= 3:
                    apk_arguement["version_code"] = tmpsplit[1].split("=")[1]
                    apk_arguement["version_name"] = tmpsplit[2].split("=")[1]
            elif tmp.startswith('sdkVersion'):
                tmp = tmp.replace("'", '')
                apk_arguement['min_sdk_version'] = tmp.split(':')[1]
            elif tmp.startswith('targetSdkVersion'):
                tmp = tmp.replace("'", '')
                apk_arguement['target_sdk_version'] = tmp.split(':')[1]
                pass
    except Exception as e:
        Log.out("[Exception...] %s" % e)
    return apk_arguement     

def link_resource(base_apk, decode_apk_dir, compiled_resource_file, apk_arguement):
    Log.out("[Logging...] 开始生成主包 : %s" % base_apk)
    if os.path.exists(base_apk):
        Log.out("[Logging...] 生成主包成功\n")
        return True
    min_sdk_version = apk_arguement.get('min_sdk_version')
    target_sdk_version = apk_arguement.get('target_sdk_version')
    version_code = apk_arguement.get('version_code')
    version_name = apk_arguement.get('version_name')
    manifest_file = os.path.join(decode_apk_dir, 'AndroidManifest.xml')
    cmdlist = [Common.AAPT2_BIN, 'link', '--proto-format', '-o', base_apk,
         '-I', Common.ANDROID_JAR, '--min-sdk-version', min_sdk_version, '--target-sdk-version', target_sdk_version, 
         '--version-code', version_code, '--version-name', version_name, '--manifest', manifest_file,
         '-R', compiled_resource_file, '--auto-add-overlay']
    process = subprocess.Popen(cmdlist, stdout=subprocess.PIPE)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 链接资源失败")
        Utils.deleteFile(compiled_resource_file)
        return False
    else:
        Log.out("[Logging...] 链接资源成功\n")
        return True
    pass

def unzip_base_apk(base_apk, base_apk_dir):
    Log.out("[Logging...] 解压压缩文件 : %s" % base_apk)
    if os.path.exists(base_apk_dir):
        Log.out("[Logging...] 解压文件成功\n")
        return True
    r = zipfile.is_zipfile(base_apk)
    if r:
        fz = zipfile.ZipFile(base_apk, 'r')
        for file in fz.namelist():
            fz.extract(file, base_apk_dir)
        Log.out("[Logging...] 解压文件成功\n")
        return True
    else:
        Log.out("[Logging...] 文件格式错误")
        return False
    pass

def copy_resource(base_apk_dir, decode_apk_dir):
    Log.out("[Logging...] 复制压缩文件 : %s" % base_apk_dir)

    manifest_dir = os.path.join(base_apk_dir, 'manifest')
    if not os.path.exists(manifest_dir):
        os.mkdir(manifest_dir)
    Utils.movefile(os.path.join(base_apk_dir, 'AndroidManifest.xml'), os.path.join(manifest_dir, 'AndroidManifest.xml'))
    
    assets_dir = os.path.join(base_apk_dir, 'assets')
    if not os.path.exists(assets_dir):
        os.mkdir(assets_dir)
    Utils.copydir(os.path.join(decode_apk_dir, "assets"), assets_dir)

    lib_dir = os.path.join(base_apk_dir, 'lib')
    if not os.path.exists(lib_dir):
        os.mkdir(lib_dir)
    Utils.copydir(os.path.join(decode_apk_dir, 'lib'), lib_dir)

    root_dir = os.path.join(base_apk_dir, 'root')
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    Utils.copydir(os.path.join(decode_apk_dir, 'unknown'), root_dir)

    kotlin_dir = os.path.join(base_apk_dir, 'root', 'kotlin')
    if not os.path.exists(kotlin_dir):
        os.mkdir(kotlin_dir)
    Utils.copydir(os.path.join(decode_apk_dir, 'kotlin'), kotlin_dir)


    meta_data_dir = os.path.join(base_apk_dir, 'root', 'META-INF')
    if not os.path.exists(meta_data_dir):
        os.mkdir(meta_data_dir)
    Utils.copydir(os.path.join(decode_apk_dir, 'original', 'META-INF'), meta_data_dir)
    file_list = os.listdir(meta_data_dir)
    if file_list != None and len(meta_data_dir) > 0:
        for f in file_list:
            if f != None and (f.endswith(".SF") or f.endswith(".MF") or f.find(".RSA") > -1):
                Utils.deleteFile(os.path.join(meta_data_dir, f))

    dex_dir = os.path.join(base_apk_dir, 'dex')
    if not os.path.exists(dex_dir):
        os.mkdir(dex_dir)
    file_list = os.listdir(decode_apk_dir)
    if file_list != None and len(file_list) > 0:
        for f in file_list:
            if f.endswith('.dex'):
                Utils.copyfile(os.path.join(decode_apk_dir, f), dex_dir)
    Log.out("[Logging...] 复制文件成功\n")
    return True
    pass

def zip_base_dir(base_dir, base_zip):
    Log.out("[Logging...] 压缩所有文件 : %s" % base_zip)
    z = zipfile.ZipFile(base_zip,'w',zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(base_dir):
        fpath = dirpath.replace(base_dir,'')
        fpath = fpath and fpath + os.sep or ''
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
    z.close()
    Log.out("[Logging...] 压缩文件成功\n")
    return True
    pass

def bundle_aab(base_zip, base_aab):
    Log.out("[Logging...] 生成AAB文件")
    if os.path.exists(base_aab):
        os.remove(base_aab)
    cmdlist = [Common.JAVA, '-jar', Common.BUNDLE_TOOL, 'build-bundle', '--modules=%s' % base_zip, '--output=%s' % base_aab]
    process = subprocess.Popen(cmdlist)
    ret = process.wait()
    if (ret != 0):
        Log.out("[Logging...] 生成文件失败")
        return False
    else:
        Log.out("[Logging...] 生成文件成功\n")
        return True
    pass

def sign_aab_file(base_aab, final_aab_file):
    cmdlist = ["python", SIGNAPK_FILE, '-j', "-o", final_aab_file, base_aab]
    ret = subprocess.call(cmdlist)
    if (ret == 0):
        return True
    else:
        return False

def delete_temp_file(decode_apk_dir, base_apk_dir, base_apk, compiled_resource_file, base_zip, base_aab):
    Utils.deletedir(decode_apk_dir)
    Utils.deletedir(base_apk_dir)
    Utils.deleteFile(base_apk)
    Utils.deleteFile(compiled_resource_file)
    Utils.deleteFile(base_zip)
    Utils.deleteFile(base_aab)
    pass

def apk2aab(apk_file):
    apk_dir = os.path.dirname(apk_file)
    apk_name = os.path.basename(apk_file)
    apk_base_name,_ = os.path.splitext(apk_name)
    decode_apk_dir = os.path.join(apk_dir, 'decode_apk_dir')
    base_apk = os.path.join(apk_dir, "base.apk")
    base_apk_dir = os.path.join(apk_dir, "base")
    compiled_resource_file = os.path.join(apk_dir, 'compiled_resources.zip')
    base_zip = os.path.join(apk_dir, "base.zip")
    base_aab = os.path.join(apk_dir, "base.aab")
    final_aab_file = os.path.join(apk_dir, '%s-final.aab' % apk_base_name)
    result = decode_apk_resource(apk_file, decode_apk_dir)
    if not result:
        Common.pause()
        return
    result = compile_resource(decode_apk_dir, compiled_resource_file)
    if not result:
        Common.pause()
        return
    apk_arguement = fetch_apk_arguement(apk_file)
    result = link_resource(base_apk, decode_apk_dir, compiled_resource_file, apk_arguement)
    if not result:
        Common.pause()
        return
    result = unzip_base_apk(base_apk, base_apk_dir)
    if not result:
        Common.pause()
        return
    result = copy_resource(base_apk_dir, decode_apk_dir)
    if not result:
        Common.pause()
        return
    result = zip_base_dir(base_apk_dir, base_zip)
    if not result:
        Common.pause()
        return
    result = bundle_aab(base_zip, base_aab)
    if not result:
        Common.pause()
        return
    sign_aab_file(base_aab, final_aab_file)
    delete_temp_file(decode_apk_dir, base_apk_dir, base_apk, compiled_resource_file, base_zip, base_aab)
    Log.out("\n[Logging...] 生成AAB文件 : %s" % final_aab_file)
    sleep(2)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        Log.out("[Logging...] 缺少apk参数")
        exit(0)
    apk_file = os.path.join(os.getcwd(), sys.argv[1])
    if apk_file == None or not os.path.exists(apk_file):
        Log.out("[Logging...] apk文件不存在 : %s" % apk_file)
        exit(0)
    if not apk_file.endswith(".apk"):
        Log.out("[Logging...] 不是apk文件 : %s" % apk_file)
        exit(0)
    apk2aab(apk_file)