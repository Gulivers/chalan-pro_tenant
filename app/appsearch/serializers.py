from rest_framework import serializers


class TransactionSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(required=True, allow_blank=False, max_length=500)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=100, default=50)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class TransactionSearchResultSerializer(serializers.Serializer):
    document_line_id = serializers.IntegerField()
    document_id = serializers.IntegerField()
    score = serializers.FloatField()
    snippet = serializers.CharField()
    metadata = serializers.DictField()


class TransactionSearchResponseSerializer(serializers.Serializer):
    query = serializers.CharField()
    semantic_query = serializers.CharField()
    applied_filters = serializers.DictField()
    resolved_entities = serializers.DictField()
    results = TransactionSearchResultSerializer(many=True)
    document_ids = serializers.ListField(child=serializers.IntegerField())
    count = serializers.IntegerField()
