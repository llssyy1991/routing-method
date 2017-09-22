from json import dumps, loads

class packetReader(object):
    # packet content format :
    # {
    #   "addr" :  str
    #   "squence" : int
    #   "costs"   :{ str (addr) : int
    #                .........
    #               }
    # }

    def __init__(self, LSPIn):

        self.data = loads(LSPIn)

    def getAddr(self):
        return self.data["addr"]

    def getSquence(self):
        return self.data["squence"]

    def getCosts(self):
        return self.data["costs"]


class packetWriter(object):
    pass

