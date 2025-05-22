
from rest_framework             import serializers

from common.rest                import SerializerWithCustomFields

from discussion.models          import Discussion, Message, Publication

class PublicationSerializer(SerializerWithCustomFields):
    class Meta:
        model = Publication
        exclude = []
    def fill_additional_data(self, publication, result):
        result["author_name"] = publication.author.get_full_name()

class PartialPublicationSerializer(PublicationSerializer):
    class Meta:
        model = Publication
        # Remove "response" and other fields for anonymous users
        fields = Publication.PUBLIC_FIELDS

class MessageSerializer(SerializerWithCustomFields):
    class Meta:
        model = Message
        exclude = []
    def fill_additional_data(self, message, result):
        result["author_name"] = message.author.get_full_name()

class DiscussionSerializer(SerializerWithCustomFields):
    class Meta:
        model = Discussion
        exclude = []

    def fill_additional_data(self, discussion, result):

        result["nb_unread"] = discussion.nb_unread_messages()
        if discussion.publication_id:
            result["publication_url"] = discussion.publication.url_key
        else:
            result["publication_url"] = None

        if self.has_many_objs():
            result["nb_messages"] = discussion.messages.count()
        else:
            result["messages"] = MessageSerializer(discussion.messages.all().order_by("date"), many = True).data