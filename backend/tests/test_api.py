import io
import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient


def make_test_workbook() -> SimpleUploadedFile:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Clean Data"
    # Match the exact column headers your Day 2 loader expects
    ws.append(["Date", "Cafe", "Quantity (kg)"])
    ws.append(["2026-01-01", "Fire Ice", 10.0])
    ws.append(["2026-01-01", "Roadhouse", 15.0])
    ws.append(["2026-01-02", "Fire Ice", 12.0])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return SimpleUploadedFile(
        "test_cafe_data.xlsx",
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


class ImportEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_import_is_idempotent(self):
        # 1st upload: 2 unique cafes, 3 unique (date, cafe) stops
        res1 = self.client.post("/api/import/", {"file": make_test_workbook()}, format="multipart")
        self.assertEqual(res1.status_code, 200, msg=res1.json())
        self.assertEqual(res1.json(), {"cafes": 2, "stops": 3})

        # 2nd upload of the exact same data: counts must not change
        res2 = self.client.post("/api/import/", {"file": make_test_workbook()}, format="multipart")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json(), {"cafes": 2, "stops": 3})

    def test_missing_file_returns_400(self):
        res = self.client.post("/api/import/", {}, format="multipart")
        self.assertEqual(res.status_code, 400)