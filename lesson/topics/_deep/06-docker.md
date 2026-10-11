## Từ Dockerfile đến tiến trình đang chạy

Dockerfile là công thức build image; image là các lớp nội dung và metadata; container là một tiến trình (hoặc nhóm tiến trình) chạy từ image với filesystem writable riêng, network namespace và giới hạn tài nguyên theo cấu hình. Dừng container không đồng nghĩa xóa image; xóa container có thể xóa dữ liệu ở writable layer. Volume/bind mount là cách đưa dữ liệu ra ngoài vòng đời container, nhưng volume vẫn cần backup. Nếu app dùng SQLite ở `/data/notes.db`, chạy image mà không mount `/data` có thể làm ghi chú biến mất khi thay container.

Quy trình đọc Dockerfile: xác định base image và phiên bản, thứ tự `COPY`/`RUN`, user cuối cùng, cổng, biến môi trường, đường ghi, lệnh khởi động. Base image nhỏ không mặc nhiên an toàn; vẫn cần update/quét dependency và kiểm tra bản vá. Dùng tag cố định hoặc digest cho build tái tạo được. `EXPOSE` chỉ là metadata mô tả cổng; publish cổng từ host là lựa chọn riêng khi `docker run -p` hoặc Compose `ports`.

## Lab 1: image bất biến, dữ liệu tồn tại

Tại `lesson/labs/notes-api`, đọc Dockerfile rồi build `docker build -t notes-api:lab-1 .`. Chạy container lab với `-p 127.0.0.1:8000:8000` và volume gắn `/data`. Gọi `GET /health`, tạo ghi chú, đọc lại. Dừng/xóa container, chạy container mới từ **cùng image** với **cùng volume**, xác nhận ghi chú còn. Lặp lại với volume mới để thấy dữ liệu không tự đi theo image. Ghi tên volume, ID image, ID container và nội dung DB; đó là bằng chứng phân biệt các khái niệm. Khi dọn dẹp, chỉ xóa container/volume lab đã xác nhận tên, không dùng lệnh prune toàn máy nếu có dự án khác.

Nếu chạy Compose, `docker compose up --build -d`, xem `docker compose ps`, `docker compose logs`, rồi `docker compose down`. Đừng thêm `-v` nếu bạn còn cần volume dữ liệu lab. Trong YAML Compose, `build` tạo image, `environment` đặt cấu hình runtime, `volumes` nối dữ liệu, `ports` xuất cổng ra host. Container trong cùng network gọi nhau bằng tên service và container port; `localhost` trong container chỉ trỏ về chính container đó.

## Lab 2: ba lỗi có chủ đích

1. Đổi host port 8000 sang 8001 nhưng vẫn gọi 8000. Kiểm tra `docker compose ps` và mapping; không sửa app khi lỗi ở cổng host.
2. Đổi biến `NOTES_DB` sang đường không ghi được dưới non-root user. `GET /health` có thể vẫn 200 nhưng `POST /notes` lỗi; xem log và quyền filesystem. Sửa về `/data/notes.db` đã mount writable.
3. Đổi tên service DNS trong cấu hình reverse proxy hoặc app phụ thuộc. Kiểm tra container network và tên service. Đừng dùng IP container cố định vì có thể đổi khi tái tạo.

Sau mỗi lỗi, ghi giả thuyết, lệnh kiểm tra, output then chốt, sửa một biến và xác nhận. Cách này quan trọng hơn việc thuộc lòng toàn bộ option Docker.

## Bảo mật, tài nguyên và vận hành

Chạy non-root giảm tác động nếu app bị khai thác, nhưng không thay việc kiểm soát secret, filesystem, network và image. Không `COPY .` bừa nếu thư mục chứa `.env`, private key hoặc test data; dùng `.dockerignore`. Không đưa secret vào `ARG`/`ENV` khi build vì có thể lộ qua layer/history hoặc registry. Đặt memory/CPU limit trong môi trường phù hợp và xem OOM exit code khi app restart. Log nên ra stdout/stderr để collector thu; file log bên trong container dễ mất khi thay container.

Container không phải VM: nó dùng kernel host; isolation có giới hạn và phụ thuộc cấu hình runtime. Một container `healthy` theo healthcheck đơn giản cũng chưa chứng minh chức năng ghi DB thành công. Cần kết hợp smoke test và telemetry khi release.
