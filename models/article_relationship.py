from django.db import models


class ArticleRelationshipRelationType(models.TextChoices):
    GREATER = "GREATER"
    EQUAL = "EQUAL"
    LESS = "LESS"


class ArticleRelationshipDifferentialType(models.TextChoices):
    PERCENTAGE = "PERCENTAGE"


class ArticleRelationshipType(models.TextChoices):
    GOODBETTERBEST = "GOODBETTERBEST"
    OWNBRANDVSNATIONALBRAND = "OWNBRANDVSNATIONALBRAND"
    SIZEGROUPPRICING = "SIZEGROUPPRICING"


class ArticleRelationship(models.Model):

    source_article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="article_relationship_source_article",
    )
    target_article = models.ForeignKey(
        "core.Article",
        on_delete=models.CASCADE,
        related_name="article_relationship_target_article",
    )
    relation = models.CharField(
        max_length=20,
        choices=ArticleRelationshipRelationType.choices,
        default=ArticleRelationshipRelationType.GREATER,
    )
    differential = models.FloatField()
    differential_type = models.CharField(
        max_length=100,
        choices=ArticleRelationshipDifferentialType.choices,
        default=ArticleRelationshipDifferentialType.PERCENTAGE,
    )
    relationship_type = models.CharField(
        max_length=100,
        choices=ArticleRelationshipType.choices,
        default=ArticleRelationshipType.GOODBETTERBEST,
    )
