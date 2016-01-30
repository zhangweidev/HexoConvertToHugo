#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import yaml
import pytoml as toml
from datetime import datetime
import argparse
import sys


__author__ = 'zhangwei'



reload(sys)                      # reload 才能调用 setdefaultencoding 方法  
sys.setdefaultencoding('utf-8')  # 设置 'utf-8'  


content_regex = re.compile(r'([\s\S]*?)---*([\s\S]*)')
temp_regex = re.compile(r'\+\+\+*([\s\S]*?)\+\+\+*([\s\S]*)')



def write_out_file(front_data, body_text, out_file_path):
    out_lines = ['+++']
    front_string = toml.dumps(front_data)
    out_lines.extend(front_string.splitlines())
    out_lines.append('+++')
    out_lines.extend(body_text.splitlines())

    with open(out_file_path, 'w') as f:

        f.write('\n'.join(out_lines))

def convert_file(file_path,out_dir,file_temp=None):
    """
    file_path  需要转换的文件
    out_dir  文件输出目录 
    file_temp  输出模板 
    """
    filename = os.path.basename(file_path)#.replace('.','_') # 似乎标题有.会有些问题 

    temp_content =''
    m_head={}
    if file_temp:
        with open(file_temp,'r') as f:
            temp_content = f.read()
        m_temp = temp_regex.match(temp_content)
        m_head = toml.loads(m_temp.group(1))


    content = ''
    with open(file_path,'r') as f :
        content = f.read()

    m = content_regex.match(content)
    if not m:
        print 'Error match content: %s' % file_path
        return False

    front_data = yaml.load(m.group(1))
    if not front_data:
        print 'Error load yaml: %s' % file_path
        return False

    m_head['title']= front_data.get('title','')

    if front_data.get("description",None):
        m_head['description']=front_data.get("description",None)

    if front_data.get('date',None):
        #time.strftime("%Y-%m-%dT%H:%M:%S+08:00",b)
        m_head['date']=front_data.get('date',None).strftime('%Y-%m-%dT%H:%M:%S+08:00')

    m_tags = front_data.get('tags',None)
    if m_tags:
        print type(m_tags),m_tags
        m_head['tags']=[]
        if isinstance(m_tags,list):
            m_head['tags'].extend(m_tags)
        else:
            m_head['tags'].append(m_tags)
        print m_head['tags']

    m_categories = front_data.get('categories',None)
    if m_categories:
        m_head['categories']=[]
        if isinstance(m_categories,list):
            m_head['categories'].extend(m_categories)
        else:
            m_head['categories'].append(m_categories)
        print m_head['categories']
    
    write_out_file(m_head,m.group(2),out_dir+'/'+filename)

    return True 





def convert_post(file_path, out_dir):
    filename = os.path.basename(file_path)

    print filename 
    content = ''
    with open(file_path, 'r') as f:
        content = f.read()

    m = content_regex.match(content)
    if not m:
        print 'Error match content: %s' % file_path
        return False

    front_data = yaml.load(m.group(1))
    if not front_data:
        print 'Error load yaml: %s' % file_path
        return False



    #print front_data  

    '''
    保留 title tags  data categories 
    '''
    print front_data 
    data = {}
    data['title']= front_data.get('title','')
    if front_data.get('date',None):
        #time.strftime("%Y-%m-%dT%H:%M:%S+08:00",b)
        data['date']=front_data.get('date',None).strftime('%Y-%m-%dT%H:%M:%S+08:00')


    data['tags']=front_data.get('tags',None)
    if front_data.get('categories',None):
        data['categories']=front_data.get('categories',None)

    write_out_file(data,m.group(2),out_dir+'/'+filename)

    '''
    if 'layout' in front_data:
        if post_date:
            out_dir = os.path.join(out_dir, front_data['layout'], str(post_date.year))
        else:
            out_dir = os.path.join(out_dir, front_data['layout'])
    '''

    # if not os.path.exists(out_dir):
    #     os.makedirs(out_dir)

    # out_file_path = os.path.join(out_dir, filename)

    # convert_front_matter(front_data, post_date, url)
    # body_text = convert_body_text(m.group(2))
    # write_out_file(front_data, body_text, out_file_path)

    return True


def convert(src_dir, out_dir,file_temp=None):
    count = 0
    error = 0
    for root, dirs, files in os.walk(src_dir):
        for filename in files:
            try:
                if os.path.splitext(filename)[1] != '.md' or filename in ['README.md', 'LICENSE.md']:
                    continue
                file_path = os.path.join(root, filename)
                common_prefix = os.path.commonprefix([src_dir, file_path])
                rel_path = os.path.relpath(
                    os.path.dirname(file_path), common_prefix)
                real_out_dir = os.path.join(out_dir, rel_path)
                print file_path, real_out_dir
                if convert_file(file_path, real_out_dir,file_temp):
                    print 'Converted: %s' % file_path
                    count += 1
                else:
                    error += 1
            except Exception as e:
                error += 1
                print 'Error convert: %s \nException: %s' % (file_path, e)

    print '--------\n%d file converted! %s' % (count, 'Error count: %d' % error if error > 0 else 'Congratulation!!!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Hexo blog to Hugo')
    parser.add_argument('src_dir', help='hexo _posts dir')
    parser.add_argument('out_dir', help='hugo root path')
    parser.add_argument('file_temp', help='hugo theme default templete')

    args = parser.parse_args()
    print os.path.abspath(args.src_dir)
    

    convert(os.path.abspath(args.src_dir),
        os.path.abspath(args.out_dir),
        os.path.abspath(args.file_temp))

