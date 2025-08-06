from django.shortcuts import render
from .models import Position

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