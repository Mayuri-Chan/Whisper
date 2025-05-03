import aiofiles
import os

from aiohttp import web
from datetime import datetime
from whisper.route import Route


class Transcribe:
    @Route.post("/v1/transcribe")
    async def transcribe(self, request):
        """
        Transcribe audio file
        """
        reader = await request.multipart()
        # Get the file
        field = await reader.next()
        if field is None:
            return web.json_response({"error": "No file found"}, status=400)
        if field.name != "file":
            return web.json_response({"error": "Invalid file field"}, status=400)
        # Get the file extension
        file_name = field.filename
        if not file_name:
            return web.json_response({"error": "No file name found"}, status=400)
        ext = file_name.split(".")[-1]
        file_name = f"audio-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.{ext}"
        # Save the file
        if not os.path.exists("tmp"):
            os.makedirs("tmp")
        async with aiofiles.open(f"tmp/{file_name}", "wb") as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                await f.write(chunk)
        transcription = await self.run_sync(self.model.transcribe, f"tmp/{file_name}")
        # Remove the file
        os.remove(f"tmp/{file_name}")
        if transcription is None:
            data = {"status": "error", "message": "Transcription failed"}
            return web.json_response(data, status=500)
        text = ""
        for segment in transcription:
            text += segment.text
        data = {
            "status": "ok",
            "text": text
        }
        return web.json_response(data)
