# To-do list web app

Ứng dụng quản lý công việc với Django REST Framework, React và PostgreSQL.

## Chạy toàn bộ ứng dụng bằng Docker

Cần Docker Engine/Desktop và Docker Compose. Tại thư mục gốc:

```sh
cp .env.example .env
```

Đổi `DJANGO_SECRET_KEY` và `POSTGRES_PASSWORD` trong `.env`, rồi khởi động:

```sh
docker compose up --build
```

Compose đợi PostgreSQL sẵn sàng, chạy `migrate` và `collectstatic`, rồi mới khởi động Gunicorn và nginx. Mở <http://localhost:8080>. API dùng cùng origin tại `/api/v1/`; health check ở `/healthz/`. Dừng bằng `docker compose down`; dữ liệu PostgreSQL nằm trong volume `postgres_data` và được giữ lại. Muốn xóa cả dữ liệu, dùng `docker compose down -v`.

Compose phục vụ HTTP để phát triển và chạy thử tại máy cá nhân. Khi đưa ra Internet, đặt nginx sau TLS reverse proxy và cấu hình proxy đó ghi đè header `X-Forwarded-Proto` theo kết nối TLS. Dùng secret ngẫu nhiên (`python -c "import secrets; print(secrets.token_urlsafe(64))"`), khai báo hostname thật trong `DJANGO_ALLOWED_HOSTS`, đặt đúng `CSRF_TRUSTED_ORIGINS`, rồi bật `DJANGO_SSL_REDIRECT=true`, `DJANGO_SECURE_COOKIES=true` và HSTS sau khi HTTPS đã hoạt động ổn định. Chỉ bật `DJANGO_HSTS_INCLUDE_SUBDOMAINS=true` và `DJANGO_HSTS_PRELOAD=true` nếu mọi subdomain cũng chỉ phục vụ HTTPS và domain đủ điều kiện preload.

### Nâng cấp từ database phiên bản cũ

Migration giữ lại task và danh mục từ schema cũ. Nếu database chỉ có một tài khoản đang hoạt động, các task cũ được gán cho tài khoản đó. Nếu không có hoặc có nhiều tài khoản, migration tạo chủ sở hữu khóa `legacy_import` (hoặc tên có hậu tố), bị vô hiệu hóa để tránh cấp nhầm dữ liệu. Quản trị viên cần chuyển các task đó sang đúng tài khoản trước khi người dùng truy cập. Hãy sao lưu PostgreSQL trước khi nâng cấp.

Sau migration, có thể xem các tài khoản nhập dữ liệu bằng Django shell:

```sh
docker compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; print(list(get_user_model().objects.filter(username__startswith='legacy_import').values_list('username', 'is_active')))"
```

Các cảnh báo `manage.py check --deploy` về HTTPS/HSTS là có chủ đích khi chạy Compose cục bộ qua HTTP; production cần bật các biến bảo mật bên trên và kiểm tra lại sau khi TLS reverse proxy đã cấu hình.

## Chạy backend và frontend riêng để phát triển

Cần Python 3.11+ và Node.js 22+. Tạo `.env` từ `.env.example`, rồi cài backend:

```sh
python -m venv backend/.venv
# Windows PowerShell:
backend\.venv\Scripts\Activate.ps1
# macOS/Linux: source backend/.venv/bin/activate
pip install -r requirements.txt
```

Đặt `POSTGRES_HOST=localhost` trong `.env` nếu PostgreSQL đang chạy trên máy host. Nếu chưa có PostgreSQL, bỏ các biến `POSTGRES_*` hoặc xóa `POSTGRES_DB` để Django dùng SQLite cục bộ.

```sh
cd backend
python manage.py migrate
python manage.py runserver
```

Trong terminal khác:

```sh
cd frontend/todo_frontend
npm ci
npm start
```

frontend dev server chạy tại <http://localhost:5173> và proxy API tới `http://127.0.0.1:8000`. Để trỏ frontend đến API ở origin khác, đặt `VITE_API_URL` trước khi build.

## Cấu hình môi trường

Cấu hình được đọc từ biến môi trường hoặc file `.env` ở thư mục gốc hay `backend/`. Xem [.env.example](.env.example) để biết các giá trị mẫu. Những biến thường cần chỉnh:

| Biến | Mục đích |
| --- | --- |
| `DJANGO_SECRET_KEY` | Khóa bí mật Django; bắt buộc khi `DJANGO_DEBUG=false` |
| `DJANGO_DEBUG` | Chế độ debug; mặc định tắt |
| `DJANGO_ALLOWED_HOSTS` | Danh sách hostname được phép, phân tách bằng dấu phẩy |
| `TIME_ZONE` | Múi giờ Django; mặc định `Asia/Ho_Chi_Minh` |
| `DJANGO_TEST_SQLITE` | Dùng SQLite riêng cho test; Compose tắt để kiểm tra trên PostgreSQL |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Thông tin database PostgreSQL |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Địa chỉ PostgreSQL; Compose tự đặt host thành `db` |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | Các origin được phép, phân tách bằng dấu phẩy |
| `AUTH_TOKEN_TTL_DAYS` | Số ngày hiệu lực của token |

## Kiểm tra

Chạy backend tests trong `backend/`:

```sh
python manage.py test
```

Mặc định test backend dùng SQLite riêng để chạy nhanh. Để kiểm tra migration và toàn bộ test trên PostgreSQL bằng Docker Compose:

```sh
docker compose run --rm backend python manage.py test
```

Build và test frontend:

```sh
cd frontend/todo_frontend
npm ci
npm test
npm run build
```

