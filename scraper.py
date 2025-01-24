import re
import os
import time
import requests 
import pandas as pd
from bs4 import BeautifulSoup 
from google.cloud import storage

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcs-key.json"

leftover_ids =[]


#Personal Information
def personal_information(soup , Scientists_Data):
    def per_inf_ext(pattern):
        match = re.search(pattern, str(soup))
        if match:
            return match.group(1).strip()
            
    def get_per_info():

        name = r"<span class=\"col-sm-12\"><strong>\s*<h4>\s*<span>(.*?)</span>\s*</h4>\s*</strong></span>"
        DOB =  r"<span class=\"col-sm-5\"><i class=\"fa fa-calendar\"></i><span>(\d{4})</span></span>"
        gender = r"<span class=\"col-sm-3\"><i class=\"fa fa-user\"></i><span>(.*?)</span></span>"
        Home = r"<span class=\"col-sm-12\"><i class=\"fa fa-home\"></i><span>(.*?)</span></span>"
        work_place = r"<span class=\"col-sm-12\"><i class=\"fa fa-map-marker\"></i><span id=\"p_country\">(.*?)</span></span>"
        
        #updating dataset
        Scientists_Data["name"].append(per_inf_ext(name))
        Scientists_Data["DOB"].append(per_inf_ext(DOB))
        Scientists_Data["gender"].append(per_inf_ext(gender))
        Scientists_Data["Home"].append(per_inf_ext(Home))
        Scientists_Data["work_place"].append(per_inf_ext(work_place))
        
        return Scientists_Data #pd.DataFrame(Scientists_Data)
    get_per_info()
    
    #QUALIFICATIONS
def Qualifications(soup , Scientists_Data):
    def qual_data(year,qltn,inst):
        Scientists_Data["qual_yrs"].append(year if year else "0")
        Scientists_Data["Qualification"].append(qltn if qltn else "0")
        Scientists_Data["qual_inst"].append(inst if inst else "0")

    def qual_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                personal_section = soup.find('ul', id='qua-ul') 
                if personal_section :
                    year = [h.get_text(strip=True) for h in personal_section.find_all("time")] 
                    qltn = [h.get_text(strip=True) for h in personal_section.find_all( "h2")] 
                    inst = [h.get_text(strip=True) for h in personal_section.find_all("p")] 
                    qual_data(year,qltn ,inst)
                else:
                    qual_data( 0 , 0 , 0)
            else:
                qual_data( 0 , 0 , 0)
        except Exception as e:
            print("Exception occured ",e)

    qual_ext(soup)

    #Experience
def Experience_information(soup , Scientists_Data):
    def Exp_data_org(ex_yr , desig , exp_inst):
        Scientists_Data["Exp_yrs"].append(ex_yr if ex_yr else "0")
        Scientists_Data["Designation"].append(desig if desig else "0")
        Scientists_Data["Exp_inst"].append(exp_inst if exp_inst else "0")

    def extract_exp(soup):
        #print(soup)
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                experience = soup.find('div', id='list_panel_experience') 
                if experience:
                    ex_yr = [h.get_text(strip=True) for h in experience.find_all("span")] 
                    ex_yr = [item.replace('\n', ' ').replace('                                                        ', '').strip() for item in ex_yr]
                    desig =[h.get_text(strip=True) for h in experience.find_all( "h2")] 
                    exp_inst =[h.get_text(strip=True) for h in experience.find_all(["p"])] 
                    Exp_data_org(ex_yr , desig , exp_inst)
                else:
                    Exp_data_org(0 , 0 , 0)
            else:
                Exp_data_org(0 , 0 , 0)
        except Exception as e:
            print("Exception occured ",e)
        
    extract_exp(soup)

def Expertise_information(soup , Scientists_Data):
    def Expertise_data(domain , interest):
        Scientists_Data["domain"] = (domain if domain else "0")  #.append(domain if domain else "")
        Scientists_Data["interest"].append(interest if interest else "0")

    def Expertise_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                expertise_section = soup.find('div', id='expertise-view') 
                if expertise_section: 
                    domain = [h.get_text(strip=True) for h in expertise_section.find_all("span")]
                    interest = [h.get_text(strip=True) for h in expertise_section.find_all("h5")] 
                    Expertise_data(domain,interest)
                else:
                    Expertise_data( 0 , 0)
            else:
                Expertise_data( 0 , 0)
        except Exception as e:
            print("Exception occured ",e)

    Expertise_ext(soup)

def Present_information(soup , Scientists_Data ):
    def Present_data(pre_data):
        Scientists_Data["present_desig"].append(pre_data[1] if pre_data[1] else "0")
        Scientists_Data["present_inst"].append(pre_data[2] if pre_data[2] else "0")

    def Present_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                present_section = soup.find('div', class_='name-location') 
                if present_section:
                    pre_data = [h.get_text(strip=True) for h in present_section.find_all("span")]
                    Present_data(pre_data)
                else:
                    Present_data([0,0,0])
            else:
                Present_data([0,0,0])
        except Exception as e:
            print("Exception occured ",e)

    Present_ext(soup)

def Stats_information(soup , Scientists_Data):
    def Stats_data(data):
        stats_list = ["Articles" , "Conferences", "Books" , "Projects", "Awards"]
        for i in range(0,len(data),2):
            Scientists_Data[data[i+1]].append(data[i])
            
        for k in stats_list:
            if Scientists_Data[k] == []:
                Scientists_Data[k].append("0")

    def Stats_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                stats_section = soup.find('div', class_='service-block-v3 service-block-blue') 
                if stats_section:
                    data = [h.get_text(strip=True) for h in stats_section.find_all("span") ]
                    Stats_data(data)
                else:
                    Stats_data([])
            else:
                Stats_data([]) 
        except Exception as e:
            print("Exception occured ",e)

    Stats_ext(soup)

#HONOURS AND AWARDS
def Honour_Awards(soup , Scientists_Data ):
    def awards_data(awardyr , awd , awdin):
        Scientists_Data["award_yrs"].append(awardyr if awardyr else "0")
        Scientists_Data["Award"].append(awd if awd else "0")
        Scientists_Data["award_inst"].append(awdin if awdin else "0")

    def awards_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                awards_section =  soup.find('div', id='awards-form-view')
                if awards_section: 
                    awardyr = [h.get_text(strip=True) for h in awards_section.find_all("span")]          #year
                    awd = [h.get_text(strip=True) for h in awards_section.find_all("h3")]    #award
                    awdin = [h.get_text(strip=True) for h in awards_section.find_all("p")]  #institute
                    awards_data(awardyr , awd , awdin)
                else:
                    awards_data( 0 , 0 , 0)
            else:
                awards_data( 0 , 0 , 0)
        except Exception as e:
            print("Exception occured ",e)


    awards_ext(soup)

# Membership in Prof Bodies
def Membership_prof(soup , Scientists_Data):
    def mpb_data(prb , prval):
        Scientists_Data["Professional Bodies"].append(prb if prb else "0")
        Scientists_Data["prof_validity"].append(prval if prval else "0")

    def memb_prof(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                memb_pro =  soup.find('div', id='pb-form-view')
                if memb_pro: 
                    prb= [h.get_text(strip=True) for h in memb_pro.find_all("h3")] 
                    prval = [h.get_text(strip=True) for h in memb_pro.find_all("p")]
                    mpb_data(prb , prval)
                else:
                    mpb_data(0,0)
            else:
                mpb_data(0,0)
        except Exception as e:
            print("Exception occured ",e)

    memb_prof(soup)

#Membership of committees
def Membership_comm(soup , Scientists_Data):
    def mcom_data(m_yr , comm , m_val):
        Scientists_Data["mc_year"].append(m_yr if m_yr else "0")
        Scientists_Data["committees"].append(comm if comm else "0")
        Scientists_Data["mc_validity"].append(m_val if m_val else "0")


    def memb_com(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                committ =  soup.find('div', id='mc-form-view')
                if committ: 
                    m_yr = [h.get_text(strip=True) for h in committ.find_all("span")] 
                    comm = [h.get_text(strip=True) for h in committ.find_all("h3")] 
                    m_val = [h.get_text(strip=True) for h in committ.find_all("p")] 
                    mcom_data(m_yr , comm , m_val)
                else:
                    mcom_data(0,0,0)
            else:
                mcom_data(0,0,0)
        except Exception as e:
            print("Exception occured ",e)

    memb_com(soup)

# RESEARCH PROJECTS

def Research_projects(soup , Scientists_Data ):
    def research_data(re_title , agency):
        Scientists_Data["research_title"].append(re_title if re_title else "0")
        Scientists_Data["Funding_Agency"].append(agency if agency else "0")

    def research_ext(soup):
        try:
            if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                committ =  soup.find('div', id='rp-form-view')
                committ1 =  soup.find('div', id='list-rp')
                if committ: 
                    re_title = [h.get_text(strip=True) for h in committ.find_all("h2")] + ([h.get_text(strip=True) for h in committ1.find_all("h2")]) 
                    agency = [h.get_text(strip=True) for h in committ.find_all("b")] + ([h.get_text(strip=True) for h in committ1.find_all("h2")]) 
                    research_data(re_title , agency)
                else:
                    research_data( 0 , 0)
            else:
                    research_data( 0 , 0)
        except Exception as e:
            print("Exception occured ",e)
    
    research_ext(soup)

import ast

def remove_spl_chars(data):
    l =[]
    if data and data not in [ [""], "0" , 0, None]:
        for i in data:
            s = i.replace("&","and")
            s = s.replace("–","-")
            l.append(s)
        return l
           

def converter(obj):
    L=[]
    if obj and obj not in [ [""], "0" , 0, None]:
        for i in ast.literal_eval(obj):
            L.append(i.strip())
        return L

def clean_and_sort_education(education):
    l =[]
    if education and education not in [ [""], "0" , 0, None]:
        for i in education:
            if (i[0]) =="P":
                return i
            
        for i in education:
            if (i[0]) =="M":
                return i
            
        for i in education:
            if (i[0]) =="P":
                return i

def main(soup, eid):
    Scientists_Data = { "name" :[] , "DOB" :[], "gender":[] ,  "Home":[],"work_place":[],
                        "Exp_yrs" :[] , "Designation" :[], "Exp_inst":[] ,
                       "qual_yrs" :[] , "Qualification" :[], "qual_inst":[],
                       "award_yrs" :[] , "Award" :[], "award_inst":[] ,
                       "Professional Bodies" :[] , "prof_validity" :[],
                       "mc_year" :[],"committees" :[] , "mc_validity" :[] ,
                       "research_title" :[],"Funding_Agency" :[],
                       "domain" :[] ,  "interest":[],
                       "present_desig" :[] , "present_inst":[],
                       "Articles" :[] , "Conferences" :[], "Books":[] , "Projects" :[], "Awards":[] , "ExpertID": []
                      }
    if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
        Scientists_Data['ExpertID'] = eid
        personal_information(soup , Scientists_Data)
        Experience_information(soup , Scientists_Data)
        Qualifications(soup , Scientists_Data)
        Honour_Awards(soup , Scientists_Data )
        Membership_prof(soup , Scientists_Data)
        Membership_comm(soup , Scientists_Data)
        Research_projects(soup , Scientists_Data )
        Expertise_information(soup , Scientists_Data)
        Present_information(soup , Scientists_Data)
        Stats_information(soup , Scientists_Data)
        
        #print(Scientists_Data)
        return pd.DataFrame(Scientists_Data)
    return None


MAX_RETRIES = 3
RETRY_DELAY = 10  # seconds

def get_response(pid):
    url = "https://vidwan.inflibnet.ac.in/profile/" + str(pid)
    retries = 0

    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, timeout=60)  # 1-minute timeout
            if response.status_code == 200:
                soup = response.text
                if "This Profile is not activated by the VIDWAN Administrator" not in str(soup) and soup:
                    return BeautifulSoup(soup, "html.parser")
                else:
                    if pid not in leftover_ids:
                        leftover_ids.append(pid)
                    return 0
            else:
                raise Exception(f"Profile not accessible. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Failed to scrape {url} on attempt {retries + 1}: {e}")
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)  # Wait before retrying
            else:
                print(f"All retry attempts failed for {url}.")
                return 0    
    
        
def data_cleaning(Main_dataset):
    Main_dataset['name'] = Main_dataset['name'].str.replace(r'\b(Dr|Dr\.|Mr|Mr\.Ms|Mrs\.|Prof|prof\.|Smt|smt)\b\.?', '', regex=True).str.strip()
    Main_dataset['name'] = Main_dataset['name'].str.replace(r'\b(\w)\s+(\w)\b', r'\1.\2.', regex=True)
    Main_dataset['name'] = Main_dataset['name'].str.replace(r'\.(\s+)', r'.', regex=True)
    Main_dataset['name'] = Main_dataset['name'].str.replace(r'\b([A-Z])\s+', r'\1.', regex=True)
    return Main_dataset

        
def generate_data(leftover_ids, Main_dataset):
    for i in leftover_ids:
        #print(i , end = " ")
        ext_info = get_response(i)
        if ext_info != 0 and "This Profile is not activated by the VIDWAN Administrator" not in str(ext_info) and ext_info:  
            df = main(ext_info , i)
            Main_dataset = pd.concat([Main_dataset, df], ignore_index=True)
    
    Main_dataset = data_cleaning(Main_dataset)
    return Main_dataset

def upload_to_gcs(bucket_name, output_file, Main_dataset):
    client = storage.Client()
    vidwan_bucket = client.get_bucket(bucket_name)
    vidwan_bucket.blob(output_file).upload_from_string(Main_dataset.to_csv(),'text/csv')

    print(f"File {output_file} uploaded.")
  
   

if __name__ == "__main__":
    start = 1
    end =  250335
    Main_dataset =[]
    flag = False

    for i in range(start,end):
        print(i , end = " ")
        ext_info = get_response(i)
        if ext_info != 0 and ext_info:
            df = main(ext_info , i)
            if df is not None:
                if flag: 
                    Main_dataset = pd.concat([Main_dataset, df], ignore_index=True)
                else:
                    Main_dataset = pd.DataFrame(df)
                    flag = True

    Main_dataset = data_cleaning(Main_dataset)

    print("retrying failed IDs")
    Main_dataset = generate_data(leftover_ids, Main_dataset)

    bucket_name = "vidwan-data-bucket"
    output_file = "Dataset"+str(start)+"-"+str(end)+".csv"
    #Main_dataset.to_excel("../vidwan_data.xlsx",index=False)
    upload_to_gcs(bucket_name, output_file,Main_dataset )

    print("file saved at : ",output_file)


#print(DATA.head())
