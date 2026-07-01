from celery.result import AsyncResult
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class TaskStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, task_id):
        """
        Returns the Celery task status and result for a given task ID.
        """
        try:
            res = AsyncResult(task_id)
            status_str = res.status
            result = res.result
            if isinstance(result, Exception):
                result = str(result)
        except Exception:
            status_str = "PENDING"
            result = None
            
        return Response({
            "task_id": task_id,
            "status": status_str,
            "result": result
        })