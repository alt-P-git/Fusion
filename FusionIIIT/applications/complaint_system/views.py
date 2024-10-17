#views.py
import datetime
from datetime import date, datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render
from applications.globals.models import User, ExtraInfo, HoldsDesignation

from notifications.models import Notification
from .models import Caretaker, StudentComplain, Supervisor
from notification.views import complaint_system_notif

from applications.filetracking.sdk.methods import *
from applications.filetracking.models import *
from operator import attrgetter

# Import DRF classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import (
    StudentComplainSerializer,
    CaretakerSerializer,
    ExtraInfoSerializer,
)

# Converted to DRF APIView
class CheckUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        The function is used to check the type of user.
        There are three types of users: student, staff, or faculty.
        Returns the user type and the appropriate endpoint.
        """
        a = request.user
        b = ExtraInfo.objects.select_related("user", "department").filter(user=a).first()
        supervisor_list = Supervisor.objects.all()
        caretaker_list = Caretaker.objects.all()
        is_supervisor = False
        is_caretaker = False
        for i in supervisor_list:
            if b.id == i.sup_id_id:
                is_supervisor = True
                break
        for i in caretaker_list:
            if b.id == i.staff_id_id:
                is_caretaker = True
                break
        if is_supervisor:
            return Response({"user_type": "supervisor", "next_url": "/complaint/supervisor/"})
        elif is_caretaker:
            return Response({"user_type": "caretaker", "next_url": "/complaint/caretaker/"})
        elif b.user_type == "student":
            return Response({"user_type": "student", "next_url": "/complaint/user/"})
        elif b.user_type == "staff":
            return Response({"user_type": "staff", "next_url": "/complaint/user/"})
        elif b.user_type == "faculty":
            return Response({"user_type": "faculty", "next_url": "/complaint/user/"})
        else:
            return Response({"error": "wrong user credentials"}, status=400)

# Converted to DRF APIView
class UserComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns the list of complaints made by the user.
        """
        a = request.user
        y = ExtraInfo.objects.select_related("user", "department").filter(user=a).first()
        complaints = StudentComplain.objects.filter(complainer=y).order_by("-id")
        serializer = StudentComplainSerializer(complaints, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Allows the user to register a new complaint.
        """
        a = request.user
        y = ExtraInfo.objects.select_related("user", "department").filter(user=a).first()
        data = request.data.copy()
        data["complainer"] = y.id
        data["status"] = 0
        comp_type = data.get("complaint_type", "")
        # Finish time is according to complaint type
        complaint_finish = datetime.now() + timedelta(days=2)
        if comp_type == "Electricity":
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == "carpenter":
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == "plumber":
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == "garbage":
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == "dustbin":
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == "internet":
            complaint_finish = datetime.now() + timedelta(days=4)
        elif comp_type == "other":
            complaint_finish = datetime.now() + timedelta(days=3)
        data["complaint_finish"] = complaint_finish

        serializer = StudentComplainSerializer(data=data)
        if serializer.is_valid():
            complaint = serializer.save()
            # Handle file uploads, notifications, etc.
            # Omitted for brevity.
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)

# Converted to DRF APIView
class CaretakerFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Allows the user to submit feedback for a particular type of caretaker.
        """
        feedback = request.data.get("feedback", "")
        rating = request.data.get("rating", "")
        caretaker_type = request.data.get("caretakertype", "")
        try:
            rating = int(rating)
        except ValueError:
            return Response({"error": "Invalid rating"}, status=400)
        all_caretaker = Caretaker.objects.filter(area=caretaker_type).order_by("-id")
        for x in all_caretaker:
            rate = x.rating
            if rate == 0:
                newrate = rating
            else:
                newrate = (rate + rating) / 2
            x.myfeedback = feedback
            x.rating = newrate
            x.save()
        return Response({"success": "Feedback submitted"})

# Converted to DRF APIView
class SubmitFeedbackView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, complaint_id):
        """
        Allows the user to submit feedback for a complaint.
        """
        feedback = request.data.get("feedback", "")
        rating = request.data.get("rating", "")
        try:
            rating = int(rating)
        except ValueError:
            return Response({"error": "Invalid rating"}, status=400)
        StudentComplain.objects.filter(id=complaint_id).update(feedback=feedback, flag=rating)
        a = StudentComplain.objects.select_related("complainer", "complainer_user", "complainer_department").filter(id=complaint_id).first()
        care = Caretaker.objects.filter(area=a.location).first()
        rate = care.rating
        if rate == 0:
            newrate = rating
        else:
            newrate = int((rating + rate) / 2)
        care.rating = newrate
        care.save()
        return Response({"success": "Feedback submitted"})

# Converted to DRF APIView
class ComplaintDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, detailcomp_id1):
        """
        Returns the details of a complaint.
        """
        try:
            complaint = StudentComplain.objects.select_related(
                "complainer", "complainer_user", "complainer_department"
            ).get(id=detailcomp_id1)
        except StudentComplain.DoesNotExist:
            return Response({"error": "Complaint not found"}, status=404)
        serializer = StudentComplainSerializer(complaint)
        return Response(serializer.data)
    # Import DRF classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Import necessary models and serializers
from .serializers import (
    StudentComplainSerializer,
    CaretakerSerializer,
    FeedbackSerializer,
    ResolvePendingSerializer,
)
# Other imports remain the same
import datetime
from datetime import datetime, timedelta
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404, render
from applications.globals.models import User, ExtraInfo, HoldsDesignation
from notifications.models import Notification
from .models import Caretaker, StudentComplain, Supervisor
from notification.views import complaint_system_notif
from applications.filetracking.sdk.methods import *
from applications.filetracking.models import *
from operator import attrgetter

# Converted to DRF APIView
class CaretakerLodgeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Allows the caretaker to lodge a new complaint.
        """
        # Get the current user
        a = request.user
        y = ExtraInfo.objects.select_related('user', 'department').filter(user=a).first()

        data = request.data.copy()
        data['complainer'] = y.id
        data['status'] = 0

        comp_type = data.get('complaint_type', '')
        # Finish time is according to complaint type
        complaint_finish = datetime.now() + timedelta(days=2)
        if comp_type == 'Electricity':
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == 'carpenter':
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == 'plumber':
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == 'garbage':
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == 'dustbin':
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == 'internet':
            complaint_finish = datetime.now() + timedelta(days=4)
        elif comp_type == 'other':
            complaint_finish = datetime.now() + timedelta(days=3)
        data['complaint_finish'] = complaint_finish

        serializer = StudentComplainSerializer(data=data)
        if serializer.is_valid():
            complaint = serializer.save()

            # Notification logic (if any)
            location = data.get('location', '')
            if location == "hall-1":
                dsgn = "hall1caretaker"
            elif location == "hall-3":
                dsgn = "hall3caretaker"
            elif location == "hall-4":
                dsgn = "hall4caretaker"
            elif location == "CC1":
                dsgn = "cc1convener"
            elif location == "CC2":
                dsgn = "CC2 convener"
            elif location == "core_lab":
                dsgn = "corelabcaretaker"
            elif location == "LHTC":
                dsgn = "lhtccaretaker"
            elif location == "NR2":
                dsgn = "nr2caretaker"
            elif location == "Maa Saraswati Hostel":
                dsgn = "mshcaretaker"
            elif location == "Nagarjun Hostel":
                dsgn = "nhcaretaker"
            elif location == "Panini Hostel":
                dsgn = "phcaretaker"
            else:
                dsgn = "rewacaretaker"
            caretaker_name = HoldsDesignation.objects.select_related('user', 'working', 'designation').get(designation__name=dsgn)

            # Send notification
            student = 1
            message = "A New Complaint has been lodged"
            complaint_system_notif(request.user, caretaker_name.user, 'lodge_comp_alert', complaint.id, student, message)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Returns the list of complaints lodged by the caretaker.
        """
        a = request.user
        y = ExtraInfo.objects.select_related('user', 'department').filter(user=a).first()
        complaints = StudentComplain.objects.filter(complainer=y).order_by('-id')
        serializer = StudentComplainSerializer(complaints, many=True)
        return Response(serializer.data)

# Converted to DRF APIView
class CaretakerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Returns the list of complaints assigned to the caretaker.
        """
        current_user = request.user
        y = ExtraInfo.objects.select_related('user', 'department').filter(user=current_user).first()
        try:
            a = Caretaker.objects.select_related('staff_id', 'staff_id_user', 'staff_id_department').get(staff_id=y.id)
            b = a.area
            complaints = StudentComplain.objects.filter(location=b).order_by('-id')
            serializer = StudentComplainSerializer(complaints, many=True)
            return Response(serializer.data)
        except Caretaker.DoesNotExist:
            return Response({'error': 'Caretaker does not exist'}, status=status.HTTP_404_NOT_FOUND)

# Converted to DRF APIView
class FeedbackCareView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, feedcomp_id):
        """
        Returns the feedback details for a specific complaint.
        """
        try:
            detail = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').get(id=feedcomp_id)
            serializer = StudentComplainSerializer(detail)
            return Response(serializer.data)
        except StudentComplain.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

# Converted to DRF APIView
class ResolvePendingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, cid):
        """
        Allows the caretaker to resolve a pending complaint.
        """
        serializer = ResolvePendingSerializer(data=request.data)
        if serializer.is_valid():
            newstatus = serializer.validated_data['yesorno']
            comment = serializer.validated_data.get('comment', '')
            intstatus = 2 if newstatus == 'Yes' else 3
            StudentComplain.objects.filter(id=cid).update(status=intstatus, comment=comment)

            # Send notification to the complainer
            complainer_details = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').get(id=cid)
            student = 0
            message = "Congrats! Your complaint has been resolved"
            complaint_system_notif(request.user, complainer_details.complainer.user, 'comp_resolved_alert', complainer_details.id, student, message)

            return Response({'success': 'Complaint status updated'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, cid):
        """
        Returns the details of the complaint to be resolved.
        """
        try:
            complaint = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').get(id=cid)
            serializer = StudentComplainSerializer(complaint)
            return Response(serializer.data)
        except StudentComplain.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

# Converted to DRF APIView
class ComplaintDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, detailcomp_id1):
        """
        Returns the details of a complaint for the caretaker.
        """
        try:
            complaint = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').get(id=detailcomp_id1)
            serializer = StudentComplainSerializer(complaint)
            return Response(serializer.data)
        except StudentComplain.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

# Converted to DRF APIView
class SearchComplaintView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Searches for complaints based on query parameters.
        """
        # Implement search logic based on query parameters
        # For now, return all complaints
        complaints = StudentComplain.objects.all()
        serializer = StudentComplainSerializer(complaints, many=True)
        return Response(serializer.data)

# Converted to DRF APIView
class SubmitFeedbackCaretakerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, complaint_id):
        """
        Allows the caretaker to submit feedback for a complaint.
        """
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            feedback = serializer.validated_data['feedback']
            rating = serializer.validated_data['rating']
            try:
                rating = int(rating)
            except ValueError:
                return Response({'error': 'Invalid rating'}, status=status.HTTP_400_BAD_REQUEST)
            StudentComplain.objects.filter(id=complaint_id).update(feedback=feedback, flag=rating)

            a = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').filter(id=complaint_id).first()
            care = Caretaker.objects.filter(area=a.location).first()
            rate = care.rating
            newrate = int((rating + rate) / 2) if rate != 0 else rating
            care.rating = newrate
            care.save()
            return Response({'success': 'Feedback submitted'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, complaint_id):
        """
        Returns the complaint details for which feedback is to be submitted.
        """
        try:
            complaint = StudentComplain.objects.select_related('complainer', 'complainer_user', 'complainer_department').get(id=complaint_id)
            serializer = StudentComplainSerializer(complaint)
            return Response(serializer.data)
        except StudentComplain.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)
