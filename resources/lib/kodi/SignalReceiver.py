class SignalReceiver(xbmc.Monitor):
    def __init__(self):
        self._slots = {}

    def registerSlot(self, signaler_id, signal, callback):
        if signaler_id not in self._slots:
            self._slots[signaler_id] = {}
        self._slots[signaler_id][signal] = callback

    def unRegisterSlot(self, signaler_id, signal):
        if signaler_id not in self._slots:
            return
        if signal not in self._slots[signaler_id]:
            return
        del self._slots[signaler_id][signal]

    def onNotification(self, sender, method, data):
        if not sender[-7:] == '.SIGNAL':
            return
        sender = sender[:-7]
        if sender not in self._slots:
            return
        signal = method.split('.', 1)[-1]
        if signal not in self._slots[sender]:
            return
        self._slots[sender][signal](self._decodeData(data))

    def _decodeData(self, data):
        data = json.loads(data)
        if data:
            return json.loads(binascii.unhexlify(data[0]))
