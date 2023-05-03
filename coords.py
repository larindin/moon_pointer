import astropy.coordinates
import geopy.geocoders
import numpy as np

m_per_au = 149597870700

class Position():
    
    def __init__(self, label:str, time:astropy.time.Time):
        
        self.label = label
        self.time = time
        
    def get_xyz_coords(self) -> np.array:
        
        x = self.gcrs_coords[0] * np.cos(self.gcrs_coords[1]) * np.cos(self.gcrs_coords[2])
        y = self.gcrs_coords[0] * np.cos(self.gcrs_coords[1]) * np.sin(self.gcrs_coords[2])
        z = self.gcrs_coords[0] * np.sin(self.gcrs_coords[1])
        
        return np.array([x, y, z])
    
    def update_xyz_coords(self):
        
        self.xyz_coords = self.get_xyz_coords()
    
    def update(self, time:astropy.time.Time):
        self.time = time
        
        self.update_gcrs_coords()
        self.update_xyz_coords()
        
class CelestialPosition(Position):
    
    def __init__(self, label:str, time:astropy.time.Time, body:str):
        
        self.body = body
        super().__init__(label, time)
        
        self.update_gcrs_coords()
        super().update_xyz_coords()
      
    def get_gcrs_coords(self, time:astropy.time.Time) -> np.array:
        
        gcrs_coords = astropy.coordinates.get_body(body=self.body, time=time)  
        return np.array([gcrs_coords.distance.value, gcrs_coords.dec.rad, gcrs_coords.ra.rad])
    
    def update_gcrs_coords(self):
        
        self.gcrs_coords = self.get_gcrs_coords(self.time)


class TerrestrialPosition(Position):
    
    def __init__(self, label:str, time:astropy.time.Time, location_name:str):
        super().__init__(label, time)
        
        geoloc = geopy.geocoders.Nominatim(user_agent="GetLoc").geocode(location_name)
        self.loc = astropy.coordinates.EarthLocation.from_geodetic(geoloc.longitude, geoloc.latitude)
        
        self.update_gcrs_coords()
        super().update_xyz_coords()
        
    
    def get_gcrs_coords(self, time:astropy.time.Time) -> np.array:
        
        gcrs_coords = self.loc.get_gcrs(time)
    
        return np.array([gcrs_coords.distance.value / m_per_au, gcrs_coords.dec.rad, gcrs_coords.ra.rad])
    
    def update_gcrs_coords(self):
        
        self.gcrs_coords = self.get_gcrs_coords(self.time)
    
    def get_azimuth_0(self) -> np.array:
        '''
        Returns
        -------
        azimuth_0
            Vector pointing in the direction of azimuth = 0 (true north) from
            location on Earth represented by self.gcrs_coords
        '''
        
        x = -np.sin(self.gcrs_coords[1]) * np.cos(self.gcrs_coords[2])
        y = -np.sin(self.gcrs_coords[1]) * np.sin(self.gcrs_coords[2])
        z = np.cos(self.gcrs_coords[1])
        
        return np.array([x, y, z])
    
    def get_az_alt_rad(self, to_position:Position) -> tuple:
        
        # Creates and normalizes vector from observation to target
        view_vector = to_position.xyz_coords - self.xyz_coords
        view_vector = view_vector / np.linalg.norm(view_vector)
           
        # Gets vector pointing to azimuth = 0
        azimuth_0 = self.get_azimuth_0()
        
        # Projection of view vector onto plane tangent to Earth at observation point
        projection = (
            view_vector - 
            np.dot(self.xyz_coords, view_vector) / (np.linalg.norm(self.xyz_coords) ** 2) * self.xyz_coords
            )
        
        cross = np.cross(projection, azimuth_0)
        
        # Calculates the azimuth (0 to 360-)
        if np.dot(cross, self.xyz_coords) > 0:
            azimuth = np.arccos(np.dot(projection, azimuth_0) / (np.linalg.norm(projection) * np.linalg.norm(azimuth_0)))
        elif np.dot(cross, self.xyz_coords) < 0:
            azimuth = 2*np.pi - np.arccos(np.dot(projection, azimuth_0) / (np.linalg.norm(projection) * np.linalg.norm(azimuth_0)))
        elif np.dot(projection, azimuth_0) > 0:
            azimuth = 0
        elif np.dot(projection, azimuth_0) < 0:
            azimuth = np.pi
        
        # Normalizes vector normal to observational plane
        normal = self.xyz_coords / np.linalg.norm(self.xyz_coords)
        
        # Angle between view vector and normal vector (arcsin[x.y / (|x|*|y|)])
        altitude = np.arcsin(np.dot(normal, view_vector))
               
        return azimuth, altitude
    
    def get_az_alt(self, to_position:Position) -> tuple:
        
        azimuth, altitude = self.get_az_alt_rad(to_position)
        return np.degrees(azimuth), np.degrees(altitude)
    

