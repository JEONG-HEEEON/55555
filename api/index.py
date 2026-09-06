"""Vercel Python 서버리스 함수 진입점.

Vercel의 @vercel/python 런타임은 이 파일에서 `app` 변수를 찾아 ASGI 앱으로 실행한다.
backend/ 를 import 경로에 추가해 로컬/Render용 FastAPI 앱을 그대로 재사용한다.
(backend/ 가 함수 번들에 들어가도록 vercel.json 의 includeFiles 를 설정해 두었다.)
"""

import os
import sys

BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app  # noqa: E402  (sys.path 설정 후에 import 해야 함)

__all__ = ["app"]
