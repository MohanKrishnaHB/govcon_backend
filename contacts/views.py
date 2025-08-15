from django.shortcuts import render
from .models import Position
from django.http import JsonResponse, HttpResponse
from .models import (
    ContactType, Group, Department, GovernamentOffice,
    PrimaryDesignation, Position, PositionContact
)
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
import os
from openpyxl import Workbook
from django.conf import settings
from django.core import serializers





def get_subordinates(position):
    subordinates = Position.objects.filter(SupervisorPosition=position)
    return [
        {
            'position': sub,
            'children': get_subordinates(sub)  # recursion
        }
        for sub in subordinates
    ]

def org_structure_view(request):
    # Get top-level positions (no supervisor)
    root_positions = Position.objects.filter(SupervisorPosition__isnull=True)

    hierarchy = []
    for root in root_positions:
        hierarchy.append({
            'position': root,
            'children': get_subordinates(root)
        })

    return render(request, 'org_structure.html', {'hierarchy': hierarchy})

@csrf_exempt  # Remove if you handle CSRF in frontend
def map_address_ids(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)  # Expecting a list of dicts
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not isinstance(data, list):
        return JsonResponse({"error": "Expected a list of objects"}, status=400)

    # Fetch all addresses from DB
    addresses = list(GovernamentOffice.objects.values("id", "OfficeAddress"))

    # Helper function to find matching ID
    def find_address_id(address_str):
        for addr in addresses:
            if address_str.lower() in addr["OfficeAddress"].lower():
                return addr["id"]
        return None

    # Add AddressId to each record
    for item in data:
        address_str = item.get("Address", "")
        match_id = find_address_id(address_str) if address_str else None
        item["AddressId"] = match_id

    return JsonResponse(data, safe=False)

@csrf_exempt
def update_designation(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    updated_data = []
    last_address_id = None

    for item in data:
        # If AddressId is missing, use the last known
        if not item.get("AddressId"):
            item["AddressId"] = last_address_id
        else:
            last_address_id = item["AddressId"]

        # Get primaryDesignationId from ShortForm match
        try:
            # Here I assume Designation is same as ShortForm, 
            # adjust if you need a mapping logic
            pd_obj = PrimaryDesignation.objects.filter(
                ShortForm=item.get("Designation", "").strip()
            ).first()
            # item["primaryDesignationId"] = pd_obj.id if pd_obj else None
        except PrimaryDesignation.DoesNotExist:
            # item["primaryDesignationId"] = None
            pass

        updated_data.append(item)

    return JsonResponse(updated_data, safe=False)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
from .models import Position, PositionContact, PrimaryDesignation, GovernamentOffice


@csrf_exempt
def insert_positions_with_contacts(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        records = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    failed_records = []

    for record in records:
        try:
            with transaction.atomic():
                # Lookup PrimaryDesignation
                try:
                    primary_designation = PrimaryDesignation.objects.get(pk=record['PrimaryDesignationId'])
                except PrimaryDesignation.DoesNotExist:
                    raise ValueError(f"PrimaryDesignation {record['PrimaryDesignationId']} not found")

                # Lookup Office
                try:
                    office = GovernamentOffice.objects.get(pk=record['AddressId'])
                except GovernamentOffice.DoesNotExist:
                    raise ValueError(f"Office {record['AddressId']} not found")

                # Prepare position name
                mobile_list = record.get('MobileNumber', [])
                first_mobile = mobile_list[0] if mobile_list else ''

                # If position already exists, change the name for the new one
                if Position.objects.filter(Position=record['Designation']).exists():
                    position_name = f"{record['Designation']} - {first_mobile}" if first_mobile else record['Designation']
                else:
                    position_name = record['Designation']

                # Create new Position
                position_obj = Position.objects.create(
                    Position=position_name,
                    PrimaryDesignation=primary_designation,
                    SupervisorPosition=None,
                    Office=office,
                    DutiesandResponsibilities=''
                )

                # Add mobile contacts
                for mobile in mobile_list:
                    PositionContact.objects.create(
                        Position=position_obj,
                        ContactType_id=2,  # Mobile
                        ContactValue=mobile
                    )

                # Add email contacts
                for email in record.get('Email', []):
                    PositionContact.objects.create(
                        Position=position_obj,
                        ContactType_id=1,  # Email
                        ContactValue=email
                    )

        except (ValueError, IntegrityError) as e:
            failed_records.append({
                'record': record,
                'error': str(e)
            })

    return JsonResponse({
        'status': 'completed',
        'failed_records': failed_records
    })



@csrf_exempt
def delete_all_positions_and_contacts(request):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Only DELETE method is allowed'}, status=405)

    # First delete contacts (since they depend on positions)
    contacts_deleted, _ = PositionContact.objects.all().delete()

    # Then delete positions
    positions_deleted, _ = Position.objects.all().delete()

    return JsonResponse({
        'status': 'success',
        'positions_deleted': positions_deleted,
        'contacts_deleted': contacts_deleted
    })



@csrf_exempt
def save_json_to_xlsx(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    try:
        data = json.loads(request.body)
        if not isinstance(data, list) or not all(isinstance(row, dict) for row in data):
            return JsonResponse({'error': 'Invalid data format. Expected list of objects.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Create workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Data"

    # Write header row from keys of first item
    headers = list(data[0].keys())
    ws.append(headers)

    # Write data rows
    for row in data:
        ws.append([row.get(key, '') for key in headers])

    # Save file in media folder
    output_dir = os.path.join(settings.MEDIA_ROOT, "exports")
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "positions.xlsx")
    wb.save(file_path)

    return JsonResponse({
        'status': 'success',
        'file_path': file_path
    })




# ---------- 1. BACKUP VIEW ----------
@csrf_exempt
def backup_data(request):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET method allowed"}, status=405)

    backup = {}

    # For each model, serialize all records to plain dict (excluding PK)
    def serialize_queryset(qs, fields=None):
        return list(qs.values())

    backup["ContactType"] = serialize_queryset(ContactType.objects.all())
    backup["Group"] = serialize_queryset(Group.objects.all())
    backup["Department"] = serialize_queryset(Department.objects.all())
    backup["GovernamentOffice"] = serialize_queryset(GovernamentOffice.objects.all())
    backup["PrimaryDesignation"] = serialize_queryset(PrimaryDesignation.objects.all())
    backup["Position"] = serialize_queryset(Position.objects.all())
    backup["PositionContact"] = serialize_queryset(PositionContact.objects.all())

    # Return as downloadable JSON
    response = HttpResponse(
        json.dumps(backup, indent=4),
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="backup.json"'
    return response


# ---------- 2. RESTORE VIEW ----------
@csrf_exempt
def restore_data(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)

    try:
        backup = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    with transaction.atomic():
        # First clear existing data if needed (optional)
        # ContactType.objects.all().delete()
        # Group.objects.all().delete()
        # Department.objects.all().delete()
        # GovernamentOffice.objects.all().delete()
        # PrimaryDesignation.objects.all().delete()
        # Position.objects.all().delete()
        # PositionContact.objects.all().delete()

        # Map old IDs to new IDs for foreign key resolution
        id_map = {
            "ContactType": {},
            "Group": {},
            "Department": {},
            "GovernamentOffice": {},
            "PrimaryDesignation": {},
            "Position": {}
        }

        # Restore in dependency order
        for item in backup.get("ContactType", []):
            old_id = item.pop("id", None)
            obj = ContactType.objects.create(**item)
            id_map["ContactType"][old_id] = obj.id

        for item in backup.get("Group", []):
            old_id = item.pop("id", None)
            obj = Group.objects.create(**item)
            id_map["Group"][old_id] = obj.id

        for item in backup.get("Department", []):
            old_id = item.pop("id", None)
            obj = Department.objects.create(**item)
            id_map["Department"][old_id] = obj.id

        for item in backup.get("GovernamentOffice", []):
            old_id = item.pop("id", None)
            item["Department_id"] = id_map["Department"][item["Department_id"]]
            obj = GovernamentOffice.objects.create(**item)
            id_map["GovernamentOffice"][old_id] = obj.id

        for item in backup.get("PrimaryDesignation", []):
            old_id = item.pop("id", None)
            item["Group_id"] = id_map["Group"][item["Group_id"]]
            item["Department_id"] = id_map["Department"][item["Department_id"]]
            obj = PrimaryDesignation.objects.create(**item)
            id_map["PrimaryDesignation"][old_id] = obj.id

        for item in backup.get("Position", []):
            old_id = item.pop("id", None)
            item["PrimaryDesignation_id"] = id_map["PrimaryDesignation"][item["PrimaryDesignation_id"]]
            item["Office_id"] = id_map["GovernamentOffice"][item["Office_id"]]
            if item["SupervisorPosition_id"]:
                item["SupervisorPosition_id"] = id_map["Position"].get(item["SupervisorPosition_id"])
            obj = Position.objects.create(**item)
            id_map["Position"][old_id] = obj.id

        for item in backup.get("PositionContact", []):
            old_id = item.pop("id", None)
            item["Position_id"] = id_map["Position"][item["Position_id"]]
            item["ContactType_id"] = id_map["ContactType"][item["ContactType_id"]]
            PositionContact.objects.create(**item)

    return JsonResponse({"status": "Restore completed successfully"})
