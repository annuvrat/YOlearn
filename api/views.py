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
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def get(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"error": "Missing or invalid Authorization header"}, status=401)

        token = auth_header.split(" ")[1]

        # Decode Supabase JWT to get user_id
        user_info_resp = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"Authorization": f"Bearer {token}", "apikey": SUPABASE_SERVICE_KEY}
        )
        if user_info_resp.status_code != 200:
            return Response({"error": "Invalid Supabase token"}, status=401)

        user_id = user_info_resp.json().get("id")
        if not user_id:
            return Response({"error": "User ID not found in token"}, status=401)

        # Pagination
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 10))
            offset = (page - 1) * limit
        except ValueError:
            return Response({"error": "Invalid page or limit value"}, status=400)

        # Optional filters
        tool = request.query_params.get("tool")
        date = request.query_params.get("date")  # Expected in YYYY-MM-DD

        filters = [f"user_id=eq.{user_id}"]
        if tool:
            filters.append(f"tool_name=eq.{tool}")
        if date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
                filters.append(f"created_at::date=eq.{parsed_date}")
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"}, status=400)

        filter_str = "&".join(filters)

        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Prefer": "count=exact"
        }

        # Count total matching items
        count_url = f"{SUPABASE_URL}/rest/v1/ai_outputs?{filter_str}&select=id"
        count_resp = requests.get(count_url, headers=headers)

        if count_resp.status_code != 200:
            return Response({"error": "Failed to count items from Supabase"}, status=500)

        content_range = count_resp.headers.get("content-range")
        try:
            total_items = int(content_range.split("/")[-1]) if content_range else 0
        except Exception:
            total_items = 0

        total_pages = (total_items + limit - 1) // limit if limit > 0 else 1

        # Get actual data
        data_url = f"{SUPABASE_URL}/rest/v1/ai_outputs?{filter_str}&select=tool_name,output_content,created_at&order=created_at.desc&limit={limit}&offset={offset}"
        data_resp = requests.get(data_url, headers=headers)

        if data_resp.status_code != 200:
            return Response({"error": "Failed to fetch data from Supabase"}, status=500)

        data = data_resp.json()

        return Response({
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "total_items": total_items,
            "data": data
        })
