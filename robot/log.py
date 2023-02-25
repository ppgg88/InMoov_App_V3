import logging
import time

name = "log/Robot_"+time.strftime("%d_%m_%Y-%H_%M_%S",time.localtime())+".log"
logging.basicConfig(level=logging.DEBUG,
        filename=name,
        filemode="a",
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S')