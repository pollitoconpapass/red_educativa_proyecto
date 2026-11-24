#!/usr/bin/env python3
"""Controlador SDN de EduNet (Ryu + OpenFlow 1.3).

Switch L2 aprendido + ACL de documentos calculada desde PERMISO_ACCESO:
por cada host y cada documento sin permiso en la BD instala un `drop` de
prioridad 100, por encima del reenvío L2 (prioridad 10).

Arranque:  ryu-manager sdn_controlador.py
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.lib.packet import ether_types, ethernet, packet
from ryu.ofproto import ofproto_v1_3

from config import db
from config import config as cfg
from config.politica import reglas_denegadas

PRIO_ACL = 100
PRIO_L2 = 10


class EduNet(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_a_puerto = {}

        # Sin BD no hay política: es preferible no arrancar antes que dejar la red abierta.
        documentos, permisos = db.cargar_estado()
        self.reglas = reglas_denegadas(cfg.HOSTS, documentos, permisos)
        self.logger.info(
            "BD leida: %d documentos, %d permisos, %d reglas de bloqueo por switch",
            len(documentos), len(permisos), len(self.reglas),
        )

    def _add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        instrucciones = [
            parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)
        ]
        datapath.send_msg(parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match,
            instructions=instrucciones,
        ))

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Tabla-miss: todo paquete desconocido va al controlador (aprendizaje L2).
        self._add_flow(
            datapath, 0, parser.OFPMatch(),
            [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)],
        )

        # ACL de documentos. Una regla sin acciones descarta el paquete.
        for regla in self.reglas:
            match = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=6,  # TCP
                eth_src=regla["mac_src"],
                ipv4_dst=regla["ip_dst"],
                tcp_dst=regla["puerto"],
            )
            self._add_flow(datapath, PRIO_ACL, match, [])

        self.logger.info("Switch 0x%x conectado: %d reglas ACL instaladas",
                         datapath.id, len(self.reglas))

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match["in_port"]

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth is None or eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        puertos = self.mac_a_puerto.setdefault(datapath.id, {})
        puertos[eth.src] = in_port
        out_port = puertos.get(eth.dst, ofproto.OFPP_FLOOD)

        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=eth.dst, eth_src=eth.src)
            self._add_flow(datapath, PRIO_L2, match,
                           [parser.OFPActionOutput(out_port)])

        # Si el paquete venía en buffer, data debe ir vacío.
        data = None if msg.buffer_id != ofproto.OFP_NO_BUFFER else msg.data
        datapath.send_msg(parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=in_port,
            actions=[parser.OFPActionOutput(out_port)], data=data,
        ))
