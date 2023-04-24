from collectors_server import Collector_Server
from utils.logger_utils import get_logger

logger = get_logger('collector2')
if __name__ == '__main__':
    collector2 = Collector_Server("Collector 2", logger, port=3002)
    collector2.start() 