# MJ1

An image comparison judge that tells you which image is better.

## Setup

```bash
cd webapp
pip install -r requirements.txt
cd mj1-app && npm install && npm run build && cd ..
```

## Run

```bash
python mj1_proxy.py
```

Then go to http://localhost:8001

## Deploy

Use the `render.yaml` file for Render.com or host it wherever you want.

Need to set `TINKER_API_KEY` in your environment.