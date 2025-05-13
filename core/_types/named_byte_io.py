import io

class NamedByteIO(io.BytesIO):
    """
    A subclass of BytesIO that allows for a name to be associated with the stream.
    This can be useful for debugging or logging purposes.
    """

    def __init__(self, *args, name: str = "audio.wav", **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name if name is not None else "Unnamed"