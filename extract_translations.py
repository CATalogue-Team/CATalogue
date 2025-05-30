# -*- coding: utf-8 -*-
import os
import subprocess

def main():
    os.system('chcp 65001 > nul')
    subprocess.run([
        'pybabel', 
        'extract',
        '-F', 'babel.cfg',
        '-o', 'messages.pot',
        '.'
    ], check=True)

if __name__ == '__main__':
    main()
