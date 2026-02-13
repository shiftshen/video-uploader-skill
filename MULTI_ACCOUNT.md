# 多账号管理

## 目录结构

```
cookies/
├── douyin_uploader/
│   ├── 账号1/cookie.json    # 账号1的cookie
│   ├── 账号2/cookie.json    # 账号2的cookie
│   └── default/cookie.json  # 默认账号
└── tk_uploader/
    ├── 账号1/cookie.json
    └── 账号2/cookie.json
```

## 使用方式

```bash
# 指定账号上传
--account cookies/douyin_uploader/账号1/cookie.json
--account cookies/douyin_uploader/账号2/cookie.json
```

## 登录新账号

1. 创建账号目录：`mkdir cookies/douyin_uploader/新账号`
2. 删除该目录下的 cookie.json（如果存在）
3. 运行上传命令，会自动打开浏览器登录
4. 登录后 cookie 会自动保存

## 示例命令

```bash
# 抖音账号1
PYTHONPATH=. python3 upload_video.py \
  --platform douyin \
  --title "视频标题" \
  --video ~/Videos/test.mp4 \
  --account cookies/douyin_uploader/账号1/cookie.json

# 抖音账号2
PYTHONPATH=. python3 upload_video.py \
  --platform douyin \
  --title "视频标题" \
  --video ~/Videos/test.mp4 \
  --account cookies/douyin_uploader/账号2/cookie.json
```
