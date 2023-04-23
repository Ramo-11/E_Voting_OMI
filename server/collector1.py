from collectors_server import Collector_Server

if __name__ == '__main__':
    collector1 = Collector_Server("Collector 1", port=3001)
    collector1.start()