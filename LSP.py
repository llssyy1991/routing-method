from packetReader import packetReader

class LSP(object):

    def __init__(self, addr, squence, cost):

        self.addr       = addr
        self.squence    = squence
        self.costs      = cost

    def updateLSP(self, packetIn):
        rtn = True
        if self.squence >= packetIn.getSquence():
            return False
        self.squence   = packetIn.getSquence()
        if self.costs == packetIn.getCosts():
            return False
        if self.costs != packetIn.getCosts():
            self.costs = packetIn.getCosts()
            return True
