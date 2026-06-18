from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import io
import sys
import traceback
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


def execute_python(code: str):
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()

    try:
        exec(code)

        output = sys.stdout.getvalue()

        return {
            "success": True,
            "output": output
        }

    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }

    finally:
        sys.stdout = old_stdout


def extract_error_lines(traceback_text: str):
    matches = re.findall(
        r'File "<string>", line (\d+)',
        traceback_text
    )

    return [int(x) for x in matches]


@app.get("/")
async def root():
    return {"status": "running"}


@app.options("/code-interpreter")
async def options_code_interpreter():
    return Response(status_code=200)


@app.post("/code-interpreter")
async def code_interpreter(req: CodeRequest):

    result = execute_python(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    return {
        "error": extract_error_lines(
            result["output"]
        ),
        "result": result["output"]
    }
