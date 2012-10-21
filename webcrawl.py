#!/usr/bin/env python


import manager

def main():
    mg = manager.Manager("http://www.baidu.com/", 1)
    mg.poll()

if __name__ == '__main__':
    main()
