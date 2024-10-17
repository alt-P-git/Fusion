#Was creating error due to use of dateTime instead of date
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
        elif comp_type == "Carpenter":
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == "Plumber":
            complaint_finish = datetime.now() + timedelta(days=2)
        elif comp_type == "Garbage":
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == "Dustbin":
            complaint_finish = datetime.now() + timedelta(days=1)
        elif comp_type == "Internet":
            complaint_finish = datetime.now() + timedelta(days=4)
        elif comp_type == "Other":
            complaint_finish = datetime.now() + timedelta(days=3)
        data["complaint_finish"] = complaint_finish.date()

        serializer = StudentComplainSerializer(data=data)
        if serializer.is_valid():
            complaint = serializer.save()
            # Handle file uploads, notifications, etc.
            # Omitted for brevity.
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


#Was crashing server on some requests due to absence of try catch
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
        
        try:
            StudentComplain.objects.filter(id=complaint_id).update(feedback=feedback, flag=rating)
            a = StudentComplain.objects.filter(id=complaint_id).first()
            care = Caretaker.objects.filter(area=a.location).first()
            rate = care.rating
            if rate == 0:
                newrate = rating
            else:
                newrate = int((rating + rate) / 2)
            care.rating = newrate
            care.save()
            return Response({"success": "Feedback submitted"})
        except:
            print("---error---")
            return Response({"error": "Internal server errror"}, status=500)



#Was creating error due to use of dateTime instead of date
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
        data['complaint_finish'] = complaint_finish.date()

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

