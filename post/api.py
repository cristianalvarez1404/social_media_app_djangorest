from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.http import JsonResponse
from django.shortcuts import render

#models
from .models import Post, Like, Comment, Trend
from account.models import User

#forms
from .forms import PostForm

#serializers
from account.serializer import UserSerializer
from .serializers import PostSerializer, PostDetailSerializer, CommentSerializer, TrendSerializer

@api_view(['GET'])
def post_list(request):
  user_ids = [request.user.id]

  for user in request.user.friends.all():
    user_ids.append(user.id)

  posts = Post.objects.filter(created_by_id__in=list(user_ids))
  serializer = PostSerializer(posts, many=True)

  return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def post_detail(request, pk):
  post = Post.objects.get(pk=pk)

  return JsonResponse({
    'post': PostDetailSerializer(post).data
  })

@api_view(['GET'])
def post_list_profile(request, id):
  user = User.objects.get(pk=id)
  posts = Post.objects.filter(created_by_id=id)

  posts_serializer = PostSerializer(posts, many=True)
  user_serializer = UserSerializer(user)

  return JsonResponse({'posts':posts_serializer.data, 'user':user_serializer.data}, safe=False)

@api_view(['POST'])
def post_create(request):
  form = PostForm(request.data)

  if form.is_valid():
    post = form.save(commit=False)
    post.created_by = request.user #added authomatically by Django when we login
    post.save()

    serializer = PostSerializer(post)

    return JsonResponse(serializer.data, safe=False)

  else:
    return JsonResponse({'error':'add something here later!...'})


@api_view(['POST'])
def post_like(request, pk):
  post = Post.objects.get(pk=pk)

  if not post.likes.filter(created_by=request.user):
    like = Like.objects.create(created_by = request.user)
    post.likes_count = post.likes_count + 1
    post.likes.add(like)
    post.save()
    return JsonResponse({'message':'like created'})
  else:
    return JsonResponse({'message':'post already liked'})

@api_view(['POST'])
def post_create_comment(request, pk):
  comment = Comment.objects.create(body=request.data.get('body'), created_by=request.user)

  post = Post.objects.get(pk=pk)
  post.comments.add(comment)
  post.comment_count = post.comment_count + 1
  post.save()

  serializer = CommentSerializer(comment)

  return JsonResponse(serializer.data, safe=False)

@api_view(['GET'])
def get_trends(request):
  trends = Trend.objects.all()
  serializer = TrendSerializer(trends, many=True)

  return JsonResponse(serializer.data, safe=False)