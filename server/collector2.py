from collectors_server import Collector_Server

if __name__ == '__main__':
    collector2 = Collector_Server("Collector 2", port=3002)
    collector2.start() 