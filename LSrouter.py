####################################################
# LSrouter.py
# Names:
# NetIds:
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads
from LSP import LSP
from packetReader import packetReader
from Queue import PriorityQueue

COST_MAXIMUM = 16


class LSrouter(Router):
    """Link state routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.routersLSP  = {}
        self.routersAddr = {}
        self.routersPort = {}
        self.routersNext = {}
        self.routersCost = {}
        self.sequence    = 0
        self.routersLSP[self.addr] = LSP(self.addr, 0, {})
        self.last        = None
        self.heartBeat   = heartbeatTime


    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""
        transfer = False
        if packet.isRouting():
            # self.packet = packet
            if packet.srcAddr == packet.dstAddr:
                return
            reader       = packetReader(packet.content)

            if reader.getAddr() not in self.routersLSP:
                self.routersLSP[reader.getAddr()]  = LSP(reader.getAddr(),
                                                         reader.getSquence(),
                                                         reader.getCosts())
                transfer = True
            if self.routersLSP[reader.getAddr()].updateLSP(reader):
                transfer = True

            if transfer:
                for portNext in self.routersAddr:
                    if portNext != port:
                        packet.srcAddr = self.addr
                        packet.dstAddr = self.routersAddr[portNext]
                        self.send(portNext, packet)

        if packet.isTraceroute():
            try :
                if packet.dstAddr in self.routersNext:
                    self.send(self.routersPort[self.routersNext[packet.dstAddr]], packet)
            except:
                print "addr : " + self.addr
                print "routeNext : " + str(self.routersNext)
                print "packetDst : " + packet.dstAddr


    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        self.routersAddr[port]                     = endpoint
        self.routersPort[endpoint]                 = port
        self.routersLSP[self.addr].costs[endpoint] = cost
        for port in self.routersAddr:
            self.send(port, self.LSPUpdatePacket(self.routersAddr[port]))

    def LSPUpdatePacket(self, dst):
        return Packet(Packet.ROUTING, self.addr, dst, self.LSPUpdateContent())


    def LSPUpdateContent(self):

        content = {}
        content["addr"]     = self.addr
        content["squence"]  = self.sequence
        content["costs"]    = self.routersLSP[self.addr].costs
        self.sequence      += 1
        return dumps(content)

    def calPath(self):
        self.setCostMax()
        Q = PriorityQueue()
        for addr, cost in self.routersLSP[self.addr].costs.items():
            Q.put((cost, addr, addr))
        while not Q.empty():
            Cost, Next, addrP = Q.get(False)
            if addrP not in self.routersCost or Cost < self.routersCost[addrP]:
                self.routersCost[addrP] = Cost
                self.routersNext[addrP] = Next
                if addrP in self.routersLSP:
                    for pres, cost in self.routersLSP[addrP].costs.items():
                        Q.put((cost + Cost, Next, pres))


    def setCostMax(self):
        for addr in self.routersCost:
            self.routersCost[addr] = COST_MAXIMUM
        self.routersCost[self.addr] = 0
        self.routersNext[self.addr] = self.addr

    def handleRemoveLink(self, port):
        """TODO: handle removed link"""

        pass


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        if self.last == None or timeMillisecs - self.last > self.heartBeat:
            self.last = timeMillisecs
            self.calPath()

    def updateNode(self, contents):
        pass

    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""

        # return str(self.packet.srcAddr) + "\t" \
        #        + str(self.packet.dstAddr) + '\t' \
        #         + str(self.packet.content)

        return str(self.routersNext)
