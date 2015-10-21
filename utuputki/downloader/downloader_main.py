# -*- coding: utf-8 -*-

import os
import mimetypes

if __name__ == '__main__':
    print("Utuputki2 Downloader Daemon starting up ...")
    os.sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from runner import Runner

    mimetypes.init()
    runner = Runner()
    runner.run()
    runner.close()
