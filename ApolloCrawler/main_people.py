import csv
from pprint import pprint
import time
import string
import random
import json
import requests


def create_session(username, password):
    session = requests.Session()

    session.headers = {
        "authority": "app.apollo.io",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36",
        "sec-ch-ua-platform": '"macOS"',
        "accept": "*/*",
        "origin": "https://app.apollo.io",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://app.apollo.io/",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    }

    json_data = {
        "email": username,
        "password": password,
        "timezone_offset": 0,
        "cacheKey": int(time.time()),
    }

    pprint(json_data)

    response = session.post("https://app.apollo.io/api/v1/auth/login", json=json_data)
    print(response.url)

    json_dict = response.json()

    view_id = (
        json_dict.get("bootstrapped_data", dict()).get("finder_views")[0].get("id")
    )

    return session, view_id

def write_file(file_name,text):
    path_file = file_name + ".txt"
    f = open(path_file, "a")
    f.write(json.dumps(text))
    f.write("\n")
    f.close()

def scrape_company_data(session, view_id, query, output_csv_path):
    page = 1

    json_data = {
        "finder_view_id": view_id,
        "q_organization_name": query,
        "page": page,
        "display_mode": "explorer_mode",
        "per_page": 25,
        "open_factor_names": [],
        "num_fetch_result": 1,
        "context": "companies-index-page",
        "show_suggestions": False,
        # Based on:
        # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
        "ui_finder_random_seed": "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        ),
        "cacheKey": int(time.time()),
    }

    out_f = open(output_csv_path, "w", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["name", "linkedin_url", "website_url", "primary_domain", "phone"],
        lineterminator="\n",
    )
    csv_writer.writeheader()

    for i in range(5):
        resp = session.post(
            "https://app.apollo.io/api/v1/mixed_companies/search", json=json_data
            # "https://app.apollo.io/api/v1/mixed_people/search", json=json_data
        )
        print(resp.url)

        json_dict = resp.json()
        print(json_dict)
        for org_dict in json_dict.get("organizations", []):
            name = org_dict.get("name")
            linkedin_url = org_dict.get("linkedin_url")
            website_url = org_dict.get("website_url")
            primary_domain = org_dict.get("primary_domain")
            phone = org_dict.get("phone")

            row = {
                "name": name,
                "linkedin_url": linkedin_url,
                "website_url": website_url,
                "primary_domain": primary_domain,
                "phone": phone,
            }

            # pprint(row)
            csv_writer.writerow(row)
        try:
            pagination_dict = json_dict.get("pagination")
            total_pages = pagination_dict.get("total_pages")
        except Exception as e:
            print(e)
            write_file("exception",json_dict)

        if total_pages == page:
            break

        page += 1
        json_data["page"] = page

    out_f.close()

def scrape_people_data(session, view_id, query, output_csv_path):
    page = 1

    json_data = {
        "finder_view_id": view_id,
        # "q_keywords": query,
        "q_person_name":"ac",
        "page": page,
        "display_mode": "explorer_mode",
        "per_page": 25,
        "open_factor_names": [],
        "num_fetch_result": 1,
        "context": "people-index-page",
        "show_suggestions": False,
        # Based on:
        # https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits
        "ui_finder_random_seed": "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
        ),
        "cacheKey": int(time.time()),
    }

    out_f = open(output_csv_path, "w", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["name","title","linkedin_url", "website_url","email_status","email", "phone"],
        lineterminator="\n",
    )
    csv_writer.writeheader()

    for i in range(5):
        resp = session.post(
            # "https://app.apollo.io/api/v1/mixed_companies/search", json=json_data
            "https://app.apollo.io/api/v1/mixed_people/search", json=json_data
        )
        print(resp.url)

        json_dict = resp.json()
        print(json_dict)
        for org_dict in json_dict.get("people", []):
            name = org_dict.get("name")
            title = org_dict.get("title")
            linkedin_url = org_dict.get("linkedin_url")
            website_url = org_dict.get("website_url")
            email_status = org_dict.get("email_status")
            email = org_dict.get("email")
            phone = org_dict.get("phone_numbers")

            row = {
                "name": name,
                "title": title,
                "linkedin_url": linkedin_url,
                "website_url": website_url,
                "email_status": email_status,
                "email": email,
                "phone": phone,
            }

            # pprint(row)
            csv_writer.writerow(row)
        try:
            pagination_dict = json_dict.get("pagination")
            total_pages = pagination_dict.get("total_pages")
        except Exception as e:
            print(e)
            write_file("exception",json_dict)

        if total_pages == page:
            break

        page += 1
        json_data["page"] = page

    out_f.close()

def main():
    username = "hieule1191997@gmail.com"
    password = "minhhieu1997"
    query = "add"
    output_csv_path = "aplo.csv"
    session, view_id = create_session(username, password)

    print(session.cookies)
    scrape_people_data(session, view_id, query, output_csv_path)


if __name__ == '__main__':
    main()