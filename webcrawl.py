#!/usr/bin/env python


import manager

def main():
    mg = manager.Manager("http://www.python.org", 0)
    mg.poll()

if __name__ == '__main__':
    main()
