#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import manager

def main():
    mg = manager.Manager("http://www.baidu.com/", "baidu.db", 1, "千千静听")
    mg.poll()

if __name__ == '__main__':
    main()
