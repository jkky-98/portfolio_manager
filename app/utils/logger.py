import logging


logger = logging.getLogger("logger")
f_hdlr = logging.FileHandler("./logger.log")
s_hdlr = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
s_hdlr.setFormatter(formatter)

logger.addHandler(f_hdlr)
logger.addHandler(s_hdlr)
logger.setLevel(logging.DEBUG)
