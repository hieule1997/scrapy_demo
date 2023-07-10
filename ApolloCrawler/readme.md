Scapy apollo web
get Job title  
url:
```
/api/v1/tags/search?q_tag_fuzzy_name=man&kind=person_title&display_mode=fuzzy_select_mode&cacheKey=1688959676223
```
param:
```
    q_tag_fuzzy_name: man
    kind: person_title
    display_mode: fuzzy_select_mode
    cacheKey: 1688959676223
```

kind : person_title

Get people search  
url:
```
https://app.apollo.io/api/v1/mixed_people/search
```
payload:  
```
{
    "finder_table_layout_id": null,
    "finder_view_id": "5b6dfc5a73f47568b2e5f11c",
    "page": 1,
    "person_titles": [
        "managing director"
    ],
    "person_department_or_subdepartments": [
        "product_ui_ux_design",
        "graphic_design"
    ],
    "person_seniorities": ["owner"],
    "display_mode": "explorer_mode",
    "per_page": 25,
    "open_factor_names": [],
    "num_fetch_result": 14,
    "context": "people-index-page",
    "show_suggestions": false,
    "ui_finder_random_seed": "x1z5wlf3q9",
    "cacheKey": 1688960594001
}
```
lưu ý :   
* Job titles:  
    + person_titles[] là `Titles`  
    + person_seniorities[] là `Management Level`   
    + person_department_or_subdepartments[] là `Department & Job Function` 
    + `exist_fields: ["person_title_normalized"]` là Job title is Known  
    + `not_exist_fields : ["person_title_normalized"]` là Job title is unknown
* Location:    
    + person_locations[] là `Location , select region , city/ state/contry/Zip`  
    + person_not_locations ["North America"] là `Location , select region , city/ state/contry/Zip exculde locations` loại trừ vị trí  
* Company:
    + is any of:
    `organization_ids: ["5f2a39cb77a7440112460cf5"]`
    + is not any of:
    `not_organization_ids: ["5fc93db64c38d300d6aa24e6"]`
    + include past company
    `person_past_organization_ids:["5fca408962ba9b00f6d3c961"]`
    + is known

    + is unknow

* Employees  
    + predefine Range :  
    organization_num_employees_ranges: ["21,50"] là `# Employees`
    + Custom Range :   
    organization_num_employees_ranges: ["1,50"] là `# Employees`
    + `not_exist_fields : ["organization_num_employees_ranges"]` là # of Employees is unknown
* Industry & Keywords  
    + Search Industries  
    `organization_industry_tag_ids []`  Tag id 
    + is not any of 
     `organization_not_industry_tag_ids: ["5567e0bf7369641d115f0200"]`
    + is known
    `exist_fields: ["organization_estimated_number_employees"]`
    + is unknown
    `not_exist_fields:["organization_estimated_number_employees"organization_linkedin_industry_tag_ids"]`
    + company keyword `q_organization_keyword_tags:["aws"]`
* Email Status: 
    + `contact_email_status :
["verified", "guessed", "user_managed", "new_data_available", "unavailable"]`  




Company
url:
```
/api/v1/organizations/search
```
payload:   
```
{
    "q_organization_fuzzy_name": "ab",
    "display_mode": "fuzzy_select_mode",
    "cacheKey": 1688980305668
}
```
Location:  
url :  
```
/api/v1/tags/search?q_tag_fuzzy_name=%C3%A1&exclude_categories%5B%5D=US%20State&kind=location&display_mode=fuzzy_select_mode&cacheKey=1688980440347
```
param
```
q_tag_fuzzy_name: á
exclude_categories[]: US State
kind: location
display_mode: fuzzy_select_mode
cacheKey: 1688980440347
```


Industry & Keywords :  
url :  
```
/api/v1/tags/search?q_tag_fuzzy_name=&kind=linkedin_industry&display_mode=fuzzy_select_mode&cacheKey=1688980514814
```
param
```
q_tag_fuzzy_name: 
kind: linkedin_industry
display_mode: fuzzy_select_mode
cacheKey: 1688980514814
```
