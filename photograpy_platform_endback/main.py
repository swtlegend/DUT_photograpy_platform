from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# 确保上传目录存在
UPLOAD_DIRECTORY = "./uploaded_images"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

app = FastAPI()

# 定义允许的源 - 在开发环境中允许所有源，生产环境中应具体指定
ALLOWED_ORIGINS = ["*"]

# 添加CORS中间件以解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"],
    max_age=600,
)

# 挂载静态文件目录以提供上传的图片访问
app.mount("/images", StaticFiles(directory=UPLOAD_DIRECTORY), name="images")

# 包含路由
from routers import users, posts, comments, interactions, follows, collections, ratings, leaderboard, messages
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(comments.router, prefix="/api/comments", tags=["comments"])
app.include_router(interactions.router, prefix="/api/interactions", tags=["interactions"])
app.include_router(follows.router, prefix="/api/follows", tags=["follows"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["ratings"])
app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["leaderboard"])
app.include_router(messages.router, prefix="/api/messages", tags=["messages"])

# 全局异常处理器，确保CORS头在错误情况下也能正确设置
@app.exception_handler(Exception)
async def universal_exception_handler(request, exc):
    from fastapi.responses import JSONResponse
    response = JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )
    # 当允许所有源时，使用请求的源作为响应头
    origin = request.headers.get("origin")
    if origin:
        response.headers["Access-Control-Allow-Origin"] = origin
    elif ALLOWED_ORIGINS == ["*"]:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

@app.get("/")
async def root():
    return {"message": "欢迎来到摄影论坛API"}

@app.get("/api")
async def api_root():
    return {"message": "摄影论坛API", "version": "1.0.0"}