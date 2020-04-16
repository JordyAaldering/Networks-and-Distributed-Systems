class Header:
    
    def __init__(self, seq_number: int, ack_number: int, flags: int, 
            window_size: int, data_length: int, checksum: int = 0):
        self.seq_number = seq_number
        self.ack_number = ack_number
        self.flags = flags
        self.window_size = window_size
        self.data_length = data_length
        self.checksum = checksum

    def ack(self) -> bool:
        return self.flags >> 2 & 1
    
    def syn(self) -> bool:
        return self.flags >> 1 & 1

    def fin(self) -> bool:
        return self.flags >> 0 & 1

    def build_flags(self, ack: bool, syn: bool, fin: bool):
        self.flags = ack << 2 | syn << 1 | fin << 0
