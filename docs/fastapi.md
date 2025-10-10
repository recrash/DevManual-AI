FastAPI는 현대적이고, 빠르며(고성능), 파이썬 표준 타입 힌트에 기초한 Python의 API를 빌드하기 위한 웹 프레임워크입니다.

주요 특징으로:

- **빠름**: (Starlette과 Pydantic 덕분에) **NodeJS** 및 **Go**와 대등할 정도로 매우 높은 성능. [사용 가능한 가장 빠른 파이썬 프레임워크 중 하나](https://fastapi.tiangolo.com/ko/#_11).
- **빠른 코드 작성**: 약 200%에서 300%까지 기능 개발 속도 증가. *
- **적은 버그**: 사람(개발자)에 의한 에러 약 40% 감소. *
- **직관적**: 훌륭한 편집기 지원. 모든 곳에서 . 적은 디버깅 시간.
    
    자동완성
    
- **쉬움**: 쉽게 사용하고 배우도록 설계. 적은 문서 읽기 시간.
- **짧음**: 코드 중복 최소화. 각 매개변수 선언의 여러 기능. 적은 버그.
- **견고함**: 준비된 프로덕션 용 코드를 얻으십시오. 자동 대화형 문서와 함께.
- **표준 기반**: API에 대한 (완전히 호환되는) 개방형 표준 기반: [OpenAPI](https://github.com/OAI/OpenAPI-Specification) (이전에 Swagger로 알려졌던) 및 [JSON 스키마](http://json-schema.org/).

FastAPI는 거인들의 어깨 위에 서 있습니다:

- 웹 부분을 위한 [Starlette](https://www.starlette.io/).
- 데이터 부분을 위한 [Pydantic](https://docs.pydantic.dev/).

## 설치[¶](https://fastapi.tiangolo.com/ko/#_4)

`pip install fastapi████████████████████████████████████████ 100%restart ↻`

프로덕션을 위해 [Uvicorn](http://www.uvicorn.org/) 또는 [Hypercorn](https://github.com/pgjones/hypercorn)과 같은 ASGI 서버도 필요할 겁니다.

`pip install "uvicorn[standard]"████████████████████████████████████████ 100%restart ↻`

## 예제[¶](https://fastapi.tiangolo.com/ko/#_5)

### 만들기[¶](https://fastapi.tiangolo.com/ko/#_6)

- `main.py` 파일을 만드십시오:

`from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}`

- **또는 `async def` 사용하기...**
    
    여러분의 코드가 `async` / `await`을 사용한다면, `async def`를 사용하십시오.
    
    `from typing import Union
    
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    async def read_root():
        return {"Hello": "World"}
    
    @app.get("/items/{item_id}")
    async def read_item(item_id: int, q: Union[str, None] = None):
        return {"item_id": item_id, "q": q}`
    
    **Note**:
    
    잘 모르겠다면, [문서에서 `async`와 `await`](https://fastapi.tiangolo.com/async/#in-a-hurry)에 관한 *"급하세요?"* 섹션을 확인해 보십시오.
    

### 실행하기[¶](https://fastapi.tiangolo.com/ko/#_7)

서버를 실행하십시오:

`uvicorn main:app --reloadINFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)INFO:     Started reloader process [28720]INFO:     Started server process [28722]INFO:     Waiting for application startup.INFO:     Application startup complete.restart ↻`

- **`uvicorn main:app --reload` 명령에 관하여...**
    
    명령 `uvicorn main:app`은 다음을 나타냅니다:
    
    - `main`: `main.py` 파일 (파이썬 "모듈").
    - `app`: the object created inside of `main.py` with the line `app = FastAPI()`.
    - `-reload`: 코드가 변경된 후 서버 재시작하기. 개발환경에서만 사용하십시오.

### 확인하기[¶](https://fastapi.tiangolo.com/ko/#_8)

브라우저로 http://127.0.0.1:8000/items/5?q=somequery를 열어보십시오.

아래의 JSON 응답을 볼 수 있습니다:

`{"item_id": 5, "q": "somequery"}`

여러분은 벌써 API를 만들었습니다:

- *경로* `/` 및 `/items/{item_id}`에서 HTTP 요청 받기.
- 두 *경로* 모두 `GET` *연산*(HTTP *메소드* 로 알려진)을 받습니다.
- *경로* `/items/{item_id}`는 *경로 매개변수* `int`형 이어야 하는 `item_id`를 가지고 있습니다.
- *경로* `/items/{item_id}`는 선택적인 `str`형 이어야 하는 *경로 매개변수* `q`를 가지고 있습니다.

### 대화형 API 문서[¶](https://fastapi.tiangolo.com/ko/#api)

이제 http://127.0.0.1:8000/docs로 가보십시오.

자동 대화형 API 문서를 볼 수 있습니다 ([Swagger UI](https://github.com/swagger-api/swagger-ui) 제공):

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-01-swagger-ui-simple.png)

### 대안 API 문서[¶](https://fastapi.tiangolo.com/ko/#api_1)

그리고 이제 http://127.0.0.1:8000/redoc로 가봅시다.

다른 자동 문서를 볼 수 있습니다([ReDoc](https://github.com/Rebilly/ReDoc) 제공):

![ReDoc](https://fastapi.tiangolo.com/img/index/index-02-redoc-simple.png)

## 예제 심화[¶](https://fastapi.tiangolo.com/ko/#_9)

이제 `PUT` 요청에 있는 본문(Body)을 받기 위해 `main.py`를 수정해봅시다.

Pydantic을 이용해 파이썬 표준 타입으로 본문을 선언합니다.

`from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}`

서버가 자동으로 리로딩 할 수 있어야 합니다 (위에서 `uvicorn` 명령에 `--reload`을 추가 했기 때문입니다).

### 대화형 API 문서 업그레이드[¶](https://fastapi.tiangolo.com/ko/#api_2)

이제 http://127.0.0.1:8000/docs로 이동합니다.

- 대화형 API 문서가 새 본문과 함께 자동으로 업데이트 합니다:

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-02.png)

- "Try it out" 버튼을 클릭하면, 매개변수를 채울 수 있게 해주고 직접 API와 상호작용 할 수 있습니다:

![Swagger UI interaction](https://fastapi.tiangolo.com/img/index/index-04-swagger-03.png)

- 그러고 나서 "Execute" 버튼을 누르면, 사용자 인터페이스는 API와 통신하고 매개변수를 전송하며 그 결과를 가져와서 화면에 표시합니다:

![Swagger UI interaction](https://fastapi.tiangolo.com/img/index/index-05-swagger-04.png)

### 대안 API 문서 업그레이드[¶](https://fastapi.tiangolo.com/ko/#api_3)

그리고 이제, http://127.0.0.1:8000/redoc로 이동합니다.

- 대안 문서 역시 새 쿼리 매개변수와 본문을 반영합니다:

![ReDoc](https://fastapi.tiangolo.com/img/index/index-06-redoc-02.png)

### 요약[¶](https://fastapi.tiangolo.com/ko/#_10)

요약하면, 여러분은 매개변수의 타입, 본문 등을 함수 매개변수로서 **한번에** 선언했습니다.

여러분은 현대 표준 파이썬 타입으로 이를 행했습니다.

새로운 문법, 특정 라이브러리의 메소드나 클래스 등을 배울 필요가 없습니다.

그저 표준 **Python** 입니다.

예를 들어, `int`에 대해선:

`item_id: int`

또는 좀 더 복잡한 `Item` 모델에 대해선:

`item: Item`

...그리고 단 하나의 선언으로 여러분이 얻는 것은:

- 다음을 포함한 편집기 지원:
    - 자동완성.
    - 타입 검사.
- 데이터 검증:
    - 데이터가 유효하지 않을 때 자동으로 생성하는 명확한 에러.
    - 중첩된 JSON 객체에 대한 유효성 검사.
- 입력 데이터 : 네트워크에서 파이썬 데이터 및 타입으로 전송. 읽을 수 있는 것들:
    
    변환
    
    - JSON.
    - 경로 매개변수.
    - 쿼리 매개변수.
    - 쿠키.
    - 헤더.
    - 폼(Forms).
    - 파일.
- 출력 데이터 : 파이썬 데이터 및 타입을 네트워크 데이터로 전환(JSON 형식으로):
    
    변환
    
    - 파이썬 타입 변환 (`str`, `int`, `float`, `bool`, `list`, 등).
    - `datetime` 객체.
    - `UUID` 객체.
    - 데이터베이스 모델.
    - ...더 많은 것들.
- 대안가능한 사용자 인터페이스를 2개 포함한 자동 대화형 API 문서:
    - Swagger UI.
    - ReDoc.

---

이전 코드 예제로 돌아가서, **FastAPI**는 다음처럼 처리합니다:

- `GET` 및 `PUT` 요청에 `item_id`가 경로에 있는지 검증.
- `GET` 및 `PUT` 요청에 `item_id`가 `int` 타입인지 검증.
    - 그렇지 않다면 클라이언트는 유용하고 명확한 에러를 볼 수 있습니다.
- `GET` 요청에 `q`라는 선택적인 쿼리 매개변수가 검사(`http://127.0.0.1:8000/items/foo?q=somequery`처럼).
    - `q` 매개변수는 `= None`으로 선언되었기 때문에 선택사항입니다.
    - `None`이 없다면 필수사항입니다(`PUT`의 경우와 마찬가지로).
- `/items/{item_id}`으로의 `PUT` 요청은 본문을 JSON으로 읽음:
    - `name`을 필수 속성으로 갖고 `str` 형인지 검사.
    - `price`을 필수 속성으로 갖고 `float` 형인지 검사.
    - 만약 주어진다면, `is_offer`를 선택 속성으로 갖고 `bool` 형인지 검사.
    - 이 모든 것은 깊이 중첩된 JSON 객체에도 적용됩니다.
- JSON을 변환하거나 JSON으로 변환하는 것을 자동화.
- 다음에서 사용할 수 있는 모든 것을 OpenAPI로 문서화:
    - 대화형 문서 시스템.
    - 여러 언어들에 대한 자동 클라이언트 코드 생성 시스템.
- 2개의 대화형 문서 웹 인터페이스를 직접 제공.

---

우리는 그저 수박 겉 핥기만 했을 뿐인데 여러분은 벌써 어떻게 작동하는지 알고 있습니다.

다음 줄을 바꿔보십시오:

    `return {"item_name": item.name, "item_id": item_id}`

...에서:

        `... "item_name": item.name ...`

...으로:

        `... "item_price": item.price ...`

...그러고 나서 여러분의 편집기가 속성과 타입을 알고 자동 완성하는지 보십시오:

![editor support](https://fastapi.tiangolo.com/img/vscode-completion.png)

더 많은 기능을 포함한 보다 완전한 예제의 경우, [튜토리얼 - 사용자 가이드](https://fastapi.tiangolo.com/tutorial/)를 보십시오.

**스포일러 주의**: 튜토리얼 - 사용자 가이드는:

- 서로 다른 장소에서 **매개변수** 선언: **헤더**, **쿠키**, **폼 필드** 그리고 **파일**.
- `maximum_length` 또는 `regex`처럼 **유효성 제약**하는 방법.
- 강력하고 사용하기 쉬운 **의존성 주입** 시스템.
- **OAuth2** 지원을 포함한 **JWT tokens** 및 **HTTP Basic**을 갖는 보안과 인증.
- (Pydantic 덕분에) **깊은 중첩 JSON 모델**을 선언하는데 더 진보한 (하지만 마찬가지로 쉬운) 기술.
- (Starlette 덕분에) 많은 추가 기능:
    - **웹 소켓**
    - **GraphQL**
    - HTTPX 및 `pytest`에 기반한 극히 쉬운 테스트
    - **CORS**
    - **쿠키 세션**
    - ...기타 등등.

## 성능[¶](https://fastapi.tiangolo.com/ko/#_11)

독립된 TechEmpower 벤치마크에서 Uvicorn에서 작동하는 FastAPI 어플리케이션이 [사용 가능한 가장 빠른 프레임워크 중 하나](https://www.techempower.com/benchmarks/#section=test&runid=7464e520-0dc2-473d-bd34-dbdfd7e85911&hw=ph&test=query&l=zijzen-7)로 Starlette와 Uvicorn(FastAPI에서 내부적으로 사용)에만 밑돌고 있습니다. (*)

자세한 내용은 [벤치마크](https://fastapi.tiangolo.com/benchmarks/) 섹션을 보십시오.

## 선택가능한 의존성[¶](https://fastapi.tiangolo.com/ko/#_12)

Pydantic이 사용하는:

- [`email-validator`](https://github.com/JoshData/python-email-validator) - 이메일 유효성 검사.

Starlette이 사용하는:

- [`HTTPX`](https://www.python-httpx.org/) - `TestClient`를 사용하려면 필요.
- [`jinja2`](http://jinja.pocoo.org/) - 기본 템플릿 설정을 사용하려면 필요.
- [`python-multipart`](https://github.com/Kludex/python-multipart) - `request.form()`과 함께 의 지원을 원하면 필요.
    
    "parsing"
    
- [`itsdangerous`](https://pythonhosted.org/itsdangerous/) - `SessionMiddleware` 지원을 위해 필요.
- [`pyyaml`](https://pyyaml.org/wiki/PyYAMLDocumentation) - Starlette의 `SchemaGenerator` 지원을 위해 필요 (FastAPI와 쓸때는 필요 없을 것입니다).
- [`graphene`](https://graphene-python.org/) - `GraphQLApp` 지원을 위해 필요.

FastAPI / Starlette이 사용하는:

- [`uvicorn`](http://www.uvicorn.org/) - 애플리케이션을 로드하고 제공하는 서버.
- [`orjson`](https://github.com/ijl/orjson) - `ORJSONResponse`을 사용하려면 필요.
- [`ujson`](https://github.com/esnme/ultrajson) - `UJSONResponse`를 사용하려면 필요.

`pip install fastapi[all]`를 통해 이 모두를 설치 할 수 있습니다.