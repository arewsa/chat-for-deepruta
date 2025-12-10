from typing import Any, Optional, List, Dict
import httpx
from enum import Enum


class AddressType(str, Enum):
    STREET = "STREET"
    LOCATION = "LOCATION"


class GeocodingQuality(str, Enum):
    FAILED = "FAILED"
    CITY = "CITY"
    STREET = "STREET"
    LOCATION = "LOCATION"


class Coordinates:
    def __init__(self, lng: float, lat: float):
        self.lng = lng
        self.lat = lat


class GeocodedObject:
    def __init__(self, address: str, coordinates: Coordinates, quality: GeocodingQuality, feature: Dict[str, Any]):
        self.address = address
        self.coordinates = coordinates
        self.quality = quality
        self.feature = feature


class GeocoderClient:
    def __init__(self, base_url: str = "https://deepruta.ru/geocoder"):
        self.base_url = base_url
        self.timeout = 30.0
    
    async def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make HTTP request to geocoder API with error handling."""
        url = f"{self.base_url}{endpoint}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=data, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            except Exception:
                return None
    
    async def forward(self, 
                     address: str, 
                     address_type: AddressType,
                     normalize: bool = True,
                     use_cache: bool = True,
                     language: Optional[str] = None,
                     bounds: Optional[Dict[str, Any]] = None,
                     service_area: Optional[Dict[str, Any]] = None,
                     origin_address: Optional[str] = None,
                     origin_coordinates: Optional[Dict[str, float]] = None,
                     lanes_enabled: bool = True) -> Optional[List[GeocodedObject]]:
        """Forward geocoding: address -> coordinates."""
        data = {
            "address": address,
            "normalize": normalize,
            "use_cache": use_cache,
            "lanes_enabled": lanes_enabled
        }
        
        if language:
            data["language"] = language
        if address_type:
            data["address_type"] = address_type.value
        if bounds:
            data["bounds"] = bounds
        if service_area:
            data["service_area"] = service_area
        if origin_address:
            data["origin_address"] = origin_address
        if origin_coordinates:
            data["origin_coordinates"] = origin_coordinates
        
        response = await self._make_request("/api/v1/forward", data)
        print(f"Response: {response}, data: {data}")
        if not response or response.get("error") or not response.get("data"):
            return None
        
        results = []
        for item in response["data"]:
            coords = Coordinates(
                lng=item["coordinates"]["lng"],
                lat=item["coordinates"]["lat"]
            )
            quality = GeocodingQuality(item["quality"])
            obj = GeocodedObject(
                address=item["address"],
                coordinates=coords,
                quality=quality,
                feature=item["feature"]
            )
            results.append(obj)
        
        return results
    
    async def reverse(self,
                    longitude: float,
                    latitude: float,
                    language: Optional[str] = None,
                    address_type: Optional[AddressType] = None,
                    bounds: Optional[Dict[str, Any]] = None,
                    service_area: Optional[Dict[str, Any]] = None,
                    origin_address: Optional[str] = None,
                    use_cache: bool = True) -> Optional[List[GeocodedObject]]:
        """Reverse geocoding: coordinates -> address."""
        data = {
            "coordinates": {
                "lng": longitude,
                "lat": latitude
            },
            "use_cache": use_cache
        }
        
        if language:
            data["language"] = language
        if address_type:
            data["address_type"] = address_type.value
        if bounds:
            data["bounds"] = bounds
        if service_area:
            data["service_area"] = service_area
        if origin_address:
            data["origin_address"] = origin_address
        
        response = await self._make_request("/api/v1/reverse", data)
        if not response or response.get("error") or not response.get("data"):
            return None
        
        results = []
        for item in response["data"]:
            coords = Coordinates(
                lng=item["coordinates"]["lng"],
                lat=item["coordinates"]["lat"]
            )
            quality = GeocodingQuality(item["quality"])
            obj = GeocodedObject(
                address=item["address"],
                coordinates=coords,
                quality=quality,
                feature=item["feature"]
            )
            results.append(obj)
        
        return results
    
    async def suggest(self,
                     query: str,
                     limit: int = 10,
                     language: Optional[str] = None,
                     address_type: Optional[AddressType] = None,
                     bounds: Optional[Dict[str, Any]] = None,
                     service_area: Optional[Dict[str, Any]] = None,
                     origin_address: Optional[str] = None,
                     use_cache: bool = True) -> Optional[List[str]]:
        """Suggest addresses based on query."""
        data = {
            "query": query,
            "limit": limit,
            "use_cache": use_cache
        }
        
        if language:
            data["language"] = language
        if address_type:
            data["address_type"] = address_type.value
        if bounds:
            data["bounds"] = bounds
        if service_area:
            data["service_area"] = service_area
        if origin_address:
            data["origin_address"] = origin_address
        
        response = await self._make_request("/api/v1/suggest", data)
        if not response or response.get("error") or not response.get("data"):
            return None
        
        return response["data"]
    
    async def lookup(self,
                    address: str,
                    normalize: bool = True,
                    use_cache: bool = True,
                    language: Optional[str] = None,
                    address_type: Optional[AddressType] = None,
                    bounds: Optional[Dict[str, Any]] = None,
                    service_area: Optional[Dict[str, Any]] = None,
                    origin_address: Optional[str] = None,
                    origin_coordinates: Optional[Dict[str, float]] = None,
                    lanes_enabled: bool = True) -> Optional[List[GeocodedObject]]:
        """Lookup address."""
        data = {
            "address": address,
            "normalize": normalize,
            "use_cache": use_cache,
            "lanes_enabled": lanes_enabled
        }
        
        if language:
            data["language"] = language
        if address_type:
            data["address_type"] = address_type.value
        if bounds:
            data["bounds"] = bounds
        if service_area:
            data["service_area"] = service_area
        if origin_address:
            data["origin_address"] = origin_address
        if origin_coordinates:
            data["origin_coordinates"] = origin_coordinates
        
        response = await self._make_request("/api/v1/lookup", data)
        if not response or response.get("error") or not response.get("data"):
            return None
        
        results = []
        for item in response["data"]:
            coords = Coordinates(
                lng=item["coordinates"]["lng"],
                lat=item["coordinates"]["lat"]
            )
            quality = GeocodingQuality(item["quality"])
            obj = GeocodedObject(
                address=item["address"],
                coordinates=coords,
                quality=quality,
                feature=item["feature"]
            )
            results.append(obj)
        
        return results
