####################################################
# DVrouter.py
# Names:
# NetIds:
#####################################################

import sys
from collections import defaultdict
from router import Router
from packet import Packet
from json import dumps, loads


class DVrouter(Router):
    """Distance vector routing protocol implementation."""

    def __init__(self, addr, heartbeatTime):
        """TODO: add your own class fields and initialization code here"""
        Router.__init__(self, addr)  # initialize superclass - don't remove
        self.routersPort = {}
        self.routersCost = {}
        self.routersNext = {}
        self.routersAddr = {}
        self.heartBeat   = heartbeatTime

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""

        if packet.isTraceroute():
            if packet.dstAddr in self.routersNext:
                next = self.routersNext[packet.dstAddr]
                self.send(self.routersPort[next], packet)

        if packet.isRouting():
            print "here"
            rtn = self.updateNode(packet.content)
            if rtn:
                for port in self.routersAddr:
                    content = {}
                    content["src"]  = self.addr
                    content["dst"]  = rtn[1]
                    content["cost"] = rtn[2]
                    contents        = dumps(content)
                    packet = Packet(Packet.ROUTING, self.addr, self.routersAddr[port], contents)

                    self.send(port, packet)
                    # if self.addr == "A":
                    #     print self.routersCost

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        for router in self.routersPort :

            # notify all node connected
            content        = {}
            content["src"] = self.addr
            content["dst"] = endpoint
            content["cost"]= cost
            contents       = dumps(content)
            pack           = Packet(Packet.ROUTING, self.addr, router, contents)

            self.send(self.routersPort[router], pack)

            # inform all the router info
            # TODO : the situation that undirect is smaller
            content["dst"] = router
            content["cost"]= self.routersCost[router]
            contents       = dumps(content)
            pack           = Packet(Packet.ROUTING, self.addr, endpoint, contents)

            self.send(port, pack)

        # inform all the router information to the new node

        self.routersPort[endpoint] = port
        self.routersCost[endpoint] = cost
        self.routersNext[endpoint] = endpoint
        self.routersAddr[port]     = endpoint

    def updateNode(self, content):
        data = loads(content)
        src  = data["src"]
        dst  = data["dst"]
        cost = data["cost"]
        if self.addr == "b":
            print "src is :  " + src
            print "dst is :  " + dst
            print "cost is : " + str(cost)
        if dst not in self.routersCost:
            if src in self.routersCost:
                # f self.routersCost[dst] > self.routersCost[src] + cost :
                self.routersCost[dst] = self.routersCost[src] + cost
                self.routersNext[dst] = src
                return True, dst, self.routersCost[dst]

        if dst in self.routersCost:
            if src in self.routersCost:
                if self.routersCost[dst] > self.routersCost[src] + cost:
                    self.routersCost[dst] = self.routersCost[src] + cost
                    self.routersNext[dst] = src
                    return True, dst, self.routersCost[dst]


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        pass


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        pass


    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        return ""
