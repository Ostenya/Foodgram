from django.db.models import Count
from django.shortcuts import get_object_or_404
from recipes.mixins import PostDeleteViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscription, User
from .permissions import DetailsAuthenticatedOnly
from .serializers import (CurrentUserSerializer, SubscriptionSerializer,
                          UserSetPasswordSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для обработки запросов на ендпоинты /users."""

    queryset = User.objects.all()
    serializer_class = CurrentUserSerializer
    permission_classes = (DetailsAuthenticatedOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        methods=['get'],
        detail=False,
        url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_me(self, request):
        serializer = CurrentUserSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post'],
        detail=False,
        url_path='set_password',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = UserSetPasswordSerializer(
            request.user,
            data=request.data,
            many=False,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['get'],
        detail=False,
        url_path='subscriptions',
    )
    def get_subscriptions(self, request):
        queryset = User.objects.filter(
            subscribed__user=request.user).annotate(
                recipes_count=Count('recipes'))
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscriptionViewSet(PostDeleteViewSet):
    """Вьюсет для подписки/отписки.
    Внимание! За отображение списка подписчиков отвечает
    action get_subscriptions вьюсета UserViewSet."""

    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        subscribed = get_object_or_404(
            User,
            id=self.kwargs.get('id')
        )
        if not request.user == subscribed:
            Subscription.objects.create(
                user=request.user,
                author=subscribed,
            )
        subscribed.recipes_count = subscribed.recipes.count()
        serializer = self.get_serializer(subscribed)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        subscribed = get_object_or_404(
            User,
            id=id
        )
        Subscription.objects.filter(
            user=request.user,
            author=subscribed,
        ).delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
