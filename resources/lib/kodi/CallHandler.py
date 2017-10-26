class CallHandler:
    def __init__(self, signal, data, source_id, timeout=1000):
        self.signal = signal
        self.data = data
        self.timeout = timeout
        self.sourceID = source_id
        self._return = None
        registerSlot(self.sourceID, '_return.{0}'.format(self.signal), self.callback)
        sendSignal(signal, data, self.sourceID)

    def callback(self, data):
        self._return = data

    def waitForReturn(self):
        waited = 0
        while waited < self.timeout:
            if self._return is not None:
                break
            xbmc.sleep(100)
            waited += 100
        self.unRegisterSlot(self.sourceID, self.signal)
        return self._return

    def registerSlot(self, signaler_id, signal, callback):
        receiver = _getReceiver()
        receiver.registerSlot(signaler_id, signal, callback)

    def unRegisterSlot(self, signaler_id, signal):
        receiver = _getReceiver()
        receiver.unRegisterSlot(signaler_id, signal)
