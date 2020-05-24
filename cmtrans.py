# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import argparse, os
from tkinter import *
from tkinter.messagebox import showinfo as msgbox

def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        return r.text
    except:
        return False

def trans(to_translate, from_language="", to_language="cn"):
    base_url = "https://translate.google.cn/m?hl={}&sl={}&ie=UTF-8&q={}"
    url = base_url.format(to_language, from_language, to_translate)
    html = getHTMLText(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
    try:
        result = soup.find_all("div", {"class":"t0"})[0].text
    except:
        result = to_translate
    return result

def get_cfg():
    with open('trans-cfg.xml', 'r', encoding='utf-8') as files:
        f = files.read()
    cfg_from = f[f.find('<from>')+6:f.find('</from>')]
    cfg_to = f[f.find('<to>')+4:f.find('</to>')]
    cfg_target = f[f.find('<target>')+8:f.find('</target>')]
    cfg_file = f[f.find('<file>')+6:f.find('</file>')]
    cfg_bc_start = f[f.find('<bc-start>')+10:f.find('</bc-start>')]
    cfg_bc_body = f[f.find('<bc-body>')+9:f.find('</bc-body>')]
    cfg_bc_end = f[f.find('<bc-end>')+8:f.find('</bc-end>')]
    cfg_lc = f[f.find('<lc>')+4:f.find('</lc>')]
    cfg_cc = f[f.find('<cc>')+4:f.find('</cc>')]
    return cfg_from, cfg_to, cfg_target, cfg_file, cfg_bc_start, cfg_bc_body, cfg_bc_end, cfg_lc, cfg_cc
    

def get_text(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        filelines = f.readlines()
    bc_start, bc_body, bc_end, lc, cc = get_cfg()[4:]
    lines = []
    for line in filelines:
        if line.replace(' ','')[:len(bc_start)] == bc_start:
            lines.append(['bc', line[line.find(bc_start) + len(bc_start) : -1]])
        elif line.replace(' ','')[:len(bc_body)] == bc_body:
            lines[-1][-1] = lines[-1][1] + line[line.find(bc_body) + len(bc_body) : -1]
        elif line.replace(' ','')[:len(bc_end)] == bc_end:
            lines[-1][-1] = lines[-1][1] + line[line.find(bc_end) + len(bc_end) : -1]
        elif line.replace(' ','')[:len(lc)] == lc:
            lines.append(['lc', line[line.find(lc) + len(lc) : -1]])
        elif line.find(cc) != -1:
            lines.append(['cc', line[:line.find(cc)], line[line.find(cc)+len(cc):-1]])
        else:
            lines.append(['code', line[:-1]])
    return lines

def separate(string):
    bc_start, bc_body, bc_end, lc, cc = get_cfg()[4:]
    new = ''
    new += bc_start
    while len(string) > 0:
        if len(string) > 80:
            new += string[:80]
            string = string[80:]
            if string[0] == '.':
                new += string[0]
                string = string[1:]
            elif new[-1] == ' ':
                pass
            elif string[:2] == ' .':
                new += string[:2]
                string = string[2:]
            elif string[0] == ' ':
                new += string[0]
                string = string[1:]
            else:
                new += '-'
            new += '\n'
            new += bc_body
            new += ' '
        else:
            new += string
            string = ''
    new += '\n'
    new += bc_end
    new += '\n'
    return new

def trans_file(files):
    cfrom, cto = get_cfg()[:2]
    f = files
    for i in range(len(f)):
        if f[i][0] in ['bc', 'lc', 'cc']:
            f[i][-1] = trans(f[i][-1], cfrom, cto)
    return f

def do_that(filename):
    the_file = trans_file(get_text(filename))
    new = ''
    bc_start, bc_body, bc_end, lc, cc = get_cfg()[4:]
    for i in the_file:
        if i[0] == 'bc':
            new += separate(i[-1])
        elif i[0] == 'lc':
            new += lc + ' ' + i[-1] + '\n'
        elif i[0] == 'cc':
            new += i[1] + ' ' + cc + ' ' + i[-1] + '\n'
        elif i[0] == 'code':
            new += i[-1] + '\n'
    f = open(filename, 'w', encoding = 'utf-8')
    f.write(new)
    f.close()

def cfg_window():
    cfg_from, cfg_to, cfg_target, cfg_file, cfg_bc_start, cfg_bc_body, cfg_bc_end, cfg_lc, cfg_cc = get_cfg()
    root = Tk()
    root.title('cmtrans')
    root.geometry('220x440')
    def write():
        cfrom, cto, cfile, cbcs, cbcb, cbce, clc, ccc = efrom.get(), eto.get(), efile.get(), ebcs.get(), ebcb.get(), ebce.get(), elc.get(), ecc.get()
        f = open('trans-cfg.xml', 'w', encoding='utf-8')
        f.write('<cfg>\n    <from>{}</from>\n    <to>{}</to>\n    <file>{}</file>\n    <bc-start>{}</bc-start>\n    <bc-body>{}</bc-body>\n    <bc-end>{}</bc-end>\n    <lc>{}</lc>\n    <cc>{}</cc>\n</cfg>'.format(cfrom, cto, cfile, cbcs, cbcb, cbce, clc, ccc))
        f.close
    cmd = Button(root, text='save', command=write)
    efrom = Entry(root)
    efrom.insert(0,cfg_from)
    eto = Entry(root)
    eto.insert(0,cfg_to)
    efile = Entry(root)
    efile.insert(0,cfg_file)
    ebcs = Entry(root)
    ebcs.insert(0,cfg_bc_start)
    ebcb = Entry(root)
    ebcb.insert(0,cfg_bc_body)
    ebce = Entry(root)
    ebce.insert(0,cfg_bc_end)
    elc = Entry(root)
    elc.insert(0,cfg_lc)
    ecc = Entry(root)
    ecc.insert(0,cfg_cc)
    Label(root, text='Configuration', font=('Consolas',16)).pack()
    Label(root, text='from language').pack()
    efrom.pack()
    Label(root, text='to language').pack()
    eto.pack()
    Label(root, text='file extension').pack()
    efile.pack()
    Label(root, text='block comment start').pack()
    ebcs.pack()
    Label(root, text='block comment body').pack()
    ebcb.pack()
    Label(root, text='block comment end').pack()
    ebce.pack()
    Label(root, text='line comment').pack()
    elc.pack()
    Label(root, text='code comment').pack()
    ecc.pack()
    cmd.pack()
    root.mainloop()

def main(iters):
    print('Finding file...')
    cfile = get_cfg()[3].split('|')
    result = []
    for i in iters:
        if os.path.isfile(i) and i[i.rfind('.'):] in cfile:
            result.append(i)
        elif os.path.isdir(i):
            for j in os.listdir(i):
                if os.path.isfile(i+'\\'+j) and j[j.rfind('.'):] in cfile:
                    result.append(i+'\\'+j)
    print(str(len(result)) + ' files found.')
    for i in range(len(result)):
        print('Processing ' + str(i+1), end = '\r')
        do_that(result[i])
    print('                                       \rDone!')
    input('Press any key to continue...')

parser = argparse.ArgumentParser(description='https://github.com/DarthJesusYan/-cmtrans')
parser.add_argument('F', type=str, nargs='*')
filelist = parser.parse_args().F
if not filelist:
    cfg_window()
else:
    main(filelist)


