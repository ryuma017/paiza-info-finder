import json
import requests
from bs4 import BeautifulSoup


PAIZA_URL = 'https://paiza.jp'
LOGIN_URL = PAIZA_URL + '/user_sessions'
PROFILE_URL = PAIZA_URL + '/users/basic_profile/json'
EVAL_RESULTS_URL = PAIZA_URL + '/career/mypage/results'
RETRY_RESULTS_URL = PAIZA_URL + '/career/mypage/retry-results'

results_data = []
user_name = None
session = requests.session()


def scrape_eval_results():
    response = session.get(EVAL_RESULTS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    basicBoxes = soup.find_all(name='div', attrs={'class': 'basicBox'})

    for basicBox in basicBoxes:
        boxT = basicBox.find(name='div', attrs={'class': 'boxT'})

        if boxT is not None:
            title = boxT.find(name='span', attrs={'class': 'title'}).get_text(strip=True).split(':')
            if len(title) == 2:
                prob_num, prob_name = title[0], title[1]

            boxTR = boxT.find(name='span', attrs={'class': 'boxTR color_glay'}).get_text(strip=True).split('：')
            if len(boxTR) == 2:
                date = boxTR[1]

        boxM_inrTxt_span = basicBox.find(name='div', attrs={'class': 'boxM'}).div.find_all(name='span')

        if len(boxM_inrTxt_span) == 9:
            langage = boxM_inrTxt_span[2].get_text(strip=True)
            time = boxM_inrTxt_span[4].get_text(strip=True)
            score = boxM_inrTxt_span[8].get_text(strip=True)

        results_data.append(
            {
                "prob_num": prob_num,
                "prob_name": prob_name,
                "answer_time": time,
                "details": [
                    {
                        "date": date,
                        "langage": langage,
                        "score": score
                    }
                ]
            }
        )

def scrape_retry_results():
    response = session.get(RETRY_RESULTS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # view moreボタン押下処理
    viewmore_btn_exists = True
    while viewmore_btn_exists:
        basicBoxes = soup.find_all(name='div', attrs={'class': 'basicBox'})
        for basicBox in basicBoxes:
            boxT = basicBox.find(name='div', attrs={'class': 'boxT'})
            if boxT is not None:
                title = boxT.find(name='span', attrs={'class': 'title'}).get_text(strip=True).split(':')
                if len(title) == 2:
                    prob_num = title[0]

                boxTR = boxT.find(name='span', attrs={'class': 'boxTR color_glay'}).get_text(strip=True).split('：')
                if len(boxTR) == 2:
                    date = boxTR[1]

            boxM_inrTxt_span = basicBox.find(name='div', attrs={'class': 'boxM'}).div.find_all(name='span')
            if len(boxM_inrTxt_span) == 6:
                langage = boxM_inrTxt_span[1].get_text(strip=True)
                score = boxM_inrTxt_span[5].get_text(strip=True)

            # 一致するリザルトデータを探し、detailsに情報を追加
            for result in results_data:
                target_prob_num = result["prob_num"]
                if target_prob_num == prob_num:
                    result["details"].append(
                        {
                            "date": date,
                            "langage": langage,
                            "score": score,
                            "time": ""
                        }
                    )
                    break


        form = soup.find(name='form', attrs={'class': 'button_to'})
        if form is not None:
            post_url = PAIZA_URL + form.get('action')
            authenticity_token = form.find(attrs={'name': 'authenticity_token'}).get('value')
            form_data = {'authenticity_token': authenticity_token}
            post_response = session.post(post_url, data=form_data)

            formatted_retry_results_html = post_response.text.splitlines()[0]\
                .removeprefix('''$('#retry_results').append("''').removesuffix('");')\
                .replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n').replace('\\', '').replace(' /', '')

            formatted_view_more_html = post_response.text.splitlines()[1]\
                .removeprefix('''$("#view_more").html("''').removesuffix('");')\
                .replace("\\'", "'").replace('\\"', '"').replace('\\', '').replace(' /', '')

            soup = BeautifulSoup(formatted_retry_results_html+formatted_view_more_html, 'html.parser')

        else:
            viewmore_btn_exists = False

def set_login_data(email, password):
    response = session.get(PAIZA_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    authenticity_token = soup.find(attrs={'name': 'csrf-token'}).get('content')
    return {
        'email': email,
        'password': password,
        'authenticity_token': authenticity_token
    }

def login(email, password) -> bool:
    data = set_login_data(email, password)
    response = session.post(LOGIN_URL, data=data)

    if 'profile' in response.text:
        return True

    return False

def get_user_name():
    response = session.get(PROFILE_URL)
    profile_json = json.loads(response.text)
    user_name = f'{profile_json["name"]}（{profile_json["kana"]}）'
    return user_name

def get_results_data():
    scrape_eval_results()
    scrape_retry_results()
    return results_data
