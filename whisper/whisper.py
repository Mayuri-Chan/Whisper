import asyncio
import colorlog
import functools
import logging
import re

from aiohttp import web
from datetime import datetime
from pywhispercpp.model import Model
from typing import Callable, Any, TypeVar
from whisper import CONFIG
from whisper.route import routes_list
from whisper.routes import Routes


class Whisper(web.Application, Routes):
    def __init__(self, *args, **kwargs):
        "__init__"
        self.config = CONFIG
        super().__init__(client_max_size=self.config["whisper"]["max_audio_size"], *args, **kwargs)
        self._log = logging.getLogger("Whisper")
        self.model = Model(self.config["whisper"]["model"], print_realtime=False, print_progress=False)

    async def run(self):
        self._setup_log()
        self.middlewares.append(self._access_log_middleware)
        self._log.info("Whisper is starting up...")
        self.add_routes(routes_list)
        runner = web.AppRunner(self)
        await runner.setup()
        site = web.TCPSite(runner, host=self.config["app"]["HOST"], port=self.config["app"]["PORT"])
        await site.start()
        self._log.info("Whisper is running on %s:%s", self.config["app"]["HOST"], self.config["app"]["PORT"])
        while True:
            try:
                await asyncio.sleep(3600)
            except asyncio.exceptions.CancelledError:
                await runner.cleanup()
                self._log.info("Whisper is shutting down...")
                break

    def _setup_log(self):
        """Configures logging"""
        level = logging.INFO
        logging.root.setLevel(level)

        # Color log config
        log_color: bool = True

        file_format = "[ %(asctime)s: %(levelname)-8s ] %(name)-15s - %(message)s"
        logfile = logging.FileHandler("MayuriBin.log")
        formatter = logging.Formatter(file_format, datefmt="%H:%M:%S")
        logfile.setFormatter(formatter)
        logfile.setLevel(level)

        if log_color:
            formatter = colorlog.ColoredFormatter(
                "  %(log_color)s%(levelname)-8s%(reset)s  |  "
                "%(name)-15s  |  %(log_color)s%(message)s%(reset)s"
            )
        else:
            formatter = logging.Formatter("  %(levelname)-8s  |  %(name)-15s  |  %(message)s")
        stream = logging.StreamHandler()
        stream.setLevel(level)
        stream.setFormatter(formatter)

        root = logging.getLogger()
        root.setLevel(level)
        root.addHandler(stream)
        root.addHandler(logfile)

        # Logging necessary for selected libs
        logging.getLogger("aiohttp").setLevel(logging.WARNING)
        logging.getLogger("pywhispercpp").setLevel(logging.WARNING)

    @web.middleware
    async def _access_log_middleware(self, request, handler):
        try:
            response = await handler(request)
            status = response.status
        except web.HTTPException as ex:
            response = ex
            status = ex.status
        finally:
            if (
                not re.search(r'^/static/', request.path)
                and not re.search(r'^/favicon.ico', request.path)
            ):
                access_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if response.status == 200:
                    self._log.info(
                        '%s "%s %s HTTP/%d.%d" %s [%s]',
                        request.headers.get('X-Real-IP', request.remote),
                        request.method,
                        request.path,
                        request.version.major,
                        request.version.minor,
                        status,
                        access_time
                    )
                elif response.status < 500:
                    self._log.warning(
                        '%s "%s %s HTTP/%d.%d" %s [%s]',
                        request.headers.get('X-Real-IP', request.remote),
                        request.method,
                        request.path,
                        request.version.major,
                        request.version.minor,
                        status,
                        access_time
                    )
                else:
                    self._log.error(
                        '%s "%s %s HTTP/%d.%d" %s [%s]',
                        request.headers.get('X-Real-IP', request.remote),
                        request.method,
                        request.path,
                        request.version.major,
                        request.version.minor,
                        status,
                        access_time
                    )
        return response
    
    async def run_sync(self, func: Callable[..., TypeVar("Result")], *args: Any, **kwargs: Any) -> TypeVar("Result"):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
