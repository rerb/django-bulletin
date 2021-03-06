from django.contrib.auth.models import User
from rest_framework import serializers

from ..models import (Ad,
                      AdSize,
                      Category,
                      Issue,
                      IssueTemplate,
                      Link,
                      Newsletter,
                      Post,
                      Section,
                      SectionTemplate)


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name')


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    parent = serializers.PrimaryKeyRelatedField(
        many=False,
        default=None,
        allow_null=True,
        read_only=False,
        queryset=Category.objects.all())
    section_templates = serializers.StringRelatedField(many=True,
                                                       required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'parent', 'fully_qualified_name',
                  'section_templates')


class LinkSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Link
        fields = ('id', 'text', 'url')


class ScheduledPostSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Link
        fields = ('id', 'pub_date')


class PostSerializer(serializers.HyperlinkedModelSerializer):

    submitter = serializers.PrimaryKeyRelatedField(many=False,
                                                   required=False,
                                                   read_only=True)
    links = LinkSerializer(many=True, required=False,
                           read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'title', 'url', 'approved', 'pub_date',
                  'submitter', 'position', 'links')


class SectionPostReorderSerializer(serializers.HyperlinkedModelSerializer):
    """Used for section-post-up, section-post-down, etc.
    """
    class Meta:
        model = Post
        fields = ('id', 'position')
        read_only_fields = ('position',)


class SectionSerializer(serializers.HyperlinkedModelSerializer):

    posts = PostSerializer(many=True, required=False,
                           read_only=True)

    class Meta:
        model = Section
        fields = ('id', 'name', 'posts', 'position')


class IssueSectionReorderSerializer(serializers.HyperlinkedModelSerializer):
    """Used for issue-section-up, issue-section-down, etc.
    """
    class Meta:
        model = Section
        fields = ('id', 'position')
        read_only_fields = ('position',)


class IssueSerializer(serializers.HyperlinkedModelSerializer):

    sections = SectionSerializer(many=True, required=False)

    class Meta:
        model = Issue
        fields = ('id', 'pub_date', 'sections', 'name', 'subject',
                  'from_name', 'from_email', 'reply_to_email',
                  'organization_name', 'address_line_1', 'address_line_2',
                  'address_line_3', 'city', 'state', 'international_state',
                  'postal_code', 'country', 'html_template_name',
                  'text_template_name')

    def create(self, validated_data):
        sections_data = validated_data.pop('sections', [])
        issue = Issue.objects.create(**validated_data)
        for section_data in sections_data:
            Section.objects.create(issue=issue, **section_data)
        return issue


class NewsletterSerializer(serializers.HyperlinkedModelSerializer):

    issues = serializers.HyperlinkedIdentityField(
        many=True,
        read_only=True,
        view_name='bulletin:api:issue-detail')

    class Meta:
        model = Newsletter
        fields = ('id', 'name', 'issues')


class SectionTemplateSerializer(serializers.HyperlinkedModelSerializer):

    categories = CategorySerializer(many=True, required=False)

    class Meta:
        model = SectionTemplate
        fields = ('id', 'name', 'position', 'categories')


class IssueTemplateSerializer(serializers.HyperlinkedModelSerializer):

    section_templates = SectionTemplateSerializer(many=True, required=False)

    class Meta:
        model = IssueTemplate
        fields = ('id', 'name', 'section_templates', 'subject',
                  'from_name', 'from_email', 'reply_to_email',
                  'organization_name', 'address_line_1', 'address_line_2',
                  'address_line_3', 'city', 'state', 'international_state',
                  'postal_code', 'country', 'html_template_name',
                  'text_template_name')


class AdSizeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = AdSize
        fields = ('name', 'width', 'height')


class AdSerializer(serializers.HyperlinkedModelSerializer):

    size = serializers.PrimaryKeyRelatedField(
        queryset=AdSize.objects.all(),
        many=False,
        required=True)

    class Meta:
        model = Ad
        fields = ('name', 'start', 'end', 'size', 'url',
                  'show_on_website', 'include_in_newsletter')
