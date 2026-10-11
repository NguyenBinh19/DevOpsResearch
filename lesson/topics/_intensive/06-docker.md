## Image, container và host: ba ranh giới phải phân biệt

Image là tập lớp filesystem và metadata bất biến theo digest; container là tiến trình được chạy từ image với lớp ghi riêng, cấu hình, namespace mạng/process và giới hạn tài nguyên. Docker Engine chạy trên host; container dùng kernel của host chứ không có một kernel riêng như VM. Vì vậy image Linux không tự biến Windows host thành Linux production giống hệt; Docker Desktop thường dùng VM/WSL bên dưới. Container giúp đóng gói phụ thuộc ứng dụng, nhưng không tự tạo HA, backup hay bảo mật đầy đủ.

Build context là tập file gửi cho builder. Nếu copy cả `.git`, `.env` hoặc DB vào context, chúng có thể lọt vào image/layer hoặc làm build chậm. `.dockerignore` giới hạn context; secret build cần cơ chế secret mount phù hợp, không dùng `ARG PASSWORD` rồi hy vọng layer xóa được. Dockerfile `COPY requirements.txt` trước `COPY .` giúp cache bước cài dependency khi chỉ source đổi. Cache chỉ ảnh hưởng tốc độ build; muốn reproducible cần khóa dependency và pin base image/digest theo quy trình cập nhật bảo mật. Tag `notes:latest` là tên có thể di chuyển; digest định danh nội dung image.

### Port và filesystem qua hai ví dụ

App trong container nghe `0.0.0.0:8000`. `docker run -p 8080:8000` công bố cổng host 8080 tới cổng container 8000; `EXPOSE 8000` trong Dockerfile chỉ là metadata, không tự publish. Nếu app chỉ bind `127.0.0.1` **bên trong container**, host publish port vẫn có thể không tới process theo cách bạn mong; sửa bind address của app, không sửa ngẫu nhiên `-p`.

Writable layer của container mất khi container bị xóa; named volume có vòng đời riêng; bind mount nối trực tiếp đường host vào container. Với SQLite, nếu DB nằm trong layer, xóa/tạo container mới có thể làm mất dữ liệu. Volume không phải backup: bạn vẫn có thể xóa dữ liệu trong volume, làm hỏng file hoặc xóa cả volume. Backup cần bản sao độc lập và restore test. Bind mount tiện dev nhưng phụ thuộc đường host/quyền, dễ khác giữa máy người học và CI.

## Lab đọc một image thay vì chỉ chạy lệnh

**Điều kiện:** Docker đang chạy, dùng dự án `lesson/labs/notes-api`. Trước build, đọc Dockerfile và ghi: base image, workdir, các `COPY`, dependency, user chạy và lệnh khởi động. Chạy `docker build -t notes-lab:study .` trong thư mục lab. Quan sát output lần đầu và lần thứ hai; bước nào dùng cache? Dùng `docker image inspect notes-lab:study` xem config, `docker history notes-lab:study` xem lớp. **Kết quả dự kiến:** có image tag local; digest/ID và cache behavior thay đổi theo builder/máy. Đừng chép ID mẫu vào ghi chú.

Chạy container theo hướng dẫn app, map cổng host, rồi kiểm tra `docker ps`, `docker logs`, `docker inspect` và gọi API. Ghi chính xác ba địa chỉ: cổng process trong container, cổng publish trên host và URL client gọi. Gây lỗi bằng cách chạy một container thứ hai cùng host port: Docker báo port đã dùng. Đổi **host port** của container thứ hai, giữ container port nếu app vẫn nghe 8000. Giải thích vì sao sửa `EXPOSE` không giải quyết port conflict ở host.

Tạo dữ liệu thử trong DB của app, xóa **container lab** rồi tạo lại không gắn volume để quan sát dữ liệu mất; lặp lại với named volume đúng đường DB để thấy dữ liệu còn. Làm trong lab riêng vì thao tác xóa container/volume phá dữ liệu. Dọn bằng cách dừng/xóa đúng container và volume có tên lab sau khi đã ghi bằng chứng, kiểm tra tên bằng `docker ps -a` và `docker volume ls` trước khi xóa; không chạy lệnh prune toàn máy.

## Mạng Compose và dependency readiness

Compose tạo mạng cho service; trong cùng mạng, app gọi DB bằng tên service như `db:5432`, không dùng `localhost:5432` vì localhost của app container là chính app container. `depends_on` giúp thứ tự tạo/chạy theo cấu hình, nhưng app vẫn phải chịu được DB khởi động chậm hoặc mất kết nối sau đó. Healthcheck có thể giúp điều phối readiness ban đầu, không thay retry có backoff ở ứng dụng. Với nhiều service, tách lỗi “DNS không phân giải”, “TCP không connect”, “auth bị từ chối” và “schema chưa có”. Mỗi lỗi dẫn tới cách sửa khác.

Nếu container thoát ngay, xem `docker ps -a` và `docker logs <ten>`; exit code 0 có thể do command kết thúc bình thường nhưng bạn mong web server chạy mãi. `OOMKilled` liên quan memory; `permission denied` có thể do image user không đọc được bind mount; `no such file` có thể vì Dockerfile copy thiếu file hoặc workdir sai. Restart policy chỉ lặp lại lỗi nếu cấu hình sai. `docker exec` hữu ích để quan sát nhưng sửa file trực tiếp trong container không tồn tại sau recreate; sửa source/Dockerfile/config rồi rebuild/redeploy.

## Từ lab tới production

Chạy process dưới user không phải root nếu image/app cho phép; giới hạn capability, read-only filesystem khi phù hợp, scan image và cập nhật base image có kiểm soát. Không đưa secret vào env/log/image nếu có lựa chọn quản lý secret tốt hơn; biến môi trường dễ bị lộ qua cấu hình/quyền inspect. Thiết kế readiness/liveness ở orchestration theo hành vi app; Docker một mình không cân tải hay thay node hỏng. Với registry private như Harbor, chứng minh build agent đẩy được image, **node triển khai** kéo được image qua DNS/TLS/credential, và digest ở production đúng digest được phê duyệt.

**Ca có lời giải:** local chạy, CI build thành công, Pod production `ImagePullBackOff`. Trước hết đọc Events của Pod: `not found` khác `unauthorized`, TLS x509 hoặc timeout. So full image reference/digest, registry credential của namespace, DNS/TLS từ node và quyền project Harbor. Không sửa Dockerfile nếu image đã tồn tại đúng digest mà node không thể pull. Nguồn: [Docker build cache](https://docs.docker.com/build/cache/), [Docker volumes](https://docs.docker.com/engine/storage/volumes/), [Docker bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).
