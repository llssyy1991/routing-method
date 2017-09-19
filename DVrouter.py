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
        self.last        = None

    def handlePacket(self, port, packet):
        """TODO: process incoming packet"""

        if packet.isTraceroute():
            if packet.dstAddr in self.routersNext:
                next = self.routersNext[packet.dstAddr]
                self.send(self.routersPort[next], packet)

        if packet.isRouting():
            rtn = self.updateNode(packet.content)
            # if self.addr == "G":
            #     print packet.content
            if rtn != None:
                for port in self.routersAddr:
                    content = {}
                    content["src"]  = self.addr
                    content["dst"]  = rtn[1]
                    content["cost"] = rtn[2]
                    contents        = dumps(content)
                    packet = Packet(Packet.ROUTING, self.addr, self.routersAddr[port], contents)

                    self.send(port, packet)

    def handleNewLink(self, port, endpoint, cost):
        """TODO: handle new link"""
        for router in self.routersPort :

            # notify all node connected
            if endpoint not in self.routersCost :

                content        = {}
                content["src"] = self.addr
                content["dst"] = endpoint
                content["cost"]= cost
                contents       = dumps(content)
                pack           = Packet(Packet.ROUTING, self.addr, router, contents)

                self.send(self.routersPort[router], pack)

            elif self.routersCost[endpoint] > cost :
                content = {}
                content["src"] = self.addr
                content["dst"] = endpoint
                content["cost"] = cost
                contents = dumps(content)
                pack = Packet(Packet.ROUTING, self.addr, router, contents)

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
        self.routersAddr[port] = endpoint
        if endpoint not in self.routersCost:
            self.routersCost[endpoint] = cost
            self.routersNext[endpoint] = endpoint
        elif self.routersCost[endpoint] > cost:
            self.routersCost[endpoint] = cost
            self.routersNext[endpoint] = endpoint

    def updateNode(self, content):
        data = loads(content)
        src  = data["src"]
        dst  = data["dst"]
        cost = data["cost"]

        if dst not in self.routersCost:
            if src in self.routersCost:
                self.routersCost[dst] = self.routersCost[src] + cost
                self.routersNext[dst] = self.routersNext[src]
                return True, dst, self.routersCost[dst]

        if dst in self.routersCost:
            if src in self.routersCost:
                if (self.routersCost[dst] > self.routersCost[src] + cost) or (self.routersCost[dst] < self.routersCost[src] + cost and self.routersNext[dst] == src and src != dst):
                    print "dst is : " + dst
                    print "src is : " + src
                    print self.routersCost[src] + cost
                    self.routersCost[dst] = self.routersCost[src] + cost
                    self.routersNext[dst] = self.routersNext[src]
                    return True, dst, self.routersCost[dst]

        return None


    def handleRemoveLink(self, port):
        """TODO: handle removed link"""
        addr                   = self.routersAddr[port]
        self.routersCost[addr] = 16
        for address in self.routersNext:
            if self.routersNext[address] == addr :
                self.routersCost[address] = 16


    def handleTime(self, timeMillisecs):
        """TODO: handle current time"""
        if self.last == None or timeMillisecs - self.last > self.heartBeat:
            self.last = timeMillisecs

            for addr1 in self.routersPort:
                for dst in self.routersCost:
                    content = {}
                    content["src"] = self.addr
                    content["dst"] = dst
                    content["cost"] = self.routersCost[dst]
                    contents = dumps(content)
                    pack = Packet(Packet.ROUTING, self.addr, addr1, contents)

                    self.send(self.routersPort[addr1], pack)


    def debugString(self):
        """TODO: generate a string for debugging in network visualizer"""
        out = str(self.routersNext) + "\n\n\n\n\n"
        return out
        return ""
