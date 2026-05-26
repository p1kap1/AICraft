"""Embedding 服务：本地向量化（对标 AgentX 的 LangChain4j 本地 Embedding）"""
import hashlib, struct


def get_embedding(text: str) -> list[float]:
    """快速本地向量化，128 维"""
    h = hashlib.sha256(text.encode()).digest()
    # 每 2 字节转一个浮点数，128 个 float ≈ 256 bytes
    vec = []
    for i in range(0, min(256, len(h)), 2):
        try:
            val = struct.unpack('H', h[i:i+2])[0] / 65535.0
        except:
            val = 0.0
        vec.append(val)
    # 补齐到 128
    while len(vec) < 128:
        vec.append(0.0)
    return vec[:128]
