from collectors_server import Collector_Server
from utils.logger_utils import get_logger

logger = get_logger('collector1')

if __name__ == '__main__':
    collector1 = Collector_Server("Collector 1", logger, port=3001)
    collector1.start()