#!/usr/bin/env python3
"""GSMTAP Listener - Full SI parsing with neighbors and reselection"""

from scapy.all import sniff, Raw
import struct
import si2decode

RR_MSG_TYPES = {
    0x19: 'SI1', 0x1a: 'SI2', 0x1b: 'SI3',0x1c: 'SI4', 0x1d: 'SI5', 0x1e: 'SI6', 
    0x02: 'SI2bis', 0x03: 'SI2ter', 0x05: 'SI5bis', 0x06: 'SI5ter',
    0x00: 'SI13',
    0x21: 'Paging Req 1', 0x22: 'Paging Req 2', 0x24: 'Paging Req 3',
    0x3f: 'Imm Assign', 0x39: 'Imm Assign Ext',
}

CHANNEL_NAMES = {
    0x01: 'BCCH', 0x02: 'CCCH', 0x03: 'RACH', 0x04: 'AGCH',
    0x05: 'PCH', 0x06: 'SDCCH', 0x07: 'SDCCH4', 0x08: 'SDCCH8',
}

cell_info = {
    'mcc': None, 'mnc': None, 'lac': None, 'cell_id': None,
    'neighbors': set(),
    'reselection': {},
    'si_collected': set(),
}

def parse_lai(data):
    if len(data) < 5:
        return None
    mcc = ((data[0] & 0x0F) * 100) + ((data[0] >> 4) * 10) + (data[1] & 0x0F)
    mnc_digit3 = data[1] >> 4
    mnc = ((data[2] & 0x0F) * 10) + (data[2] >> 4)
    if mnc_digit3 != 0x0F:
        mnc = (mnc_digit3 * 100) + mnc
    lac = struct.unpack('>H', data[3:5])[0]
    return {'mcc': mcc, 'mnc': mnc, 'lac': lac}

def parse_arfcn_bitmap(data):
    """
    Parse GSM 'Cell Channel Description' / frequency list in bitmap-0 form (16 bytes).
    Bits are MSB-first. First 3 bits are the format identifier (should be 000 for bitmap-0).
    Next 124 bits correspond to ARFCN 1..124.
    """
    if data is None or len(data) < 16:
        return []

    data = data[:16]  # only 16 bytes matter

    # Expand to a list of bits, MSB first per byte
    bits = []
    for b in data:
        b = int(b)  # supports bytes, bytearray, list[int]
        for shift in range(7, -1, -1):
            bits.append((b >> shift) & 1)

    # First 3 bits are the format identifier for the frequency list
    fmt = bits[:3]
    # If you want to be strict, enforce bitmap-0 only:
    if fmt != [0, 0, 0]:
        return []

    arfcn_bits = bits[3:3 + 124]  # ARFCN 1..124
    arfcns = [i + 1 for i, v in enumerate(arfcn_bits) if v]

    return arfcns  # already in ascending order

    

def parse_cell_selection(data):
    """Parse Cell Selection Parameters (3GPP TS 44.018)"""
    if len(data) < 2:
        return {}
    print(f"  parse_cell_selection full: {data.hex()}")
    # Byte 0: MS_TXPWR_MAX_CCH (5 bits) + CELL_RESELECT_HYSTERESIS (3 bits)
    ms_txpwr_max = (data[0]) & 0x1F
    cell_reselect_hyst = (data[0] >> 5) & 0x07  # in dB
    
    # Byte 1: RXLEV_ACCESS_MIN (6 bits) + NECI (1 bit) + ACS (1 bit)
    rxlev_access_min = data[1] & 0x3F
    neci = (data[1] >> 6) & 0x01
    acs = (data[1] >> 7) & 0x01
    
    return {
        'ms_txpwr_max_cch': ms_txpwr_max,
        'cell_reselect_hysteresis_db': cell_reselect_hyst,
        'rxlev_access_min': rxlev_access_min,
        'rxlev_access_min_dbm': rxlev_access_min - 110,
        'neci': neci,
        'acs': acs,
    }

def parse_cell_options(data):
    """Parse Cell Options BCCH (3GPP TS 44.018)"""
    if len(data) < 1:
        return {}
    
    print(f"  parse_cell_options full: {data.hex()}")

    # PWRC (1) + DTX (2) + RADIO_LINK_TIMEOUT (4)
    pwrc = (data[0] >> 6) & 0x01
    dtx = (data[0] >> 4) & 0x03
    radio_link_timeout = ((data[0] & 0x0F))  # SACCH blocks
    
    dtx_names = {0: 'may use', 1: 'shall use', 2: 'shall not use', 3: 'reserved'}
    
    return {
        'pwrc': pwrc,
        'dtx': dtx_names.get(dtx, 'unknown'),
        'radio_link_timeout': radio_link_timeout,
    }

def parse_control_channel_desc(data):
    """Parse Control Channel Description"""
    if len(data) < 3:
        return {}
    
    print(f"  parse_control_channel_desc full: {data.hex()}")
    # Byte 0: MSC_R (1) + ATT (1) + BS_AG_BLKS_RES (3) + CCCH_CONF (3)
    msc_r = (data[0] >> 7) & 0x01
    att = (data[0] >> 6) & 0x01
    bs_ag_blks_res = (data[0] >> 3) & 0x07
    ccch_conf = data[0] & 0x07
    
    # Byte 1-2: BS_PA_MFRMS, T3212
    cbq3 = (data[1] >> 5)  & 0x03
    bs_pa_mfrms = (data[1]) & 0x07
    t3212 = data[2] 
    
    
    return {
    	'mscr': msc_r,
        'att': att,  # IMSI attach/detach allowed
        'bs_ag_blks_res': bs_ag_blks_res,
        'ccch_conf': ccch_conf,
        'cbq3': cbq3,
        'bs_pa_mfrms': bs_pa_mfrms,
        't3212_min': t3212,  # Convert to minutes
    }

#def parse_si1(payload):
#    """Parse SI1 - Cell channel description"""parse_contparse_control_channel_descrol_channel
#    info = {'type': 'SI1'}
#    if len(payload) >= 19:
#        # Cell channel description at offset 3 (16 bytes)
#        info['cell_arfcns'] = parse_arfcn_bitmap(payload[3:19])
#    return info
import struct

def parse_rach(rach):
    # 4) RACH Control Parameters (3 bytes)
    print(f"  parse_rach full: {rach.hex()}")
    rach_ctrl = {}
    if len(rach) == 3:
        rach_ctrl = {
            'max_retrans': rach[0] & 0x0F,  # Maximum retransmissions (4 bits)
            'tx_slots': rach[0] & 0x0F,  # Number of transmission slots (4 bits)
            'cell_barred': rach[0] >> 4 & 0x01,  # Cell barred flag (1 bit)
            're_establishment': rach[0] >> 7 & 0x01,  # Call re-establishment allowed flag (1 bit)
        }
        rach_ctrl['acc'] = struct.unpack('>H', rach[1:3])[0]  # Access class (2 bytes)
    return(rach_ctrl)
 
    

def parse_si1(payload):
    """Parse System Information Type 1 (SI1) message"""
    info = {'type': 'SI1'}
    # Check if the payload is long enough to include all mandatory fields
    if len(payload) < 20:
        raise ValueError("SI1 message too short")

     
    info['cell_arfcns'] = parse_arfcn_bitmap(payload[1:17])
    
    rach = payload[17:20]
    rach_ctrl = parse_rach(rach)
    info['rach'] = rach_ctrl
    #print(f"RACH Control Parameters: {rach_ctrl}")

    # 5) SI1 Rest Octets (optional)
    if len(payload) > 11:
        info['rest_octets'] = payload[20:].hex()
        print(f"SI1 Rest Octets: {info['rest_octets']}")

    return info


def parse_si2(payload):
    """Parse SI2 - Neighbor cells"""
    info = {'type': 'SI2'}
    print(f"  DEBUG full: {payload[:15].hex()}")
    
    if len(payload) >= 19:
        # Neighbor cell description at offset 3 (16 bytes)
    	"""
    	Parse GSM Cell Channel Description (SI1) in bit map 0 format (16 octets, V field).
	
    	Octet1:    print(f"  DEBUG rach: {rach.hex()} , len {len(rach)}")
    print(f"  DEBUG rach[2:4]: {rach[1:4].hex()} , len {len(rach[1:4])}")
      	bits 8-7: Format-ID (00 = bit map 0)
      	bits 6-5: spare
      	bits 4-1: CA ARFCN 124..121
    	Then octet2..octet16 carry CA ARFCN 120..1.
	
    	Returns ARFCNs in descending order (to match Wireshark style).
    	"""
    	data = payload[1:17]
    	if data is None or len(data) < 16:
        	return []
	
    	data = data[:16]
	
        results = decode_ncd(data)
        print(results)
    	# fmt = (data[0] >> 6) & 0b11
    	# if fmt != 0:
        # 	# Not bit map 0 (could be range 1024/512/256/128/variable bitmap)
        # 	return []
	
    	# # Expand to 128 bits, MSB-first per octet.
    	# bits = []
    	# for b in data:
        # 	for shift in range(7, -1, -1):
        # 		bits.append((b >> shift) & 1)
	
    	# bits[0] is bit128 (octet1 bit8). For ARFCN N, check bit index (128 - N).
    	arfcns = []
    	for n in range(1, 125):  # 1..124
    		if bits[128 - n]:
    			arfcns.append(n)

    	info['neighbor_arfcns'] = sorted(arfcns, reverse=True)
    
    	rach_ctrl = parse_rach(payload[18:21])
    	info['rach'] = rach_ctrl	
    	info['ncc_permited'] = payload[17]
		
    return info

def parse_si2bis(payload):
    """Parse SI2bis - Extended neighbor cells"""
    info = {'type': 'SI2bis'}
    if len(payload) >= 19:
        info['neighbor_arfcns'] = parse_arfcn_bitmap(payload[3:19])
    return info

def parse_si2ter(payload):
    """Parse SI2ter - Extended neighbor cells"""
    info = {'type': 'SI2ter'}
    if len(payload) >= 19:
        info['neighbor_arfcns'] = parse_arfcn_bitmap(payload[3:19])
    return info

import struct


def parse_si3(payload):
    """Parse SI3, including T3212 timer and Cell ID"""
    info = {'type': 'SI3'}
    
    # Debugging the full payload for initial inspection
    print(f"  DEBUG full: {payload.hex()}")
    
    # Check if the payload is large enough
    if len(payload) >= 10:
        cid = struct.unpack('>H', payload[1:3])[0]
    	
        # LAI at [3:8] - Location Area Identity (MCC, MNC, LAC)
        lai_bytes = payload[3:8]
        print(f"  DEBUG full: {lai_bytes.hex()}")
        
        # MCC (Mobile Country Code) extraction
        mcc = (lai_bytes[0] & 0x0F) * 100 + (lai_bytes[0] >> 4) * 10 + (lai_bytes[1] & 0x0F)
        
        # Extract 3rd MNC digit
        mnc_digit3 = lai_bytes[1] >> 4
        
        # MNC (Mobile Network Code) extraction
        mnc = (lai_bytes[2] & 0x0F) * 10 + (lai_bytes[2] >> 4)
        if mnc_digit3 != 0x0F:  # If MNC digit 3 is not 0x0F (not absent), add it
            mnc = mnc * 10 + mnc_digit3
        
        # LAC (Location Area Code) extraction
        lac = struct.unpack('>H', lai_bytes[3:6])[0]
        
        # Debugging LAI extraction
        print(f"  LAI bytes: {lai_bytes.hex()} -> MCC:{mcc} MNC:{mnc} LAC:{lac}")
                
        # Add the parsed values to info dictionary
        info['Control Channel Description'] = parse_control_channel_desc(payload[8:11])
        info['Cell Options'] = parse_cell_options(payload[11:12])
        info['Cell Selection Parameters'] = parse_cell_selection(payload[12:14])
        info['mcc'] = mcc
        info['mnc'] = mnc
        info['lac'] = lac
        info['cid'] = cid
        
    
    # If the payload is too short, return an error or empty info
    else:
        print("ERROR: Payload is too short to parse.")
    
    return info


def parse_si4(payload):
    """Parse SI4 - LAI, cell selection, RACH control"""
    info = {'type': 'SI4'}
    if len(payload) >= 12:
        # LAI at offset 3-7
        lai = parse_lai(payload[3:8])
        if lai:
            info.update(lai)
        
        # Cell Selection Parameters at offset 8-9
        cell_sel = parse_cell_selection(payload[8:10])
        info['Cell Selection Parameters'] = cell_sel
        
        rach_ctrl = parse_rach(payload[10:13])
        info['RACH Control Parameters'] = rach_ctrl	
        
        # RACH Control Parameters at offset 10-12
    return info
    
def parse_si5(payload):
    """Parse SI4 - LAI, cell selection, RACH control"""
    info = {'type': 'SI5'}
    print(f"  DEBUG SI5 full: {payload.hex()}")
    if len(payload) >= 12:
        data = payload[2:16]
        if data is None or len(data) < 16:
            return []
	
        data = data[:16]
	
        fmt = (data[0] >> 6) & 0b11
        if fmt != 0:
            # Not bit map 0 (could be range 1024/512/256/128/variable bitmap)
            return []
	
        # Expand to 128 bits, MSB-first per octet.
        bits = []
        for b in data:
            for shift in range(7, -1, -1):
        	    bits.append((b >> shift) & 1)
	
        # bits[0] is bit128 (octet1 bit8). For ARFCN N, check bit index (128 - N).
        arfcns = []
        for n in range(1, 125):  # 1..124
            if bits[128 - n]:
                arfcns.append(n)

        info['neighbor_arfcns'] = sorted(arfcns, reverse=True)
    	
    return info

def handle_packet(pkt):
    global cell_info
    
    if not pkt.haslayer(Raw):
        return
        
 #   if pkt.haslayer(Raw):
 #       gsmtap = bytes(pkt[Raw].load)
 #       print(f"Full packet ({len(gsmtap)} bytes): {gsmtap.hex()}")
        
    gsmtap = bytes(pkt[Raw].load)
    if len(gsmtap) < 16:
        return
    
    hdr_len = gsmtap[1] * 4
    arfcn = struct.unpack('>H', gsmtap[4:6])[0] & 0x3FFF
    signal_dbm = struct.unpack('b', gsmtap[6:7])[0]
    sub_type = gsmtap[12]
    channel = CHANNEL_NAMES.get(sub_type, f'0x{sub_type:02x}')
    
    payload = gsmtap[hdr_len:]
    if len(payload) < 3:
        return
    
    msg_type = payload[2]
    msg_name = RR_MSG_TYPES.get(msg_type, f'0x{msg_type:02x}')
    
    # Skip non-SI messages for cleaner output
    if not msg_name.startswith('SI'):
        return
    
    print(f"\n[ARFCN {arfcn}] [{channel}] {msg_name} | {signal_dbm} dBm")
    
    # Parse based on message type
    if msg_type == 0x19:  # SI1
        info = parse_si1(payload[2:])
        print(f"  SI1: {info}")
        #if 'cell_arfcns' in info:
        #    print(f"  Cell ARFCNs: {info['cell_arfcns']}")
    
    elif msg_type == 0x1a:  # SI2
        info = parse_si2(payload[2:])
        print(f"  SI2: {info}")
        #if 'neighbor_arfcns' in info:
        #    cell_info['neighbors'].update(info['neighbor_arfcns'])
        #    print(f"  Neighbor ARFCNs: {info['neighbor_arfcns']}")
    
    elif msg_type == 0x02:  # SI2bis
        info = parse_si2bis(payload)
        print(f"  SI2bis: {info}")
        #if 'neighbor_arfcns' in info:
        #    cell_info['neighbors'].update(info['neighbor_arfcns'])
        #    print(f"  Neighbor ARFCNs (bis): {info['neighbor_arfcns']}")
    
    elif msg_type == 0x03:  # SI2ter
        info = parse_si2ter(payload)
        print(f"  SI2ter: {info}")
        #if 'neighbor_arfcns' in info:
        #    cell_info['neighbors'].update(info['neighbor_arfcns'])
        #    print(f"  Neighbor ARFCNs (ter): {info['neighbor_arfcns']}")
    
    elif msg_type == 0x1b:  # SI3
        info = parse_si3(payload[2:])
        print(f"  SI3: {info}")
        #if 'cell_id' in info:
        #    cell_info['cell_id'] = info['cell_id']
        #    cell_info['mcc'] = info.get('mcc')
        #    cell_info['mnc'] = info.get('mnc')
        #    cell_info['lac'] = info.get('lac')
        #    print(f"  Cell ID: {info['cell_id']}")
        #    print(f"  MCC: {info.get('mcc')} | MNC: {info.get('mnc')} | LAC: {info.get('lac')}")
        
        #if 'cell_selection' in info:
        #    cs = info['cell_selection']
        #    cell_info['reselection'].update(cs)
        #    print(f"  Cell Selection:")
        #    print(f"    RXLEV_ACCESS_MIN: {cs.get('rxlev_access_min_dbm')} dBm")
        #    print(f"    Cell Reselect Hysteresis: {cs.get('cell_reselect_hysteresis_db')} dB")
        #    print(f"    MS_TXPWR_MAX_CCH: {cs.get('ms_txpwr_max_cch')}")
        
        #if 'cell_options' in info:
        #    co = info['cell_options']
        #    cell_info['reselection'].update(co)
        #    print(f"  Cell Options:")
        #    print(f"    DTX: {co.get('dtx')}")
        #    print(f"    Radio Link Timeout: {co.get('radio_link_timeout')} SACCH blocks")
        
        #if 'control_channel' in info:
        #    cc = info['control_channel']
        #    cell_info['reselection'].update(cc)
        #    print(f"  Control Channel:")
        #    print(f"    ATT (IMSI attach): {cc.get('att')}")
        #    print(f"    T3212: {cc.get('t3212_min')} min")
        #    print(f"    CCCH Config: {cc.get('ccch_conf')}")
    
    elif msg_type == 0x1c:  # SI4
        info = parse_si4(payload)
        print(f"  SI4: {info}")
        #if 'cell_selection' in info:
        #    cs = info['cell_selection']
        #    print(f"  Cell Selection:")
        #    print(f"    RXLEV_ACCESS_MIN: {cs.get('rxlev_access_min_dbm')} dBm")
        #    print(f"    Cell Reselect Hysteresis: {cs.get('cell_reselect_hysteresis_db')} dB")
        
    elif msg_type == 0x1d:  # SI5
        info = parse_si5(payload)
        print(f"  SI5: {info}")
        
    cell_info['si_collected'].add(msg_name)
    print(f"  [Collected: {sorted(cell_info['si_collected'])}]")

def print_summary():
    print("\n" + "=" * 60)
    print("CELL SUMMARY")
    print("=" * 60)
    print(f"MCC: {cell_info['mcc']}")
    print(f"MNC: {cell_info['mnc']}")
    print(f"LAC: {cell_info['lac']}")
    print(f"Cell ID: {cell_info['cell_id']}")
    print(f"\nNeighbor ARFCNs ({len(cell_info['neighbors'])}): {sorted(cell_info['neighbors'])}")
    print(f"\nReselection Parameters:")
    for k, v in cell_info['reselection'].items():
        print(f"  {k}: {v}")
    print(f"\nSI Types Collected: {sorted(cell_info['si_collected'])}")

print("GSMTAP Listener - Neighbors & Reselection")
print("Run: grgsm_livemon -f <freq>")
print("=" * 60)

try:
    sniff(iface='lo', filter='udp port 4729', prn=handle_packet)
except KeyboardInterrupt:
    print_summary()
