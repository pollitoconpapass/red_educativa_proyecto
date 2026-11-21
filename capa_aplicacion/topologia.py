#!/usr/bin/env python3
"""Topología Mininet de EduNet: 5 sedes en cascada, 1 switch y 2 hosts por sede.

Arranque (con el controlador ya corriendo):  sudo python3 topologia.py
"""

from config import config as cfg
from mininet.cli import CLI
from mininet.log import setLogLevel, warn
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
    # controller=None: Mininet crearia un c0 extra (mismo nombre) y el
    # ovs-vsctl de cada switch fallaria por id duplicado.
    red = Mininet(topo=EduNet(), controller=None,
                  switch=OVSKernelSwitch, autoSetMacs=False, autoStaticArp=True,
                  waitConnected=True)
    red.addController("c0", controller=RemoteController, ip="127.0.0.1", port=6653)
    # NAT: los hosts necesitan salir para consultar MySQL en la VM de datos.
    nat = red.addNAT()
    nat.configDefault()
    # addNAT() supone hosts en /8 y su gateway queda fuera de nuestras /24,
    # asi que la ruta por defecto se agrega con "onlink" y el ARP del gateway
    # es estatico (autoStaticArp corre en build(), antes de que exista nat0).
    for host in red.hosts:
        if host is not nat:
            # Primero la ruta: arp -s necesita saber por que interfaz sale.
            host.cmd(f"ip route replace default via {nat.IP()} "
                     f"dev {host.defaultIntf()} onlink")
            host.setARP(nat.IP(), nat.MAC())
    red.start()

    # Sin Ryu los switches no reenvian ni el ARP del gateway: mejor avisar aqui.
    if " 1 received" not in red["doc_carlos"].cmd(
            f"ping -c1 -W2 -q {nat.IP()}"):
        warn("*** El gateway NAT %s no responde: revisa que ryu-manager "
             "siga corriendo y conectado a los switches.\n" % nat.IP())
    CLI(red)
    red.stop()


if __name__ == "__main__":
    main()
