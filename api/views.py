from django.shortcuts import render
import os
import jwt
import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from rest_framework import status
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename="output.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
print(SUPABASE_JWT_SECRET)
# Log environment variable status
logging.info(f"SUPABASE_URL: {SUPABASE_URL}")
logging.info(f"SUPABASE_SERVICE_KEY: {'SET' if SUPABASE_SERVICE_KEY else 'NOT SET'}")
logging.info(f"SUPABASE_JWT_SECRET: {'SET' if SUPABASE_JWT_SECRET else 'NOT SET'}")


class StoreOutputView(APIView):
    def post(self, request):
        # Step 1: Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                {"error": "Missing or invalid token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split(" ")[1]

        try:
            # Step 2: Decode JWT using your Supabase JWT secret
            decoded = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
            user_id = decoded.get("sub")
            if not user_id:
                raise ValueError("sub not found in token")
        except Exception as e:
            return Response(
                {"error": f"Token decode error: {str(e)}"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Step 3: Get tool_name and output_content from request body
        tool_name = request.data.get("tool_name")
        output_content = request.data.get("output_content")

        if not tool_name or not output_content:
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Step 4: Insert into Supabase table
        try:
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/ai_outputs",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json={
                    "user_id": user_id,
                    "tool_name": tool_name,
                    "output_content": output_content,
                },
            )

            if response.status_code not in [200, 201]:
                return Response(
                    {"error": "Supabase insert failed", "details": response.text},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            result = response.json()

            # Step 5: Log to output.log
            logging.info(f"Output stored: {result}")

            return Response(
                {"message": "Output stored successfully", "data": result},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logging.error(f"Error storing output: {str(e)}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class GetOutputsView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Missing or invalid token"}, status=401)

        token = auth_header.split(" ")[1]
        try:
            decoded = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            user_id = decoded['sub']
        except jwt.InvalidTokenError as e:
            return Response({"error": f"Token decode error: {str(e)}"}, status=401)

        # Filters
        tool = request.query_params.get('tool')
        date = request.query_params.get('date')

        # Validate date
        if date:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Pagination
        try:
            limit = int(request.query_params.get('limit', 10))
            page = int(request.query_params.get('page', 1))
            offset = (page - 1) * limit
        except ValueError:
            return Response({"error": "Invalid pagination params"}, status=400)

        # Base filters
        filter_query = f"user_id=eq.{user_id}"
        if tool:
            filter_query += f"&tool_name=eq.{tool}"
        if date:
            filter_query += f"&created_at=gte.{date}T00:00:00Z&created_at=lt.{date}T23:59:59Z"

        # Count query for pagination metadata
        count_url = f"{SUPABASE_URL}/rest/v1/ai_outputs?{filter_query}&select=id"
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Prefer": "count=exact"
        }
        
        logging.info(f"Count URL: {count_url}")
        count_response = requests.get(count_url, headers=headers)
        logging.info(f"Count response status: {count_response.status_code}")
        
        if count_response.status_code not in [200, 206]:
            logging.error(f"Count failed: {count_response.status_code} - {count_response.text}")
            return Response({"error": "Failed to count items from Supabase"}, status=500)
            
        content_range = count_response.headers.get("content-range")
        logging.info(f"Content-Range header: {content_range}")
        
        try:
            total_items = int(content_range.split("/")[-1]) if content_range else 0
        except Exception as e:
            logging.error(f"Error parsing content-range: {e}")
            total_items = 0
        total_pages = (total_items + limit - 1) // limit  # ceil

        # Final query to get paginated data
        data_url = f"{SUPABASE_URL}/rest/v1/ai_outputs?{filter_query}&select=tool_name,output_content,created_at&limit={limit}&offset={offset}"
        logging.info(f"Data URL: {data_url}")
        data_response = requests.get(data_url, headers=headers)
        logging.info(f"Data response status: {data_response.status_code}")

        if data_response.status_code not in [200, 206]:
            logging.error(f"Data failed: {data_response.status_code} - {data_response.text}")
            return Response({"error": "Failed to fetch data from Supabase"}, status=500)

        return Response({
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "total_items": total_items,
            "data": data_response.json()
        }, status=200)