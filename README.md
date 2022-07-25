# Content Tech Solution Youtube Video HL

python으로 youtube video download하고 테스트 해보기 위한 프로젝트 입니다.

## Getting Started

---

기존에 crawling 모듈로 제작한 most replayed를 기반으로 제작하였습니다.
pytube, open cv를 이용하여, most replayed 구간만 추출하는 기능을 추가 하였습니다.

### Prerequisites

-   Python 3.9.10 이상

    ```
    python3 -m venv .venv
    ```

    ```
    pip install -r requirement.txt
    ```

## How to Running

---

### download and most replayed 추출

```bash
python main.py --out=./downloads  --type=k --progress --vid=GrAYU37dJ8s
```

-   type: k -> download, most replay 추출, most replay 구간 추출을 순서대로 진행
-   vid: youtube video id
-   progress: 프로그래스바 표기
-   out: 결과 동영상을 저장할 폴더
    **저장결과는 out 폴더에 {vid}.mp4, {vid}\_HL.mp4로 저장 된다**

### download

```bash
python main.py --out=./downloads --vid="GnrU_i1qTgU" --type=d --progress
```

-   type: d -> download
-   vid: youtube video id
-   progress: 프로그래스바 표기
-   out: 결과 동영상을 저장할 폴더

### video 구간 추출

```bash
python main.py --out=./downloads --outfile="test2.mp4"  --file=./downloads/GnrU_i1qTgU.mp4 --type=c --progress --start=15 --end=300
```

-   type: c -> video extract
-   file: 추출할 동영상 파일의 위치
-   outfile: 결과파일의 위치
-   progress: 프로그래스바 표기
-   out: 결과 동영상을 저장할 폴더
-   start: 추출 시작할 시간(second)
    -   start=15, end=60 이고 GnrU_i1qTgU.mp4 이 2분자리 동영상이면
    -   GnrU_i1qTgU.mp4 15초 부터 60초까지 부분만 짤라 동영상으로 저장 한다.
-   end: 추출을 끝낼 시간(second)

### video upload Google Storage

```bash
python main.py --out=./downloads  --type=s --gs --progress --vid=GrAYU37dJ8s --frame
```

## Running the tests

## License

---

This project is licensed under sandbox network content data solution team
