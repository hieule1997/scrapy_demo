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

def scrape_company_data(session, view_id, query,industry_tag,location,range_value,csv_writer):
    page = 1
    not_exist_fields_arr = []
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
            "sort_ascending": "true",
            "sort_by_field" : "sanitized_organization_name_unanalyzed",
            "ui_finder_random_seed": "".join(
                random.choice(string.ascii_lowercase + string.digits) for _ in range(6)
            ),
            "cacheKey": int(time.time()),
        }

    if range_value != "":
        json_data["organization_num_employees_ranges"] = [range_value]
    else: 
        not_exist_fields_arr.append("organization_estimated_number_employees")
        json_data["not_exist_fields"] = not_exist_fields_arr
    
    if industry_tag!= "":
        json_data["organization_industry_tag_ids"] = [industry_tag]
    # else:
    #     not_exist_fields_arr.append("organization_industry_tag_ids")
    #     json_data["not_exist_fields"] = not_exist_fields_arr

    if location!= "":
        json_data["organization_locations"] = [location]
    # else:
    #     not_exist_fields_arr.append("organization_locations")
    #     json_data["not_exist_fields"] = not_exist_fields_arr

    print(json_data)
    
    resp = session.post("https://app.apollo.io/api/v1/mixed_companies/search", json=json_data)
    json_dict = resp.json()
    try:
        pagination_dict = json_dict.get("pagination")
        total_pages = pagination_dict.get("total_pages")
    except Exception as e:
        print(e)
        write_file("exception",json_dict)
        
    if total_pages == 1: 
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
            csv_writer.writerow(row)
    elif total_pages <=5:
        page += 1
        json_data["page"] = page
        for i in range(total_pages):
            resp = session.post(
                "https://app.apollo.io/api/v1/mixed_companies/search", json=json_data
            )
            print(resp.url)

            json_dict = resp.json()
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
    elif total_pages > 5:
        query = query[:-1]
        print("Query :",query)
        for i in string.ascii_lowercase:
            scrape_company_data(session, view_id, query+i+"_",industry_tag,location,range_value,csv_writer)

def scrape_people_data(session, view_id, query, output_csv_path):
    output_csv_path = "people.csv"
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

    out_f = open(output_csv_path, "a", encoding="utf-8")
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

def getCompanyId(session, view_id, query_name, output_csv_path):
    output_csv_path = "company_id.csv"
    out_f = open(output_csv_path, "a", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["id","company_name"],
        lineterminator="\n",
    )
    json_data = {
        "q_organization_fuzzy_name":query_name,
        "display_mode":"fuzzy_select_mode",

        "cacheKey": int(time.time()),
    }
    resp = session.post(
        "https://app.apollo.io//api/v1/organizations/search", json=json_data
    )
    print(resp.url)
    json_dict = resp.json()
    print(json_dict)
    for org_dict in json_dict.get("organizations", []):
        name = org_dict.get("name")
        id_company = org_dict.get("id")

        row = {
            "id": id_company,
            "company_name": name,
        }

        # pprint(row)
        csv_writer.writerow(row)
        # try:
        #     pagination_dict = json_dict.get("pagination")
        #     total_pages = pagination_dict.get("total_pages")
        # except Exception as e:
        #     print(e)
        #     write_file("exception",json_dict)
    # page += 1
    # json_data["page"] = page

    out_f.close()

def getCompanyData(session, view_id, query, output_csv_path):
    output_csv_path = "company.csv"
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

def getJobTitle(session, query):
    param = f'kind=person_title&q_tag_fuzzy_name={query}&display_mode=fuzzy_select_mode&per_page=2000&cacheKey={int(time.time())}'
    resp = session.get("https://app.apollo.io/api/v1/tags/search?"+param)
    
    json_dict = resp.json()
    print(json_dict)
    arr_dict = []
    for org_dict in json_dict.get("tags",[]):
        id = org_dict.get("id")
        cleaned_name = org_dict.get("cleaned_name")
        row = {
            "id": id,
            "cleaned_name": cleaned_name,
        }
        arr_dict.append(row)
    
    lenArr = len(json_dict.get("tags",[]))
    if lenArr >= 2000:
        for i in string.ascii_lowercase:
            getJobTitle(session, query+i)
    else:
        output_csv_path = "JobTitle.csv"
        out_f = open(output_csv_path, "a", encoding="utf-8")
        csv_writer = csv.DictWriter(
            out_f,
            fieldnames=["id", "cleaned_name"],
            lineterminator="\n",
        )
        csv_writer.writeheader()
        csv_writer.writerows(arr_dict)

def getLocation(session,query):
    output_csv_path = "Location.csv"
    param = f'kind=location&q_tag_fuzzy_name={query}&display_mode=fuzzy_select_mode&per_page=200&cacheKey={int(time.time())}'
    print(param)
    resp = session.get(
        "https://app.apollo.io/api/v1/tags/search?"+param)
    out_f = open(output_csv_path, "a", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["id", "cleaned_name"],
        lineterminator="\n",
    )
    csv_writer.writeheader()
    json_dict = resp.json()
    print(json_dict)
    for org_dict in json_dict.get("tags",[]):
        id = org_dict.get("id")
        cleaned_name = org_dict.get("cleaned_name")
        # print(value,count)
        row = {
            "id": id,
            "cleaned_name": cleaned_name,
        }
        csv_writer.writerow(row)

def getLinkinIndustryKeywords(session):
    output_csv_path = "LinkinIndustryKeywords.csv"
    out_f = open(output_csv_path, "a", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["id", "cleaned_name"],
        lineterminator="\n",
    )
    csv_writer.writeheader()
    param = f'kind=linkedin_industry&display_mode=fuzzy_select_mode&per_page=200&cacheKey={int(time.time())}'
    resp = session.get("https://app.apollo.io/api/v1/tags/search?"+param)
    json_dict = resp.json()
    print(json_dict)
    for org_dict in json_dict.get("tags",[]):
        id = org_dict.get("id")
        cleaned_name = org_dict.get("cleaned_name")
        # print(value,count)
        row = {
            "id": id,
            "cleaned_name": cleaned_name,
        }
        csv_writer.writerow(row)

def getEmployeeNumber(session,view_id,query_name,industry_tag,location,range_value):
    json_data = {}
    if range_value == "":
        json_data = {
            "finder_view_id": view_id,
            "page": 1,
            "q_organization_name": query_name,
            "display_mode": "explorer_mode",
            "open_factor_names": ["organization_num_employees_ranges"],
            "organization_industry_tag_ids":[industry_tag],
            "organization_locations": [location],
            "context": "companies-index-page",
            "cacheKey": int(time.time()),
        }
    else:
        json_data = {
            "finder_view_id": view_id,
            "page": 1,
            "q_organization_name": query_name,
            "display_mode": "explorer_mode",
            "open_factor_names": [],
            "organization_num_employees_ranges": [range_value],
            "organization_industry_tag_ids":[industry_tag],
            "organization_locations": [location],
            "context": "companies-index-page",
            "cacheKey": int(time.time()),
        }
    print(json_data)
    resp = session.post(
        "https://app.apollo.io/api/v1/mixed_companies/facets", json=json_data
    )
    print(resp.url)
    json_dict = resp.json()
    print(json_dict)
    for org_dict in json_dict["faceting"].get("num_employees_facets",[]):
        value = org_dict.get("value")
        count = org_dict.get("count")
        print(value,count)
        if count <=125 and count > 0:
            scrape_company_data(session,view_id,query_name,industry_tag,location,value)
        elif count > 125:
            min_range,max_range = range_value.split(",")
            if min_range + 1 == max_range:
                min = int(min_range)+2
                max = int(max_range)+2
                getEmployeeNumber(session,view_id,query_name+i,industry_tag,location,f"{min},{max}")    
            else:
                min = int(min_range)
                max = min + 1
                getEmployeeNumber(session,view_id,query_name,industry_tag,location,f"{min},{max}")

    
def main():
    username = "hieule1191997@gmail.com"
    password = "minhhieu1997"
    session, view_id = create_session(username, password)
    output_csv_path = "company.csv"
    out_f = open(output_csv_path, "a", encoding="utf-8")
    csv_writer = csv.DictWriter(
        out_f,
        fieldnames=["name", "linkedin_url", "website_url", "primary_domain", "phone"],
        lineterminator="\n",
    )
    csv_writer.writeheader()
    # getEmployeeNumber(session, view_id,"","5567ce1f7369643b78570000","Bloomington, Indiana","")
    scrape_company_data(session,view_id,"","","Bloomington, Indiana","",csv_writer)
    out_f.close()
    # getLocation(session,query)
    # for i in string.ascii_lowercase:
            # getJobTitle(session,i)
            # getEmployeeNumber(session, view_id,i)
            # scrape_company_data(session, view_id, i+j)
            # getLinkinIndustryKeywords(session, view_id, i+j)
    # getEmployeeNumber(session, view_id, query)


if __name__ == '__main__':
    main()