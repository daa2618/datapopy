
from utils.soup import Soup
import re, time
from utils.selenium_imports import Select, START, END, By, EC
from urllib.parse import urljoin
import pandas as pd, json
from utils.extract_zip_file import ExtractZipFile
from typing import Dict,Any,Optional,List,Set,Union
from selenium import webdriver
from pathlib import Path

class ForceNotFound(Exception):
    pass
class MoreThanOneForceFound(Exception):
    pass


class CustomDownload:
    def __init__(self):
        self._url = "https://data.police.uk"
        self._data_url = f"{self._url}/data"
        self._made_soup = None#Soup(self._data_url).make_soup()
        #print("Custom Download Crimes Data:\n\t",self._soup.find("div",{"id":"downloads"}).find("p").text)
    @property
    def _soup(self):
        if self._made_soup is None:
            self._made_soup = Soup(self._data_url).make_soup()
        return self._made_soup
    

    @property
    def DATE_OPTIONS(self)->Dict[str,Dict[str,Any]]:
        
        return {"from_dates":{
    x.attrs.get("value"):x.text for x in self._soup.find(name="select",attrs={"id":"id_date_from"}).find_all("option")
},
"to_dates":{
    x.attrs.get("value"):x.text for x in self._soup.find(name="select",attrs={"id":"id_date_to"}).find_all("option")
}}

    @property
    def FORCE_OPTIONS(self)->List[Dict[str,Any]]:
        return [{"force_name":re.sub("\n","",x.text).lstrip(" "),
 "force_id" : x.find("input").attrs.get("value"),
 "option_id" : x.find("input").attrs.get("id")} for x in self._soup.find("ul", {"id":"id_forces"}).find_all("li")]
    
    
    @property
    def START_DATE_OPTIONS(self)->List[Any]:
        return self.DATE_OPTIONS.get("from_dates").values()
    
    @property
    def END_DATE_OPTIONS(self)->List[Any]:
        return self.DATE_OPTIONS.get("to_dates").values()
    @property
    def START_MONTHS(self)->Set[str]:
        return set([re.findall("\w+[^ \d+]", x)[0] for x in list(self.START_DATE_OPTIONS)])
    @property
    def START_YEARS(self)->Set[str]:
        return set([re.findall("\d+", x)[0] for x in list(self.START_DATE_OPTIONS)])
    @property
    def END_MONTHS(self)->Set[str]:
        return set([re.findall("\w+[^ \d+]", x)[0] for x in list(self.END_DATE_OPTIONS)])
    @property
    def END_YEARS(self)->Set[str]:
        return set([re.findall("\d+", x)[0] for x in list(self.END_DATE_OPTIONS)])

    @property
    def FORCE_ID_OPTIONS(self)->List[str]:
        return [x.get("option_id") for x in self.FORCE_OPTIONS]
    
    
    def filter_forces_for_name(self, force:str)->Optional[List[str]]:
        force = re.sub(r"_|-|of |and | police| constabulary| service", "", force.lower().rstrip(" ").lstrip(" "))
        try:
            force = force.split(" ")
        except:
            force = [force]

        filtered=[x for x in self.FORCE_OPTIONS if any(re.match(z, y, re.IGNORECASE) for z in force for y in x.get("force_name").split(" "))]
        if filtered:
            if len(filtered) == 1:
                return filtered[0]
            else:
                print("More than one matching options were found for the force")
                print(f"Select force from {filtered}")
                return filtered
        else:
            raise ForceNotFound(f"No matched police forces were found\nChoose from {', '.join([x.get('force_name') for x in self.FORCE_OPTIONS])}")
            
    
    def get_option_id_for_force(self, force:str)->Optional[str]:
        #filtered = [x.get("option_id") for x in self.filter_forces_for_name(force)]
        #if len(filtered) == 1:
         #   return filtered[0]
        #else:
         #   print("More than one matching options were found for the force")
          #  print(f"Select force from {[x for x in self.FORCE_OPTIONS if x.get('option_id') in filtered]}")
           # return filtered
        try: 
            return self.filter_forces_for_name(force).get("option_id")
        except AttributeError as e:
            #raise e
            raise MoreThanOneForceFound("More than one force option Ids were found for given force")
    
    def get_download_url(self, 
                               start_month:Union[str,int], 
                               start_year:Union[str,int], 
                               end_month:Union[str,int], 
                               end_year:Union[str,int], 
                               force:str,
                              include_outcomes_data:bool=False,
                              include_stop_search_data:bool=False):
        force_option_id = self.get_option_id_for_force(force)
        assert isinstance(force_option_id, str), "More than one force option Ids were found for given force"
        start = f"{start_month} {start_year}"
        end = f"{end_month} {end_year}"
        assert start_month in self.START_MONTHS, f"Start Months should be in {self.START_MONTHS}"
        assert start_year in self.START_YEARS, f"Start Years should be in {self.START_YEARS}"
        assert end_month in self.END_MONTHS, f"End Months should be in {self.END_MONTHS}"
        assert end_year in self.END_YEARS,f"End Months should be in {self.END_YEARS}"
        assert start in self.START_DATE_OPTIONS, f"Start should be in {self.START_DATE_OPTIONS}"
        assert end in self.END_DATE_OPTIONS, f"End should be in {self.END_DATE_OPTIONS}"
        assert force_option_id in self.FORCE_ID_OPTIONS, f"Force option shoud be in {self.FORCE_ID_OPTIONS}"
        
        
        driver, wait = START(self._data_url, headless=True, user_agent=True, verbose=True)
        try:
            from_date_select = Select(driver.find_element(By.ID, "id_date_from"))
            from_date_select.select_by_visible_text(start)
            to_date_select = Select(driver.find_element(By.ID, "id_date_to"))
            to_date_select.select_by_visible_text(end)
            force=driver.find_element(By.CSS_SELECTOR, '#{}'.format(force_option_id))
            
            #print(force.get_attribute("value"))
            force.click()
            if include_outcomes_data:
                print("="*127)
                print("Including Outcomes Data....")
                driver.find_element(By.CSS_SELECTOR, '#id_include_outcomes').click()
                help_text=driver.find_element(By.CSS_SELECTOR, '#datasets > div:nth-child(3) > p'
                                            )
                print(help_text.text)
                print("Successfully selected outcomes data")
                print("="*127)
            if include_stop_search_data:
                print("="*127)
                print("Including Stop search Data....")
                driver.find_element(By.CSS_SELECTOR, '#id_include_stop_and_search').click()
                print("Successfully selected stop search data")
                print("="*127)
            generate_file_button=driver.find_element(By.XPATH, '//*[@id="downloads"]/form/button')
            #print(generate_file_button.text)
            generate_file_button.click()
            time.sleep(5)
            download_content_button = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/a')))
            return download_content_button.get_attribute("href")
        except Exception as e:
            print(e)
        finally:
            END(driver, verbose=True)
        
    
    def get_crimes_data_for_period(self, 
                                   
                                   start_month:Union[str,int], 
                               start_year:Union[str,int], 
                               end_month:Union[str,int], 
                               end_year:Union[str,int], 
                               force:str,
                              include_outcomes_data:bool=False,
                              include_stop_search_data:bool=False,
                                        data_folder:str="data"):
        download_url = {}
        while not download_url:
            download_url = self.get_download_url(start_month,
                                                           start_year,
                                                           end_month,
                                                           end_year,
                                                           force,
                                                           include_outcomes_data,
                                                           include_stop_search_data)
        try:
            force_id = self.filter_forces_for_name(force).get("force_id")
        except:
            raise MoreThanOneForceFound("More than one force IDs were matched")

        extract_to_folder = Path(f"{data_folder}/{force_id}")

        extract_to_folder.mkdir(exist_ok=True, parents=True)

        extract=ExtractZipFile(url=download_url,
                      extract_to_folder=extract_to_folder).extract_zip_file_to_folder
        return extract_to_folder.absolute()
    
class Boundaries(CustomDownload):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._boundaries_url = f"{self._data_url}/boundaries"
        self._boundaries_soup=Soup(self._boundaries_url).make_soup()
        print("Boundaries Data:\n\t",self._boundaries_soup.find("div",{"id":"downloads"}).find("p").text)
    
    @property
    def FORCE_BOUNDARIES_URL(self)->Optional[List[Dict[str,Any]]]:
        force_boundaries=[{x.find("a", href=True).text : urljoin(self._url, x.find("a", href=True).attrs.get("href"))} for x in self._boundaries_soup.find_all("div",{"class":"kmls force_kmls"})]
        return list(force_boundaries[0].values())[0]
    
    @property
    def NEIGHBORHOOD_BOUNDARIES_URLS(self)->Optional[Dict[str,Any]]:
        neighborhood_boundaries=[{y.text : urljoin(self._url, y.attrs.get("href")) for y in x.find_all("a", href=True)} for x in self._boundaries_soup.find_all("div",{"class":"neighbourhood_kmls"})]
        neighborhood_boundaries={key:value for x in neighborhood_boundaries for key, value in x.items()}
        return neighborhood_boundaries
    
    @property
    def LATEST_NEIGHBORHOOD_BOUNDARY_URLS(self):
        return self.NEIGHBORHOOD_BOUNDARIES_URLS[list(self.NEIGHBORHOOD_BOUNDARIES_URLS.keys())[0]]
    
class OpenData(CustomDownload):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._open_data_url = f"{self._data_url}/open-data"
        self._open_data_soup = Soup(self._open_data_url).make_soup()
        
        print("Open Data:\n\t",self._open_data_soup.find("div",{"id":"downloads"}).find("p").text)
    
    @property
    def OPEN_DATA_URLS(self)->Dict[str,Any]:
        return {x.text : x.attrs.get("href") for x in self._open_data_soup.find("div",{"id":"downloads"}).find_all("a",href=True)}

class StatisticalData(CustomDownload):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._stats_data_url = f"{self._data_url}/statistical-data"
        self._stats_data_soup = Soup(self._stats_data_url).make_soup()
        
        print("Statistical Data:\n\t",self._stats_data_soup.find("div",{"id":"downloads"}).find("p").text)
        
    @property
    def STATISTICAL_DATA_URLS(self)->Optional[List[Dict[str,Any]]]:
        df=pd.read_html(self._stats_data_url)[0]

        urls=[x.attrs.get("href") for x in self._stats_data_soup.find("div",{"id":"downloads"}).find_all("a", href=True)]

        df.insert(0,"url",urls)
        df.columns = [re.sub(" ", "_", x.lower()) for x in df.columns]
        return json.loads(df.to_json(orient="records"))
    
        
        
    
    
        
        
    
    


