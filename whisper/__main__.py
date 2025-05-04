import asyncio
import uvloop

from whisper.whisper import Whisper

if __name__ == "__main__":
    uvloop.install()
    try:
        asyncio.run(Whisper().run())
    except KeyboardInterrupt:
        pass
