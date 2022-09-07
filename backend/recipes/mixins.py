from rest_framework import mixins, viewsets


class PostDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass
