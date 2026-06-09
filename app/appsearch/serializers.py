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


class SimilarTransactionSearchRequestSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(required=False, min_value=1)
    document_line_id = serializers.IntegerField(required=False, min_value=1)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=50, default=20)

    def validate(self, attrs):
        if not attrs.get('document_id') and not attrs.get('document_line_id'):
            raise serializers.ValidationError(
                'Provide document_id or document_line_id.'
            )
        return attrs


class SimilarSeedSerializer(serializers.Serializer):
    document_id = serializers.IntegerField(allow_null=True)
    document_line_id = serializers.IntegerField()
    snippet = serializers.CharField()


class SimilarTransactionSearchResponseSerializer(serializers.Serializer):
    seed = SimilarSeedSerializer()
    results = TransactionSearchResultSerializer(many=True)
    document_ids = serializers.ListField(child=serializers.IntegerField())
    count = serializers.IntegerField()
