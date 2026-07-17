import json
import logging
from typing import Any, Dict, List, Optional
from groq import Groq

# Import all service functions
from app.services.airport_service import lookup_airport, get_airport_terminal, find_nearest_airport
from app.services.baggage_service import get_baggage_allowance, calculate_excess_baggage_fee, get_special_baggage_guidance, purchase_extra_baggage
from app.services.booking_service import lookup_booking, cancel_booking, select_seat, select_meal, request_upgrade
from app.services.flight_service import search_flights, get_flight_status, get_flight_schedule, get_route_information
from app.services.weather_service import get_destination_weather, get_travel_advisory

logger = logging.getLogger(__name__)

# List of tool definitions for the Groq client
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_airport",
            "description": "Find an airport by IATA code, city, or part of its name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Airport code (e.g. DEL), city name (e.g. Delhi), or part of airport name."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_airport_terminal",
            "description": "Return mock terminal and check-in counter guidance for an airline at a specific airport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {"type": "string", "description": "The 3-letter IATA code of the airport (e.g. DEL, BOM)."},
                    "airline_code": {"type": "string", "description": "The 2-letter airline code. Defaults to 'AR'.", "default": "AR"}
                },
                "required": ["airport_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_nearest_airport",
            "description": "Find the closest listed airport to geographic coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number", "description": "Latitude coordinate in degrees."},
                    "longitude": {"type": "number", "description": "Longitude coordinate in degrees."}
                },
                "required": ["latitude", "longitude"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_baggage_allowance",
            "description": "Return checked and cabin baggage entitlement for a specific cabin class and route.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cabin_class": {"type": "string", "description": "Cabin class (economy, premium_economy, business, first)."},
                    "route_type": {"type": "string", "description": "Route type: domestic, regional, or international. Defaults to international.", "default": "international"},
                    "is_infant": {"type": "boolean", "description": "True if the traveler is an infant. Defaults to False.", "default": False}
                },
                "required": ["cabin_class"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_excess_baggage_fee",
            "description": "Quote excess charges for baggage based on bag count and total weight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cabin_class": {"type": "string", "description": "Cabin class (economy, premium_economy, business, first)."},
                    "route_type": {"type": "string", "description": "Route type: domestic, regional, or international."},
                    "bags": {"type": "integer", "description": "Number of checked bags."},
                    "total_weight_kg": {"type": "number", "description": "Total combined weight of checked bags in kilograms."}
                },
                "required": ["cabin_class", "route_type", "bags", "total_weight_kg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_special_baggage_guidance",
            "description": "Return handling and acceptance guidance for special items (e.g. sports equipment, musical instrument, oversized baggage, wheelchair, dangerous goods, pet).",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_type": {"type": "string", "description": "Type of item (sports equipment, musical instrument, oversized baggage, wheelchair, dangerous goods, pet)."},
                    "weight_kg": {"type": "number", "description": "Optional weight of the item in kg.", "default": 0}
                },
                "required": ["item_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "purchase_extra_baggage",
            "description": "Create a mock pre-purchase quote for additional checked baggage weight.",
            "parameters": {
                "type": "object",
                "properties": {
                    "route_type": {"type": "string", "description": "Route type: domestic, regional, or international."},
                    "additional_weight_kg": {"type": "number", "description": "Additional weight to purchase in kg."}
                },
                "required": ["route_type", "additional_weight_kg"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_booking",
            "description": "Look up booking details like flight number, cabin, passenger list, seats, and meal choices by PNR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string", "description": "The 6-character unique booking reference code (e.g. Q7M4KP, L9R2TX)."},
                    "last_name": {"type": "string", "description": "Optional lead passenger surname to validate."}
                },
                "required": ["pnr"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking",
            "description": "Validate and process a cancellation request for a booking by PNR reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string", "description": "The 6-character booking reference code."},
                    "reason": {"type": "string", "description": "Optional reason for cancellation."}
                },
                "required": ["pnr"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "select_seat",
            "description": "Validate seat selection and return any fee information for a passenger index on a booking PNR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string", "description": "The 6-character booking reference code."},
                    "passenger_index": {"type": "integer", "description": "0-based passenger index within the booking list."},
                    "seat": {"type": "string", "description": "Requested seat number (e.g. 14A, 3K)."}
                },
                "required": ["pnr", "passenger_index", "seat"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "select_meal",
            "description": "Validate and select a special meal preference for a passenger in a booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string", "description": "The 6-character booking reference code."},
                    "passenger_index": {"type": "integer", "description": "0-based passenger index within the booking list."},
                    "meal": {"type": "string", "description": "Special meal choice (standard, vegetarian, vegan, halal, gluten free, diabetic)."}
                },
                "required": ["pnr", "passenger_index", "meal"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_upgrade",
            "description": "Quote a mock cabin-upgrade pricing and availability offer for a booking PNR.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pnr": {"type": "string", "description": "The 6-character booking reference code."},
                    "target_cabin": {"type": "string", "description": "Desired cabin class (premium_economy, business, first)."}
                },
                "required": ["pnr", "target_cabin"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search direct and connecting flights in the mock schedule between origin and destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "3-letter origin airport code (e.g. DEL, BOM)."},
                    "destination": {"type": "string", "description": "3-letter destination airport code (e.g. BOM, DXB)."},
                    "travel_date": {"type": "string", "description": "Optional travel date in YYYY-MM-DD format."},
                    "passengers": {"type": "integer", "description": "Number of passengers. Defaults to 1.", "default": 1}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_status",
            "description": "Retrieve real-time-style operational status details for a flight number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_number": {"type": "string", "description": "The flight number to lookup (e.g. AR101, AR204)."}
                },
                "required": ["flight_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_schedule",
            "description": "List scheduled arrivals or departures at a specific airport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {"type": "string", "description": "3-letter airport IATA code (e.g. DEL, SIN)."},
                    "direction": {"type": "string", "description": "Either 'departure' or 'arrival'. Defaults to 'departure'.", "default": "departure"}
                },
                "required": ["airport_code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_route_information",
            "description": "Return route details, distance, typical duration, and schedule frequency for a direct route.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "3-letter origin airport code."},
                    "destination": {"type": "string", "description": "3-letter destination airport code."}
                },
                "required": ["origin", "destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_destination_weather",
            "description": "Return current weather conditions and forecasts for a destination city or airport.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "City name or airport code (e.g. Mumbai, DXB)."}
                },
                "required": ["destination"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_travel_advisory",
            "description": "Provide weather-sensitive warnings and practical precautions for a destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string", "description": "City name or airport code."}
                },
                "required": ["destination"]
            }
        }
    }
]

def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a service function by name with parsed arguments.
    """
    logger.info(f"Executing tool {name} with args: {args}")
    try:
        if name == "lookup_airport":
            return lookup_airport(**args)
        elif name == "get_airport_terminal":
            return get_airport_terminal(**args)
        elif name == "find_nearest_airport":
            return find_nearest_airport(**args)
        elif name == "get_baggage_allowance":
            return get_baggage_allowance(**args)
        elif name == "calculate_excess_baggage_fee":
            return calculate_excess_baggage_fee(**args)
        elif name == "get_special_baggage_guidance":
            return get_special_baggage_guidance(**args)
        elif name == "purchase_extra_baggage":
            return purchase_extra_baggage(**args)
        elif name == "lookup_booking":
            return lookup_booking(**args)
        elif name == "cancel_booking":
            return cancel_booking(**args)
        elif name == "select_seat":
            return select_seat(**args)
        elif name == "select_meal":
            return select_meal(**args)
        elif name == "request_upgrade":
            return request_upgrade(**args)
        elif name == "search_flights":
            return search_flights(**args)
        elif name == "get_flight_status":
            return get_flight_status(**args)
        elif name == "get_flight_schedule":
            return get_flight_schedule(**args)
        elif name == "get_route_information":
            return get_route_information(**args)
        elif name == "get_destination_weather":
            return get_destination_weather(**args)
        elif name == "get_travel_advisory":
            return get_travel_advisory(**args)
        else:
            return {"success": False, "message": f"Unknown tool function: {name}"}
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return {"success": False, "message": f"Execution error: {str(e)}"}

def try_tool_calling(client: Groq, model_name: str, question: str) -> Optional[Dict[str, Any]]:
    """
    Checks if the question matches any service tool. If so, executes it and generates a final response.
    Returns:
        dict: A dictionary with keys 'response' and 'sources' (empty list) if a tool is executed.
        None: If the model decides not to run a tool, indicating a RAG pipeline fallback is needed.
    """
    system_prompt = (
        "You are an AI Airline Assistant. You have access to real-time service functions "
        "for flights, bookings, baggage policies, airport directories, and weather. "
        "If the user's request requires executing one of these functions to obtain information "
        "or perform transactions, you MUST trigger the appropriate tool call. "
        "If the user's question is a general query about airline policies (e.g., FAQ, refund policies, "
        "check-in timing, rules) and does not map to any tool, DO NOT call any tool; instead, let the system "
        "handle it using the RAG knowledge documents."
    )

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            tools=TOOLS,
            tool_choice="auto",
            temperature=0
        )
        
        message = response.choices[0].message
        
        if not message.tool_calls:
            return None # No tool was invoked; fallback to RAG

        # Process the tool calls
        tool_outputs = []
        messages_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
            message
        ]

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Execute the tool
            result = execute_tool(tool_name, tool_args)
            tool_outputs.append({
                "tool_name": tool_name,
                "arguments": tool_args,
                "result": result
            })

            # Append the tool message to history
            messages_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": json.dumps(result)
            })

        # Ask the model to generate a final answer based on the tool results
        final_response = client.chat.completions.create(
            model=model_name,
            messages=messages_history,
            temperature=0
        )

        answer = final_response.choices[0].message.content
        sources = [
            {
                "source": f"Service Tool: {output['tool_name']}",
                "arguments": output["arguments"],
                "success": output["result"].get("success", False)
            }
            for output in tool_outputs
        ]
        
        return {
            "response": answer,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Error in tool-calling pipeline: {str(e)}")
        # In case of any API errors, return None so we can fallback to RAG gracefully
        return None
