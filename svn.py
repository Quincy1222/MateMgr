# coding: utf-8

# svn.py

import subprocess
from urlparse import urljoin


class svn:
    def __init__(self, repo_root, username, password):
        self.username = username
        self.password = password

        self.repo_root = repo_root
        if repo_root[-1] != '/':
            self.repo_root += '/'

    def fetch_revision(self, path): #Relative URL
        revision = -1
        if path[0] == '/':
            path = path[1:]

        url = urljoin(self.repo_root, path)
        arg = ['svn', 'info', url.encode('gbk'), 
               '--non-interactive', '--trust-server-cert', 
               '--username', self.username, 
               '--password', self.password]
        try:
            result = subprocess.check_output(arg, 
                stderr=subprocess.STDOUT, universal_newlines=True)
            
            # print result
            for line in result.split('\n'):
                i = line.find('Revision')
                if i > -1:
                    revision = int(line[9:])
                    break
        except subprocess.CalledProcessError as e:
            #print e
            pass

        return revision

    def export_file(self, path, out=None):
        retval = ''
        if path[0] == '/':
            path = path[1:]

        url = urljoin(self.repo_root, path)
        arg = ['svn', 'export', url.encode('gbk')]

        if out: arg += [out, ]
        
        arg += ['--non-interactive', '--trust-server-cert', '--force', 
                '--username', self.username, 
                '--password', self.password]
        try:
            result = subprocess.check_output(arg, 
                stderr=subprocess.STDOUT, universal_newlines=True)
            
            for line in result.split('\n'):
                if line[0] == 'A':
                    retval = line[1:].strip()
                    break
        except subprocess.CalledProcessError as e:
            print e

        return retval

if __name__ == '__main__':
    repo_root = u'http://svn.ygct.com:82/svn/YGCT'
    path = u'/Temporary/机电产品线/知识库/物料汇总表.xls'
    username='wangquanyuan'
    password='wang@\x31\x31\x34\x34'

    svn = svn(repo_root, username, password)

    print svn.fetch_revision(path)
    print svn.export_file(u'Temporary/机电产品线/知识库/解密/新建文件夹/BOM表', 'BOM')
    print svn.export_file(path, 'BOM.xls')
