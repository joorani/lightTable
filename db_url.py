import requests
from bs4 import BeautifulSoup

# 재료 별 레시피 url을 통해 각 페이지의 레시피 게시물로 들어가는 통로를 만듦
def get_urls():
    # headers = 유저 정보를 넣어서 해당 사이트의 서버에게 봇으로 인식되어 크롤링이 차단되는 것을 제지함.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    # 데이터를 가져올 http를 requests의 API get을 이용해 가져온다.
    data = requests.get('https://www.10000recipe.com/recipe/list.html?q=&query=&cat1=&cat2=21&cat3=34&cat4=&fct=&order=reco&lastcate=cat3&dsearch=&copyshot=&scrap=&degree=&portion=&time=&niresource=', headers=headers)

    # data.text = requests의 text 속성을 통해 사이트의 html을 UTF-8로 인코딩된 문자열로 얻을 수 있다.
    # BeautifulSoup을 통해 해당 html 소스를 python 객체로 변환한다.
    # BeautifulSoup은 html 코드를 Python이 이해하는 객체 구조로 변환하는 Parsing을 한다.
    soup = BeautifulSoup(data.text, 'html.parser')

    # 레시피 게시판의 페이지의 url을 얻기 위해서 각 게시판의 html을 가져온다.
    lis = soup.select('#contents_area_full > ul > ul > li')

    # urls라는 빈 배열을 하나 만든다.
    urls = []

    for li in lis:
        # 반복문을 이용하여 게시판 태그 안에 해당 페이지 링크를 가리키는 a 태그 탐색한다.
        a = li.select_one('div.common_sp_thumb > a')
        if a is not None:
            # 사이트의 도메인과 위에서 가져온 a 태그의 href 속성을 이용하여 페이지 링크를 만든다.
            base_url = 'https://www.10000recipe.com/'
            url = base_url + a['href']
            # 만들어놨던 배열에 하나씩 넣는다.
            urls.append(url)
    return urls


# 크롤링(crawling)

# 크롤링이란 단어는 웹 크롤러(crawler)라는 단어에서 시작한 말이다.
# 크롤러란 조직적, 자동화된 방법으로 월드와이드 웹을 탐색하는 컴퓨터 프로그램이다.(출처: 위키백과)
# 크롤링은 크롤러가 하는 작업을 부르는 말로, 여러 인터넷 사이트의 페이지(문서, html 등)를 수집해서 분류하는 것이다.
# 대체로 찾아낸 데이터를 저장한 후 쉽게 찾을 수 있게 인덱싱한다.


# 파싱(parsing)

# 파싱이란 어떤 페이지(문서, html 등)에서 내가 원하는 데이터를 특정 패턴이나 순서로 추출하여 정보를 가공하는 것이다.
# 컴퓨터 과학적 정의를 보면 파싱이란 일련의 문자열을 의미있는 토큰(token)으로 분해하고
# 이들로 이루어진 파스 트리(parse tree)를 만드는 과정을 말한다.(출처: 위키백과)
# parsing은 일련의 문자열을 의미있는 token(어휘 분석의 단위) 으로 분해하고 그것들로 이루어진 Parse tree를 만드는 과정
# 문서의 내용을 *토큰(token)으로 분석하고, 문법적 의미와 구조를 반영한 *파스트리(parse tree)를 생성하는 과정
# 인터프리터나 컴파일러의 구성 요소 가운데 하나로, 입력 토큰에 내제된 자료 구조를 빌드하고 문법을 검사하는 역할을 한다.


# 스크래핑(scraping)

# 스크래핑이란 HTTP를 통해 웹 사이트의 내용을 긁어다 원하는 형태로 가공하는 것이다.
# 쉽게 말해 웹 사이트의 데이터를 수집하는 모든 작업을 뜻한다.
# 크롤링도 일종의 스크래핑 기술이라고 할 수 있다.