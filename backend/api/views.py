from django.db import transaction
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from dairy_core.data.loader import read_rows, build_stops_by_day
from .models import Cafe, Visit


class ImportView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        # 1. Get the uploaded file from the request
        f = request.FILES.get("file")
        if f is None:
            return Response(
                {"error": "No file uploaded. Send the Excel file under the 'file' key."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 2. Call your Day 2 loader: rows, then stops per day
        try:
            rows = read_rows(f)
            stops_by_day = build_stops_by_day(rows)  # {date: [cafe_name, ...]}
        except Exception as exc:
            return Response(
                {"error": f"Invalid workbook: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not stops_by_day:
            return Response(
                {"error": "No valid delivery rows found in workbook."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Wrap all database writes in an atomic transaction
        with transaction.atomic():
            # 3. Ensure a Cafe row exists for every unique cafe name
            cafe_map = {}
            for cafe_names in stops_by_day.values():
                for name in cafe_names:
                    if name not in cafe_map:
                        cafe_obj, _ = Cafe.objects.get_or_create(name=name)
                        cafe_map[name] = cafe_obj

            # 4. Build Visit objects and batch-insert them, skipping existing (cafe, date) pairs
            visits_to_create = [
                Visit(cafe=cafe_map[name], date=day)
                for day, cafe_names in stops_by_day.items()
                for name in cafe_names
            ]
            Visit.objects.bulk_create(visits_to_create, ignore_conflicts=True)

        # 5. Return database counts as JSON
        return Response(
            {
                "cafes": Cafe.objects.count(),
                "stops": Visit.objects.count(),
            },
            status=status.HTTP_200_OK,
        )