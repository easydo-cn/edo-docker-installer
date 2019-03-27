# -*- coding:utf-8 -*-
import subprocess,os

def os_kind():
    if os.path.isfile('/etc/redhat-release'):
        distribution = subprocess.check_output('cat /etc/redhat-release', shell=True).split(' ')[0]
    else:
        distribution = subprocess.check_output('cat /etc/issue',shell=True).split(' ')[0]
    return distribution

def env_check():
    compose_dir = '/var/docker_data/compose'
    kernel_version = subprocess.check_output('uname -a',shell=True).split(' ')[2]
    if not kernel_version.startswith('4'):
        print('警告:内核版本为3.X,请确保docker-compose.yml配置文件中没有使用资源限制')
    if os.path.isfile(os.path.join(compose_dir,'.env')):
        print('警告:%s目录下存在.env配置文件' %(compose_dir))
    docker = subprocess.check_output('which docker||true', shell=True)
    if docker:
        get_drive = 'docker info|grep "Storage Driver"'
        drive = subprocess.check_output(get_drive,shell=True).split(':')[1].strip()
        if not drive.startswith('aufs') and not drive.startswith('overlay'):
            print('警告:docker存储驱动没有使用推荐配置overlay或aufs')

def uninstall_docker():
    distribution = os_kind()
    if distribution == 'CentOS':
        remove = 'yum remove docker docker-common docker-selinux docker-engine -y'
    else:
        remove = 'apt-get remove docker docker-engine docker.io -y'
    subprocess.check_output(remove, shell=True)

def uninstall_v6():
    # 先检查是否存在v6版本服务
    try:
        subprocess.check_output('systemctl list-unit-files|grep viewer_worker.service', shell=True)
    except Exception:
        print('未检测到安装v6服务')
        exit(-1)
    print('开始删除服务请稍候...')
    v6_svc=['assistent','etcd','mysql-discovery','upload-discovery','console','nginx-discovery','redis',
            'viewer_web-discovery','message-discovery','nginx','viewer_web','edo_backup','message','oc-discovery',
            'registry','viewer_worker-discovery','oc','sitebot-discovery','viewer_worker','edo_service','sitebot',
            'wo-discovery','wo','mqtt-discovery','es-discovery','mqtt','queue-discovery','es','queue','mount-backup-drive',
            'mount-data-drive','mount-files-drive']
    for svc in v6_svc:
        remove_cmd ='systemctl stop %(svc)s.service && systemctl disable %(svc)s.service && rm -f /etc/systemd/system/%(svc)s.service' %{'svc':svc}
        subprocess.check_output(remove_cmd,shell=True)

    reload_cmd = 'systemctl daemon-reload && systemctl reset-failed'
    subprocess.check_output(reload_cmd,shell=True)

if __name__ == '__main__':
    print( """
    1、卸载V6版本系统服务
    2、卸载旧版本docker
    3、系统环境检查""")
    do = raw_input('输入序号执行相应操作:')
    if do == '1':
        uninstall_v6()
    elif do == '2':
        uninstall_docker()
    elif do == '3':
        env_check()
    else:
        print('输入错误')