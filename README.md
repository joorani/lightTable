# 프로젝트 소개
## 가벼운 식탁
다이어트 레시피 찾기 힘드셨죠?
쉽고 맛있는 건강레시피
가벼운 식탁과 함께하세요.


![가벼운식탁logo](https://user-images.githubusercontent.com/80900915/140594405-631a3712-421e-4549-92b6-feeb3aa0cea2.png)

http://light-table.shop/


##  1.제작 기간 & 팀원 소개
2021.11.01~ 2021.11.05


## 2. 시연 연상 
[![가벼운식탁](https://img.youtube.com/vi/96KFZ_nZlzk/0.jpg)](https://youtu.be/96KFZ_nZlzk)

## 3. 초안
![](https://images.velog.io/images/jurani/post/76616efb-4c35-429d-b21f-9c82d133ff66/lightTable.JPG)

## 4. 사용 기술

* Server: AWS EC2 (Ubuntu 18.04 LTS)
* Framework: Flask (Python)
* Database: MongoDB
* front-end : HTML5, CSS3, Javascript, jquery, bootstrap

## 5. 핵심 기능
* 로그인/회원가입
  - 아이디 중복확인 기능
  - 회원가입시 아이디, 비밀번호 유효성 검사
  
* 메인페이지
   * 카드출력 (필터)
     <br>키워드 클릭 시 카드출력
   * 상세페이지 이동
     <br>카드 클릭 시 해당 상세페이지 이동
   * 스크롤 top 버튼
     <br>누르면 페이지 상단으로 이동
     
* 상세페이지
    * 댓글기능
     <br>로그인한 사용자만 댓글 작성가능
     <br>클릭한 메뉴별 댓글 불러오기

## 6. trouble shooting
문제 : 웹 스크래핑한 db와 댓글을 저장하는 db가 달라 /detail page에 원하는 댓글을 불러오기 어려운 문제
해결 : detail page에 jinja2 템플릿을 사용해 불러온 데이터를 post를 이용해 댓글과 detail page정보를 함께보내 불러오기 해결
