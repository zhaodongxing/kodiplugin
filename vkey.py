import struct
import base64
import random
import time

DELTA = 0x9e3779b9
ROUNDS = 16

SALT_LEN = 2
ZERO_LEN = 7

SEED = 0xdead

def rand():
    global SEED
    if SEED == 0:
        SEED = 123459876
    k1 = 0xffffffff & (-2836 * (SEED // 127773))
    k2 = 0xffffffff & (16807 * (SEED % 127773))
    SEED = 0xffffffff & (k1 + k2)
    if SEED < 0:
        SEED = SEED + 2147483647
    return SEED

def pack(data):
    target = []
    for i in data:
        target.extend(struct.pack('>I', i))
    return target

def unpack(data):
    bytes_data = bytes(data)
    target = []
    for i in range(0, len(data), 4):
        target.extend(struct.unpack('>I', bytes_data[i:i+4]))
    return target

def tea_encrypt(v, key):
    s = 0
    key = unpack(key)
    v = unpack(v)
    for i in range(ROUNDS):
        s += DELTA
        s &= 0xffffffff
        v[0] += (v[1]+s) ^ ((v[1]>>5)+key[1]) ^ ((v[1]<<4)+key[0])
        v[0] &= 0xffffffff
        v[1] += (v[0]+s) ^ ((v[0]>>5)+key[3]) ^ ((v[0]<<4)+key[2])
        v[1] &= 0xffffffff
    return pack(v)

def oi_symmetry_encrypt2(raw_data, key):
    pad_salt_body_zero_len = 1 + SALT_LEN + len(raw_data) + ZERO_LEN
    pad_len = pad_salt_body_zero_len % 8
    if pad_len:
        pad_len = 8 - pad_len
    data = []
    data.append(rand() & 0xf8 | pad_len)
    while pad_len + SALT_LEN:
        data.append(rand() & 0xff)
        pad_len = pad_len - 1
    data.extend(raw_data)
    data.extend([0x00] * ZERO_LEN)

    temp = [0x00] * 8
    enc = tea_encrypt(data[:8], key)
    for i in range(8, len(data), 8):
        d1 = data[i:]
        for j in range(8):
            d1[j] = d1[j] ^ enc[i-8+j]
        d1 = tea_encrypt(d1, key)
        for j in range(8):
            d1[j] = d1[j] ^ data[i-8+j] ^ temp[j]
            enc.append(d1[j])
            temp[j] = enc[i-8+j]
    return enc


KEY = [
    0xfa, 0x82, 0xde, 0xb5, 0x2d, 0x4b, 0xba, 0x31,
    0x39, 0x6,  0x33, 0xee, 0xfb, 0xbf, 0xf3, 0xb6
]

def packstr(data):
    l = len(data)
    t = []
    t.append((l&0xFF00) >> 8)
    t.append(l&0xFF)
    t.extend([ord(c) for c in data])
    return t

def strsum(data):
    s = 0
    for c in data:
        s = s*131 + c
    return 0x7fffffff & s

def echo_ckeyv3(vid, guid='', t=None, player_version='3.2.38.401', platform=10902, stdfrom='bcng'):
    data = []
    data.extend(pack([21507, 3168485562]))
    data.extend(pack([platform]))

    if not t:
        t = time.time()
    seconds = int(t)
    microseconds = int(1000000*(t - int(t)))
    data.extend(pack([microseconds, seconds]))
    data.extend(packstr(stdfrom))

    r = random.random()
    data.extend(packstr('%.16f' % r))
    data.extend(packstr(player_version))
    data.extend(packstr(vid))
    data.extend(packstr('2%s' % guid))
    data.extend(packstr('4null'))
    data.extend(packstr('4null'))
    data.extend([0x00, 0x00, 0x00, 0x01])
    data.extend([0x00, 0x00, 0x00, 0x00])

    l = len(data)
    data.insert(0, l&0xFF)
    data.insert(0, (l&0xFF00) >> 8)

    enc = oi_symmetry_encrypt2(data, KEY)

    pad = [0x00, 0x00, 0x00, 0x00, 0xff&rand(), 0xff&rand(), 0xff&rand(), 0xff&rand()]
    pad[0] = pad[4] ^ 71 & 0xFF
    pad[1] = pad[5] ^ -121 & 0xFF
    pad[2] = pad[6] ^ -84 & 0xFF
    pad[3] = pad[7] ^ -86 & 0xFF

    pad.extend(enc)
    pad.extend(pack([strsum(data)]))

    result = base64.b64encode(bytes(pad), b'_-').decode('utf-8').replace('=', '')
    return result

def getfilename(lnk, stream_id, idx):
     return '{lnk}.p{num}.{idx}.mp4'.format(lnk=lnk, num=stream_id % 10 ** 3 if stream_id < 10 ** 4 else stream_id % 10 ** 4, idx=idx)



if __name__ == '__main__':
    import sys
    import uuid
    name,vid,fmt,idx,lnk = sys.argv
    fmt=int(fmt)

    appver   = '3.2.38.401'
    guid     = uuid.uuid4().hex.upper()
    platform = 11
    cKey     = echo_ckeyv3(vid=vid, guid=guid, player_version=appver, platform=platform)
    filename = getfilename(lnk, fmt, idx)
    key_api  = 'http://vv.video.qq.com/getvkey?vid={vid}&appver={appver}&platform={platform}&otype=json&filename={filename}&format={format}&cKey={cKey}&guid={guid}&charge=1&encryptVer=5.4&lnk={vid}'.format(
                    vid=vid, appver=appver, filename=filename,
                    format=fmt, cKey=cKey, guid=guid, platform=platform, lnk=lnk)
    print(key_api)
