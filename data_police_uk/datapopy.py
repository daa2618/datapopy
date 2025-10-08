
import json, re, datetime, shapely, geopandas as gpd
from pathlib import Path
import sys
pardir = Path(__file__).resolve().parent
if str(pardir) not in sys.path:
    sys.path.insert(0, str(pardir))
from utils.response import Response
from utils.strings_and_lists import ListOperations
from utils.log_helper import BasicLogger

from typing import Optional,List,Union,Dict,Any

class NeighborhoodNotFound(Exception):
    pass

class DataPoliceUK:
    def __init__(self,**kwargs):
        self.base_url = "https://data.police.uk/api"
        self._forces = None
        self._logger = BasicLogger(log_directory=None, logger_name="DataPoliceUK", verbose=False)
        super().__init__(**kwargs)
    
    @property
    def ALL_AVAILABLE_DATASETS(self)->List[Dict[str,Any]]:
        """
        Return a list of available data sets.
        """
        return self.get_response(url=f"{self.base_url}/crimes-street-dates")
    
    def get_response(self, url, **kwargs):
        try:
            res= json.loads(Response(url=url, **kwargs).assert_response().content)
        except Exception as e:
            self._logger.error(f"Error retrieving data from {url}", str(e))
            return None
        if res:
            return res
        else:
            return None

    @property
    def LIST_OF_FORCES(self)->Optional[List[str]]:
        if self._forces is None:
            url=f"{self.base_url}/forces"
            self._forces=self.get_response(url)
        return self._forces
        
    @property
    def ALL_NAMES(self)->Optional[List[str]]:
        return [x.get("name") for x in self.LIST_OF_FORCES]
    @property
    def ALL_FORCE_IDS(self)->Optional[List[str]]:
        return [x.get("id") for x in self.LIST_OF_FORCES]
        
    def filter_for_force(self, force:str)->Optional[List[str]]:

        list_searcher = ListOperations(self.ALL_FORCE_IDS, search_string = force)
        #found_names=[x for x in self.ALL_NAMES if re.findall(force,x, re.IGNORECASE)]
        #matching_ids=[x.get("id") for x in self.LIST_OF_FORCES if x.get("name") in found_names]
        #if not found_names:
        #    found_ids = [x for x in self.ALL_FORCE_IDS if re.findall(force,x, re.IGNORECASE)]
        #    matching_ids=[x.get("id") for x in self.LIST_OF_FORCES if x.get("id") in found_ids]
        #if not found_names or not matching_ids:
        #    return None
        #else:
        #    return matching_ids
        return list_searcher.search_list_by_snowball()
    
    
    def find_force_for_neighborhood_coords(self, lat:Union[str,float], lng:Union[str,float]):
        """
        Find the neighbourhood policing team responsible for a particular area.
        params
        lat, lng : A Latitude & Longitude, e.g. 51.500617,-0.124629
        """
        url = f"{self.base_url}/locate-neighbourhood"
        params = {"q":f"{str(lat)},{str(lng)}"}
        return self.get_response(url=url,params=params)
    
    @property
    def DATE_LAST_UPDATED(self)->Optional[datetime.datetime]:
        """
        Crime data in the API is updated once a month. 
        Find out when it was last updated.
        """
        date = self.get_response(url=f"{self.base_url}/crime-last-updated").get("date")
        date = datetime.datetime.strftime(datetime.datetime.strptime(date, "%Y-%m-%d"),"%d %B %Y"
                                         )
        self._logger.info(f"The data were last updated on {date}")
        return date


class DataForForce(DataPoliceUK):
    def __init__(self, force_id, **kwargs):
        super().__init__(**kwargs)
        self.force_id = force_id
        self.force_url = f"{self.base_url}/forces"
        assert self.force_id in self.ALL_FORCE_IDS, "Force ID mismatch"
    
    def get_data_for_force(self)->Optional[List[Dict[str,Any]]]:
        url = f"{self.force_url}/{self.force_id}"
        return self.get_response(url)

    def get_all_senior_officers(self)->Optional[Any]:
        url = f"{self.force_url}/{self.force_id}/people"
        return self.get_response(url)

class CrimesData(DataPoliceUK):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._default_lat = 51.509865
        self._default_lng = -0.118092
        #self.force_id = force_id
    
    @property
    def ALL_CRIME_CATEGORIES(self):
        url = f"{self.base_url}/crime-categories"
        return self.get_response(url)
        
    @property
    def ALL_CRIME_NAMES(self)->Optional[List[str]]:
        return [x.get("name") for x in self.ALL_CRIME_CATEGORIES]
        
    @property
    def ALL_CRIME_IDS(self)->Optional[List[str]]:
        return [x.get("url") for x in self.ALL_CRIME_CATEGORIES]

    def filter_crime_id_for_name(self,crime:str)->Optional[List[str]]:
        found_crimes = ListOperations(self.ALL_CRIME_NAMES, search_string = crime).search_list_by_snowball()
        return [x.get("url") for x in self.ALL_CRIME_CATEGORIES if x.get("name") in found_crimes]
        
        
    #def get_crime_id_for_crime(self, crime:str)->Optional[List[str]]:
    #    found_names=[x for x in self.ALL_CRIME_NAMES if re.findall(crime,x, re.IGNORECASE)]
    #    matching_ids=[x.get("url") for x in self.ALL_CRIME_CATEGORIES if x.get("name") in found_names]
    #    if not found_names:
    #        found_ids = [x for x in self.ALL_CRIME_IDS if re.findall(crime,x, re.IGNORECASE)]
    #        matching_ids=[x.get("url") for x in self.ALL_CRIME_CATEGORIES if x.get("url") in found_ids]
    #    if not found_names or not matching_ids:
    #        return None
    #    else:
    #        return matching_ids
        
        
    def get_crime_url(self,crime_id:str)->str:
        return f"{self.base_url}/crimes-street/{crime_id}"
        
    def get_street_level_crimes_by_type(self, 
                                   crime_id:str,
                                   lat:Union[str,float]=None,
                                   lng:Union[str,float]=None,
                                   year:Union[str,int]=None,
                                   month:Union[str,int]=None,
                                  location_id:Union[str,int]=None,
                                  bounding_box:Union[List[str], List[float]]=None):
        """
        Crimes at street-level; 
        either within a 1 mile radius of a single point, or within a custom area.
        
        params
        crime_id : id for a crime
        
        'Specific point'
            lat :	Latitude of the requested crime area
            lng :	Longitude of the requested crime area
        'Custom area'
            poly : The lat/lng pairs which define the boundary of the custom area
            
        date : Optional. (YYYY-MM) Limit results to a specific month.
        The latest month will be shown by default
        """
        url = self.get_crime_url(crime_id)
        
        params = {}
        
        if location_id:
            params.update({
                
                "location_id":int(location_id)
            })
        elif bounding_box:
            params.update({
                
                "poly" : bounding_box
            })
        else:
            
            
            params.update({
            "lat":float(lat) if lat else self._default_lat,
            "lng":float(lng) if lng else self._default_lng,

        })
            
            
        if month and year:
            params.update({"date" : f"{year}-{month}"})
        self._logger.info(params)
        return self.get_response(url=url,
                               params=params)
        
    def get_all_street_level_crimes(self,
                                lat:Union[str,float]=None,
                                   lng:Union[str,float]=None,
                                   year:Union[str,int]=None,
                                   month:Union[str,int]=None,
                                  location_id:Union[str,int]=None,
                                  bounding_box:Union[List[str], List[float]]=None):
        """
        All Crimes at street-level; 
        either within a 1 mile radius of a single point, or within a custom area.
        'Specific point'
            lat :	Latitude of the requested crime area
            lng :	Longitude of the requested crime area
        'Custom area'
            poly : The lat/lng pairs which define the boundary of the custom area
            
        date : Optional. (YYYY-MM) Limit results to a specific month.
        The latest month will be shown by default
        """
        #url = f"{self.base_url}/crimes-street/all-crime"
        return self.get_street_level_crimes_by_type("all-crime",lat,lng,year,month,location_id,bounding_box)
    

    def get_street_level_outcomes(self,
                               lat:Union[str,float]=None,
                                lng:Union[str,float]=None,
                                year:Union[str,int]=None,
                                month:Union[str,int]=None,
                                location_id:Union[str,int]=None,
                                bounding_box:Union[List[str], List[float]]=None
                              ):
        """
        Outcomes at street-level; either at a specific location, within a 1 mile radius of a single point, or within a custom area.

        Note: Outcomes are not available for the Police Service of Northern Ireland.
        
        params
        Specific location ID
            Parameter	  Description
            date	      YYYY-MM
            location_id	  Crimes and outcomes are mapped to specific locations on the map. 
                          Valid IDs are returned by other methods which return location information.
        Latitude/longitude
            Parameter	  Description
            date	      YYYY-MM
            lat	          Latitude of the requested crime area
            lng	          Longitude of the requested crime area
        
        Custom area
            poly	The lat/lng pairs which define the boundary of the custom area
            date	Optional. (YYYY-MM) Limit results to a specific month.
            The latest month will be shown by default
        """
        params = {}
        
        if location_id:
            params.update({
                
                "location_id":int(location_id)
            })
        elif bounding_box:
            params.update({
                
                "poly" : bounding_box
            })
        else:
            
            params.update({
            "lat":float(lat) if lat else self._default_lat,
            "lng":float(lng) if lng else self._default_lng,

        })
            
        if month and year:
            params.update({"date" : f"{year}-{month}"})
        
        url = f"{self.base_url}/outcomes-at-location"
        return self.get_response(url=url,
                               params=params)

class Neighborhoods(DataPoliceUK):
    def __init__(self, force_id, **kwargs):
        super().__init__(**kwargs)
        self.force_id = force_id
        assert self.force_id in self.ALL_FORCE_IDS, "Force ID mismatch"
        self.force_url = f"{self.base_url}/{self.force_id}"
        self.neighborhoods = None

    
    @property
    def ALL_NEIGHBORHOOD_IDS_AND_NAMES(self):
        """
        List of neighbourhoods for a force
        """
        if self.neighborhoods is None:
            #self._logger.info(self.force_url)
            url =f"{self.force_url}/neighbourhoods"
            #self._logger.info(url)
            self.neighborhoods = self.get_response(url=url)
        return self.neighborhoods

    @property
    def ALL_NEIGHBORHOOD_NAMES(self)->Optional[List[str]]:
        return [x.get("name") for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES]
    @property
    def ALL_NEIGHBORHOOD_IDS(self)->Optional[List[str]]:
        return [x.get("id") for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES]
    
    def filter_neighborhood_id_for_name(self,neighborhood_name)->Optional[List[str]]:
        #neighborhoods=self.ALL_NEIGHBORHOOD_NAMES
        #assert neighborhood_name in neighborhoods, f"Neighborhood not found for force\nAvailable neighborhoods: {', '.join(neighborhoods)}"
        #return [x.get("id") for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES if x.get("name")==neighborhood_name][0]
        filtered_names = ListOperations(self.ALL_NEIGHBORHOOD_NAMES, search_string = neighborhood_name).search_list_by_snowball()
        if not filtered_names:
            return None
        return [x for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES if x.get("name") in filtered_names]

    #def get_neighborhood_id_for_force(self, neighborhood_name:str)->Optional[List[str]]:
        #found_names=[x for x in self.ALL_NEIGHBORHOOD_NAMES if re.findall(neighborhood_name,x, re.IGNORECASE)]
        #matching_ids=[x.get("id") for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES if x.get("name") in found_names]
        #if not found_names:
        #    found_ids = [x for x in self.ALL_NEIGHBORHOOD_IDS if re.findall(neighborhood_name,x, re.IGNORECASE)]
        #    matching_ids=[x.get("id") for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES if x.get("id") in found_ids]
        #if not found_names or not matching_ids:
        #    raise NeighborhoodNotFound(f"No matching neighborhood IDs was found\nSelect one from {self.ALL_NEIGHBORHOOD_NAMES}")
        #else:
        #    return matching_ids
        #return ListOperations()
    def assert_neighborhood_id(self, neighborhood_id:Union[str,int]):
        neighborhood_ids = self.ALL_NEIGHBORHOOD_IDS
        assert neighborhood_id in neighborhood_ids, f"Neighborhood ID not found for force\nAvailable IDs: {', ' .join(neighborhood_ids)}"
    #@property
    def get_neighborhood_url(self,neighborhood_id:Union[str,int])->Optional[str]:
        self.assert_neighborhood_id(neighborhood_id)
        return f"{self.base_url}/{self.force_id}/{neighborhood_id}"
    
    def get_specific_neighborhood_info(self, neighborhood_id:Union[str,int]):
        self.assert_neighborhood_id(neighborhood_id)
        url = self.get_neighborhood_url(neighborhood_id)
        return self.get_response(url=url)
    
    def get_neighborhood_boundary(self, neighborhood_id:Union[str,int]):
        self.assert_neighborhood_id(neighborhood_id)
        """
        A list of latitude/longitude pairs that make up the boundary of a neighbourhood.
        """
        url = f"{self.get_neighborhood_url(neighborhood_id)}/boundary"
        return self.get_response(url=url)
    
    
    def get_neighborhood_boundary_polygon(self, neighborhood_id:Union[str,int]):
        self.assert_neighborhood_id(neighborhood_id)
        return shapely.geometry.Polygon([[float(x.get("longitude")), float(x.get("latitude"))] for x in self.get_neighborhood_boundary(neighborhood_id)])
    
    @property
    def POLICE_FORCE_BOUNDARY(self)->Optional[gpd.GeoDataFrame]:
        dat = [
            {
                "location" : x.get("name"),
                "neighborhood_id" : x.get("id"),
                "geometry" : self.get_neighborhood_boundary_polygon(x.get("id"))
            } for x in self.ALL_NEIGHBORHOOD_IDS_AND_NAMES
        ]

        gdf=gpd.GeoDataFrame(dat).set_geometry("geometry").set_crs("EPSG:4326")
        return gdf
    
    def get_neighborhood_police_team(self, neighborhood_id:Union[str,int]):
        self.assert_neighborhood_id(neighborhood_id)
        return self.get_response(url=f"{self.get_neighborhood_url(neighborhood_id)}/people")
    
    def get_neighborhood_events(self, neighborhood_id):
        self.assert_neighborhood_id(neighborhood_id)
        events=self.get_response(url=f"{self.get_neighborhood_url(neighborhood_id)}/events")
        if not events:
            self._logger.info("No events were found")
        else:
            return events
        
    def get_neighborhood_priorities(self, neighborhood_id:Union[str,int]):
        self.assert_neighborhood_id(neighborhood_id)
        return self.get_response(url=f"{self.get_neighborhood_url(neighborhood_id)}/priorities")
    
class StopAndSearches(DataPoliceUK):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.lat = lat
        #self.lng = lng
        #self.month = month
        #self.year = year
        #self.bbox = bbox
        self.stop_search_url=f"{self.base_url}/stops-street"
    
    def params(self,
               lat:Union[str,float]=None,
                lng:Union[str,float]=None,
                year:Union[str,int]=None,
                month:Union[str,int]=None,
                location_id:Union[str,int]=None,
                bounding_box:Union[List[str], List[float]]=None)->Dict[str,Any]:
        params = {}
        
        if location_id:
            params.update({
                
                "location_id":int(location_id)
            })
        elif bounding_box:
            params.update({
                
                "poly" : bounding_box
            })
        else:
            
            params.update({
            "lat":float(lat) if lat else self._default_lat,
            "lng":float(lng) if lng else self._default_lng,

        })
        self._logger.info(params)
            
        if month and year:
            params.update({"date" : f"{year}-{month}"})
        
        return params
    
    def get_stop_searches_for_coords(self,
                                     lat:Union[str,float],
                                    lng:Union[str,float],
                                    year:Union[str,int]=None,
                                    month:Union[str,int]=None,):
        """
        Stop and searches at street-level; 
        either within a 1 mile radius of a single point, or within a custom area
        
        params
        lat : Latitude of the centre of the desired area
        lng : Longitude of the centre of the desired area
        date : Optional. (YYYY-MM) Limit results to a specific month.
                The latest month will be shown by default
        """
        params = self.params(lat,lng,year,month)
        return self.get_response(url=self.stop_search_url, params=params)
    
    def get_stop_searches_for_area(self,
                               bounding_box:Union[List[str], List[float]],
                               year:Union[str,int]=None,
                                month:Union[str,int]=None,
                                ):
        """
        Stop and searches at street-level; 
        either within a 1 mile radius of a single point, or within a custom area
        
        params
        bounding_box : The lat/lng pairs which define the boundary of the custom area
        date :       Optional. (YYYY-MM) Limit results to a specific month.
                     The latest month will be shown by default
        """
        params=self.params(bounding_box=bounding_box,month=month,year=year)
        return self.get_response(url=self.stop_search_url, params=params)
    
    def get_stop_searches_for_location(self, 
                                       location_id:Union[str,int],
                                       year:Union[str,int]=None,
                                        month:Union[str,int]=None,
                                        ):
        """
        Stop and searches at a particular location.
        
        location_id	 :   The ID of the location to get stop and searches for
        date	     :  Optional. (YYYY-MM) Limit results to a specific month.
                        The latest month will be shown by default.
        """
        params = self.params(location_id=location_id, month=month, year=year)
        return self.get_response(url=self.stop_search_url, params=params)
    
    def get_stop_searches_for_force(self, 
                                    force_id:Union[str,int],
                                    year:Union[str,int]=None,
                                    month:Union[str,int]=None,
                                    ):
        """
        Stop and searches that could not be mapped to a location.
        
        params
        force : The force that carried out the stop and searches
        date : Optional. (YYYY-MM) Limit results to a specific month.
        The latest month will be shown by default.
        """
        
        url = f"{self.base_url}/stops-no-location"
        params = dict(force=force_id)
        if month and year:
            params.update({"date":f"{year}-{month}"})
            
        
        #params = dict(force=force_id,date=f"{year}-{month}")
        return self.get_response(url=url, params=params)
    
    def get_stop_searches_reported_by_force(self,
                                            force_id:Union[str,int],
                                            year:Union[str,int]=None,
                                            month:Union[str,int]=None,):
        """
        Stop and searches reported by a particular force
        
        params
        force : The force ID of the force to get stop and searches for
        date :	Optional. (YYYY-MM) Limit results to a specific month.
        The latest month will be shown by default, even if no data is available for that force in that month; 
        use the availability API method to pick a date if this is significant for you
        
        """
        url = f"{self.base_url}/stops-force"
        params = dict(force=force_id)
        if month and year:
            params.update({"date":f"{year}-{month}"})
        return self.get_response(url=url, params=params)



