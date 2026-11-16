#!/usr/bin/env python3
"""Topología Mininet de EduNet: 5 sedes en cascada, 1 switch y 2 hosts por sede.

Arranque (con el controlador ya corriendo):  sudo python3 topologia.py
"""

from config import config as cfg
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.topo import Topo

class EduNet(Topo):
    def build(self):
        anterior = None
        for sede in cfg.SEDES:
            switch = self.addSwitch(sede["switch"], protocols="OpenFlow13")
            if anterior is not None:
                self.addLink(anterior, switch)
            anterior = switch
            for host in sede["hosts"]:
                nodo = self.addHost(
                    host["nombre"],
                    ip=f"{host['ip']}/24",
                    mac=host["mac"],
                    defaultRoute=None,
                )
                self.addLink(nodo, switch)


def main():
    setLogLevel("info")
    red = Mininet(topo=EduNet(), controller=RemoteController,
                  switch=OVSKernelSwitch, autoSetMacs=False, autoStaticArp=True)
    red.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)
    red.start()
    CLI(red)
    red.stop()


if __name__ == "__main__":
    main()
