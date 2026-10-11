## Bài đọc Dockerfile theo từng lớp

Với Dockerfile của Notes API, đánh dấu dòng nào ảnh hưởng cache khi `requirements.txt` đổi và khi chỉ `app.py` đổi. `COPY . .` sớm sẽ làm bước cài package sau nó mất cache mỗi lần source đổi. Đưa file dependency trước, cài, rồi copy source giúp build nhanh hơn, nhưng phải bảo đảm dependency được khóa và `.dockerignore` loại file nhạy cảm. Multi-stage build có thể tách tool build khỏi runtime image; image nhỏ hơn giảm bề mặt và thời gian pull, nhưng vẫn cần scan và cập nhật base. Một image chứa `curl`/shell có thể dễ debug, nhưng production image tối giản có tradeoff điều tra; dùng ephemeral debug container/telemetry theo chính sách thay vì để mọi công cụ trong image.

## Container restart và dữ liệu

`docker restart` giữ cùng container và writable layer, còn `docker rm` rồi `docker run` tạo container khác, writable layer cũ không còn. Nếu bạn test persistence chỉ bằng `restart`, bạn chưa chứng minh dữ liệu sống qua recreate/deploy. Thử với named volume và kiểm tra volume path đúng đường app ghi. Một volume vẫn có thể bị hỏng/xóa; backup cần bản sao ra ngoài Docker host, policy retention và restore test. Nếu bind mount từ Windows vào Linux VM của Docker Desktop, quyền/đường dẫn/performance có thể khác server Linux; ghi môi trường lab để tránh kết luận quá rộng.

### Exit code và signal

Container chính sống theo PID 1; nếu command khởi động shell rồi shell thoát hoặc không chuyển signal đúng, shutdown có thể không graceful. Khi orchestrator gửi SIGTERM và chờ grace period, app cần ngừng nhận request, hoàn tất công việc trong giới hạn rồi thoát. Nếu process ignore signal, bị SIGKILL, có thể mất request hoặc corrupt dữ liệu nếu app không xử lý tốt. Dockerfile `CMD` dạng exec thường giúp signal tới process trực tiếp hơn dạng shell; kiểm tra entrypoint thực. `OOMKilled` khác exit do exception: xem trạng thái, limit và log trước khi tăng memory.

## Tình huống phỏng vấn có lời giải

**Docker build xanh, container thoát ngay với code 0.** Có thể command chạy tác vụ ngắn rồi kết thúc; kiểm tra `CMD`/entrypoint, process có web server blocking không. **App gọi `localhost:5432` nhưng DB ở Compose service `db`.** Localhost trong app container là app container; dùng tên service/mạng và port DB nội bộ. **Host gọi `localhost:8080` bị refused nhưng `docker ps` Up.** Kiểm tra publish port, app bind address, process cổng trong container và firewall host. **Docker scan báo CVE trong base image.** Xác định version/đường khai thác/patch, cập nhật base có test; không xóa package tùy tiện làm app hỏng.

Nguồn: [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/), [Docker container networking](https://docs.docker.com/engine/network/), [Docker volumes](https://docs.docker.com/engine/storage/volumes/).
