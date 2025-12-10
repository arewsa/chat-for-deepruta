from typing import Dict, Any
from services.geocoder_client import GeocoderClient, AddressType

class GeminiMCPBridge:
    def __init__(self):
        self.geocoder = GeocoderClient()
    
    async def handle_function_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка вызова функции от Gemini."""
        try:
            if function_name == "forward_geocode":
                return await self._handle_forward_geocode(arguments)
            elif function_name == "reverse_geocode":
                return await self._handle_reverse_geocode(arguments)
            elif function_name == "suggest_addresses":
                return await self._handle_suggest_addresses(arguments)
            elif function_name == "lookup_address":
                return await self._handle_lookup_address(arguments)
            else:
                return {"error": f"Unknown function: {function_name}"}
        except Exception as e:
            return {"error": f"Function call failed: {str(e)}"}
    
    async def _handle_forward_geocode(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка forward geocoding."""
        address = args.get("address")
        address_type = args.get("address_type")
        language = args.get("language", "ru")
        normalize = args.get("normalize", True)
        
        if not address:
            return {"error": "Address is required"}

                
        
        results = await self.geocoder.forward(
            address=address,
            address_type=AddressType.LOCATION if address_type == "LOCATION" else AddressType.STREET,
            language=language,
            normalize=normalize
        )
        
        if not results:
            return {"error": f"Unable to geocode address: {address}"}
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "address": result.address,
                "coordinates": {
                    "longitude": result.coordinates.lng,
                    "latitude": result.coordinates.lat
                },
                "quality": result.quality.value
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    async def _handle_reverse_geocode(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка reverse geocoding."""
        longitude = args.get("longitude")
        latitude = args.get("latitude")
        language = args.get("language", "ru")
        
        if longitude is None or latitude is None:
            return {"error": "Longitude and latitude are required"}
        
        results = await self.geocoder.reverse(
            longitude=longitude,
            latitude=latitude,
            language=language
        )
        
        if not results:
            return {"error": f"Unable to reverse geocode coordinates: {longitude}, {latitude}"}
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "address": result.address,
                "coordinates": {
                    "longitude": result.coordinates.lng,
                    "latitude": result.coordinates.lat
                },
                "quality": result.quality.value
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results)
        }
    
    async def _handle_suggest_addresses(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка suggest addresses."""
        query = args.get("query")
        limit = args.get("limit", 10)
        
        if not query:
            return {"error": "Query is required"}
        
        results = await self.geocoder.suggest(
            query=query,
            limit=limit
        )
        
        if not results:
            return {"error": f"No suggestions found for query: {query}"}
        
        return {
            "success": True,
            "suggestions": results,
            "count": len(results)
        }
    
    async def _handle_lookup_address(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка lookup address."""
        address = args.get("address")
        normalize = args.get("normalize", True)
        language = args.get("language", "ru")
        
        if not address:
            return {"error": "Address is required"}
        
        results = await self.geocoder.lookup(
            address=address,
            normalize=normalize,
            language=language
        )
        
        if not results:
            return {"error": f"Unable to lookup address: {address}"}
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "address": result.address,
                "coordinates": {
                    "longitude": result.coordinates.lng,
                    "latitude": result.coordinates.lat
                },
                "quality": result.quality.value
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results)
        }