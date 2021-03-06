"""
Progress Tab Serializers
"""
from rest_framework import serializers
from rest_framework.reverse import reverse
from lms.djangoapps.certificates.models import CertificateStatuses


class GradedTotalSerializer(serializers.Serializer):
    earned = serializers.FloatField()
    possible = serializers.FloatField()


class SubsectionSerializer(serializers.Serializer):
    display_name = serializers.CharField()
    due = serializers.DateTimeField()
    format = serializers.CharField()
    graded = serializers.BooleanField()
    graded_total = GradedTotalSerializer()
    # TODO: override serializer
    percent_graded = serializers.FloatField()
    problem_scores = serializers.SerializerMethodField()
    show_correctness = serializers.CharField()
    show_grades = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    def get_url(self, subsection):
        relative_path = reverse('jump_to', args=[self.context['course_key'], subsection.location])
        request = self.context['request']
        return request.build_absolute_uri(relative_path)

    def get_problem_scores(self, subsection):
        problem_scores = [
            {
                'earned': score.earned,
                'possible': score.possible,
            }
            for score in subsection.problem_scores.values()
        ]
        return problem_scores

    def get_show_grades(self, subsection):
        return subsection.show_grades(self.context['staff_access'])


class ChapterSerializer(serializers.Serializer):
    """
    Serializer for chapters in coursewaresummary
    """
    display_name = serializers.CharField()
    subsections = SubsectionSerializer(source='sections', many=True)


class CertificateDataSerializer(serializers.Serializer):
    cert_web_view_url = serializers.CharField()
    download_url = serializers.CharField()
    is_downloadable = serializers.SerializerMethodField()
    is_requestable = serializers.SerializerMethodField()
    msg = serializers.CharField()
    title = serializers.CharField()

    def get_is_downloadable(self, cert_data):
        return cert_data.cert_status == CertificateStatuses.downloadable and cert_data.download_url is not None

    def get_is_requestable(self, cert_data):
        return cert_data.cert_status == CertificateStatuses.requesting and cert_data.request_cert_url is not None


class CreditCourseRequirementsSerializer(serializers.Serializer):
    """
    Serializer for credit_course_requirements
    """
    display_name = serializers.CharField()
    namespace = serializers.CharField()
    min_grade = serializers.SerializerMethodField()
    status = serializers.CharField()
    status_date = serializers.DateTimeField()

    def get_min_grade(self, req):
        return req['criteria']['min_grade'] * 100


class ProgressTabSerializer(serializers.Serializer):
    """
    Serializer for progress tab
    """
    certificate_data = CertificateDataSerializer()
    courseware_summary = ChapterSerializer(many=True)
    enrollment_mode = serializers.CharField()
    studio_url = serializers.CharField()
    user_timezone = serializers.CharField()
