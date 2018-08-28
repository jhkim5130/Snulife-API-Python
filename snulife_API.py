import requests
from bs4 import BeautifulSoup as bs


def get_html(sess, url):
   _html = ""
   resp = sess.get(url)
   if resp.status_code == 200:
      _html = resp.text
   return _html

def parse_html(html):
    document_list = []
    soup = bs(html, 'html.parser')
    document_area = soup.find("table", {"id": "bd_lst"}).find_all("td", {"class":"title"})
    
    for document_index in document_area:
        info_soup = document_index("a")
        _url = info_soup["href"]
        _text = info_soup.text
        _num = _url.split('/')[-1]        			
        document_list.append((_num, _text, _url, ))
    
    return document_list

def login(sess, ID, PW):
    res = sess.post("https://snulife.com", data={
            'user_id' : ID,
            'password' : PW,
            'act' : 'procMemberLogin'       
            })
    
    if res.ok:
        return None
    else: print ("로그인 오류 발생")
    
def __search(sess, keyword, page, division = None):
    
    url = "https://snulife.com/index.php?mid=all&act=IS&where=document&search_target=title_content&is_keyword=%s&page=%s"% (keyword,page)
    if division:
        url += '&division=-%s'% division 
    
    res = sess.get(url)
    
    if not res.ok:
        print ("검색 오류 발생")
        return None
    elif 0 <= res.text.find("'계속 검색' 버튼을 선택하시면 아직 검색하지 않은 부분까지 계속 검색 하실 수 있습니다."):
        return 1
    elif 0 <= res.text.find("일치하는 검색 결과가 없습니다."):
        return 2

    soup = bs(get_html(sess, url), 'html.parser')
    lis = soup.find("ul", {"class": "searchResult"}).find_all("li")
    doc_headers = []
    for li in lis:
        a = li.find('a')
        recom_num = li.find("span", {"class", "recomNum"})
        doc_headers.append({"no": int(a["href"].split('/')[-1]), "title": a.text, "url": a["href"], 
               "recom_num": int(recom_num.text) if recom_num else 0})
    return doc_headers
     
def search(ID, PW, keyword, last_document_no = None, num = -1):
    with requests.session() as s:
        login(s, ID, PW)
        page = 1
        division = last_document_no
        last_doc_no = 99999999999
        while num != 0:
            result = __search(s, keyword, page, division)
            if result == None or result == 2:
                return
            elif result == 1:
                division = '-%s' % last_doc_no
            else:
                for doc_header in result:
                    if doc_header["no"] >= last_doc_no:
                        continue
                    last_doc_no = doc_header["no"]
                    yield doc_header
                    num -= 1
                    if num == 0: return
                page += 1

