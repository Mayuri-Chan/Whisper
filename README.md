# Self-hosted whisper api  

## Requirements  
- python3.10  
- ffmpeg  

## Usage  

### bash   
```bash
curl -X POST -F "file=@/path/to/audio_file" http://host:port/v1/transcribe
```

### python requests
```python
import requests

file_path = "/path/to/audio_file"
with open(file_path, 'rb') as f:
    file_name = file_path.split("/")[-1]
    files = {"file": (file_name, f)}
    response = requests.post("http://host:port/v1/transcribe", files=files)

print(response.json())
```
