# Giai đoạn 2 - Kiểm thử, container và CI/CD

Giai đoạn này biến ứng dụng chạy trên máy cá nhân thành một sản phẩm có thể kiểm tra, đóng gói và phát hành lặp lại. Luôn giữ cùng một ứng dụng mẫu để nhìn thấy tác động của từng thay đổi.

## Bài 1. Từ mã nguồn đến bản phát hành

Mã nguồn là công thức; artifact là kết quả của quy trình build. Khi một commit được đánh dấu để phát hành, ta muốn xác định chính xác mã nào, dependency nào và quy trình nào đã tạo artifact. Nếu mỗi môi trường tự build lại từ một nhánh đang thay đổi, bạn khó bảo đảm test đã chạy trên đúng thứ đang phục vụ người dùng. Cách dễ kiểm soát hơn là build một lần, định danh artifact, rồi chuyển chính artifact đó qua các môi trường.

Test giúp kiểm tra kỳ vọng, nhưng không chứng minh phần mềm không còn lỗi. Unit test cô lập hàm hoặc module; integration test kiểm tra tương tác giữa thành phần như API và database; smoke test chạy sau triển khai để xác nhận vài luồng quan trọng. Lint và static analysis bắt các vấn đề khác. Một pipeline tốt chọn lớp kiểm tra nhanh cho mỗi commit, lớp tốn kém hơn ở vị trí phù hợp, và hiển thị lỗi đủ rõ để người sửa tìm nguyên nhân.

### Ví dụ cụ thể

API ghi chú có endpoint `POST /notes`. Unit test kiểm tra dữ liệu rỗng bị từ chối; integration test tạo ghi chú trong database thử nghiệm rồi đọc lại; smoke test sau deploy gọi health endpoint và một request đọc. Nếu unit test qua nhưng integration test lỗi kết nối, hướng điều tra chuyển sang database/configuration. Nếu tất cả test trước deploy qua nhưng smoke test lỗi 502, hướng điều tra chuyển sang route, proxy hoặc tiến trình vừa triển khai.

Một release có thể thất bại dù pipeline màu xanh: dữ liệu thật lớn hơn dữ liệu test, secret sai, tài nguyên thiếu hoặc dependency ngoài không đáp ứng. Vì thế cần observability và rollback từ sớm. Ghi rõ điều gì được kiểm tra tự động và điều gì chưa.

### Lab trên ứng dụng mẫu

Điều kiện: ứng dụng mẫu chạy local. Viết một test cho request hợp lệ và một test cho request sai. Cố ý sửa mã để test thứ hai thất bại; xem thông báo lỗi và sửa lại. Ghi commit chứa test. Nếu chưa biết framework test của ngôn ngữ, dùng hướng dẫn chính thức của framework bạn chọn, không sao chép đoạn cấu hình không hiểu.

## Bài 2. Docker: image, container, volume và network

Image là gói chỉ đọc chứa filesystem và metadata cần để tạo container. Container là một tiến trình được chạy từ image trong môi trường cô lập tương đối. Một image có thể sinh ra nhiều container. Tag là tên thuận tiện nhưng có thể thay đổi trỏ tới image khác; digest định danh nội dung cụ thể hơn. Khi cần tái tạo release, hãy ghi tag/version và digest hoặc cơ chế định danh tương đương.

Dockerfile là chỉ dẫn build image theo các layer. Lớp thay đổi ít nên đặt trước để cache hữu ích; phụ thuộc nên được khóa phiên bản phù hợp. Không đưa secret vào Dockerfile, biến build hoặc layer. Một image nhỏ, chạy bằng user không đặc quyền và chỉ chứa thứ cần thiết giúp giảm bề mặt tấn công, nhưng quan trọng nhất là hiểu dependency và quy trình vá lỗi.

Filesystem bên trong container có thể mất khi container được thay thế. Dữ liệu cần tồn tại phải nằm ở volume, dịch vụ database hoặc storage phù hợp. Nếu hai container cần nói chuyện, chúng cần địa chỉ và network thích hợp; `localhost` bên trong container API là chính container API, không phải container database. Trong Compose, các dịch vụ cùng network có thể được gọi bằng tên dịch vụ theo cấu hình Compose.

### Lab Docker từng bước

Điều kiện: Docker đã cài và daemon chạy. Trước tiên thử `docker version`; nếu lỗi, ghi thông báo và kiểm tra Docker Desktop/daemon. Tạo Dockerfile cho ứng dụng mẫu, build với tag riêng như `notes-api:lab1`, rồi chạy container gắn port local. Dùng `docker ps` xác nhận tiến trình, `docker logs <ten>` để xem log và trình duyệt hoặc `curl` gọi health endpoint. Dừng và xóa container thử nghiệm khi xong; image có thể giữ lại để so sánh.

Khi thêm database qua Compose, khởi động stack, tạo một ghi chú, restart container API và xác minh ghi chú còn tồn tại. Sau đó giải thích data nằm ở đâu. Cố ý đặt host database là `localhost` và quan sát lỗi; sửa về tên dịch vụ. Không xóa volume chứa dữ liệu quan trọng; mọi thao tác xóa chỉ trong lab dùng dữ liệu giả.

### Lỗi thường gặp

"Container running" chỉ nói tiến trình chính còn sống, không chứng minh ứng dụng dùng được. Port trong container chưa tự động mở cho máy ngoài; cần mapping hoặc network phù hợp. Docker build thành công không có nghĩa image an toàn hay test đã qua. Health check chỉ có ích khi kiểm tra được khả năng mà hệ thống phụ thuộc, với thời gian và tần suất hợp lý.

## Bài 3. CI và đường đi của một commit

Continuous Integration (CI) là cách nhóm hợp nhất thay đổi thường xuyên, kèm build và kiểm tra tự động. Một workflow thường có trigger, job, runner và step. Trigger quyết định khi nào chạy; runner là máy thực hiện; job nhóm các step; artifact là đầu ra được lưu hoặc chuyển tiếp. Hãy bắt đầu bằng pipeline đơn giản: checkout -> cài dependency đã khóa -> lint/test -> build image. Khi pipeline lỗi, xem step đầu tiên thất bại và log liên quan thay vì chạy lại vô hạn.

Runner xử lý mã từ repository và đôi khi có quyền truy cập token. Vì vậy quyền của pipeline phải tối thiểu; secret không được in ra log; workflow nhận đóng góp từ người lạ cần kiểm tra cách xử lý token. Caching có thể tăng tốc nhưng cache không phải nguồn chân lý: xóa cache mà build vẫn phải đúng. Nếu dùng action của bên thứ ba, xem nguồn gốc và cách ghim phiên bản theo khuyến nghị của nền tảng.

Continuous delivery nghĩa là phần mềm luôn ở trạng thái có thể phát hành theo quy trình đã định. Continuous deployment đi thêm một bước: thay đổi qua kiểm tra được tự động đưa vào môi trường đích. Nhóm có thể cần bước phê duyệt vì lý do sản phẩm hoặc rủi ro; việc đó không làm bài học CI/CD kém giá trị. Mục tiêu là thay đổi nhỏ, có thể quan sát và khôi phục.

### Lab CI

Điều kiện: repository thử nghiệm trên nền tảng CI bạn chọn. Viết workflow chạy test của ứng dụng mẫu khi có pull request hoặc push vào nhánh bài học. Sau khi chạy xanh, cố ý tạo một test lỗi, đẩy lên nhánh riêng, xem step và exit code, rồi sửa. Ghi lại commit, đường dẫn run và nguyên nhân. Không đặt secret thật vào repo hoặc nội dung workflow; nếu pipeline chưa cần deploy, nó không cần quyền cloud.

## Bài 4. Phân tích Dockerfile và Compose thực tế

Trong `lesson/labs/notes-api/Dockerfile`, dòng `FROM` chọn image nền có Python; `WORKDIR` đặt thư mục làm việc; `COPY` mang code vào image; `RUN` tạo thư mục dữ liệu; `USER` chuyển sang người dùng không đặc quyền; `ENV` đặt cấu hình mặc định; `EXPOSE` ghi lại cổng ứng dụng; `CMD` chỉ định tiến trình khởi chạy. `EXPOSE` không tự mở cổng ra máy bạn: bước `docker run -p` hoặc Compose `ports` mới ánh xạ cổng. Trong lab, server phải nghe `0.0.0.0` bên trong container để lưu lượng từ bên ngoài container tới được; khi chạy trực tiếp trên máy, mặc định chỉ nghe `127.0.0.1` để an toàn hơn.

Compose mô tả cách chạy các dịch vụ local bằng file. Ở bản lab này chỉ có một service API và một named volume. Volume gắn với `/data`; SQLite ghi file vào đó. Mapping `127.0.0.1:8000:8000` chỉ mở ở loopback của máy chủ Docker, giảm nguy cơ vô tình công khai lab ra mạng. Khi chuyển sang cloud hoặc cluster, cấu hình truy cập sẽ khác và cần thiết kế riêng.

### Lab tái lập, có kết quả mong đợi

Điều kiện: Docker Engine/Desktop đang chạy, cổng 8000 chưa bị chiếm, thư mục lab không chứa dữ liệu quan trọng. Mở terminal tại `lesson/labs/notes-api`, chạy `docker compose build` rồi `docker compose up -d`. Dùng `docker compose ps` để thấy service đang chạy. Gọi `http://127.0.0.1:8000/health`; mong đợi JSON `status: ok`. Gửi POST tạo một ghi chú như ở Giai đoạn 1, rồi gọi GET để xác nhận.

Chạy `docker compose restart api`; GET lại. Ghi chú phải còn vì database nằm trong named volume. Tiếp tục chạy `docker compose down` rồi `docker compose up -d`; GET lại. Dữ liệu vẫn còn nếu bạn **không** dùng tùy chọn xóa volume. Kết thúc lab bằng `docker compose down`. Chỉ khi bạn muốn xóa dữ liệu lab giả, kiểm tra tên project/volume rồi dùng tùy chọn xóa volume theo tài liệu Docker. Đừng dùng nó khi volume có dữ liệu cần giữ.

Nếu health không mở được, điều tra theo thứ tự: `docker compose ps` có service không; `docker compose logs api` có lỗi không; port 8000 bị chiếm không; có nhập đúng `127.0.0.1` không. Nếu ứng dụng chạy nhưng trả 500 sau khi ghi, xem quyền `/data` và log database. Không sửa Dockerfile, Compose và code cùng lúc; thay một yếu tố rồi thử lại.

### Câu hỏi tư duy

Vì sao `docker compose down` không nên được xem là backup? Vì sao đổi code rồi `docker compose restart` chưa chắc chạy code mới? Vì sao image đã build không chứa ghi chú vừa tạo khi volume được gắn? Đáp án gợi ý: volume là dữ liệu riêng, không phải bản sao phục hồi; restart dùng container/image hiện có, cần build và recreate để nhận mã mới; dữ liệu phát sinh được ghi vào volume ngoài image.

## Bài 5. Tự xây một pipeline có bằng chứng

Hãy diễn đạt pipeline thành hợp đồng. Đầu vào: commit cụ thể. Kiểm tra: cú pháp Python, test cho endpoint và tạo image. Đầu ra: log kết quả, artifact image có định danh, và trạng thái pass/fail. Nếu test fail, không phát hành artifact như bản dùng được. Một pipeline chỉ in chữ "success" mà không chạy kiểm tra có ý nghĩa không mang lại nhiều bảo đảm.

Với GitHub Actions, workflow là file YAML trong `.github/workflows/`. `on` xác định sự kiện, `jobs` định nghĩa công việc, `runs-on` chọn runner và `steps` chạy lệnh/action. Bắt đầu bằng workflow chỉ kiểm tra cú pháp và chạy test, chưa cần cloud credential. Workflow mẫu cần phù hợp phiên bản runner và action hiện hành; khi viết bài thực hành, tra tài liệu GitHub để xác nhận cách ghim phiên bản và quyền token.

### Lab pipeline theo hai tình huống

Tạo một test kiểm tra `GET /health` trả 200 và version. Đầu tiên chạy test trên máy; ghi lệnh và kết quả. Sau đó đưa cùng lệnh vào CI. Đẩy một commit hợp lệ để pipeline xanh. Tạo nhánh lab và sửa test để kỳ vọng sai; đẩy commit, chụp tên step fail và dòng log chỉ ra assertion. Sửa lại test hoặc code và đẩy tiếp. Lúc này bạn có một chuỗi chứng minh pipeline thực sự chặn lỗi, không chỉ là cấu hình đẹp.

Phân biệt ba loại lỗi trong CI: test assertion fail (logic/kỳ vọng), environment fail (thiếu dependency, khác phiên bản), infrastructure fail (runner hoặc registry không đáp ứng). Cách xử lý khác nhau. Với lỗi môi trường, so sánh phiên bản Python, working directory, biến môi trường và file dependency đã khóa giữa local và runner. Đừng thêm retry trước khi biết lỗi nào đang xảy ra.

## Bài 6. Bài tập thiết kế release và rollback

Viết bảng bốn cột cho phiên bản B: thay đổi gì, bằng chứng kiểm tra, tín hiệu sau deploy, cách rollback. Ví dụ: thay endpoint tạo ghi chú -> unit/integration test và smoke POST/GET -> tỷ lệ 5xx, thời gian xử lý, log validation -> triển khai lại image A nếu B lỗi, sau khi xác nhận database vẫn tương thích. Sau đó thêm một thay đổi schema; nêu vì sao rollback image có thể thất bại và cách chia migration thành bước tương thích.

Một release có thể dùng checkpoint 5 phút và 30 phút. Sau 5 phút xem smoke test và lỗi rõ; sau 30 phút xem xu hướng latency/error. Các con số chỉ là ví dụ cho lab, không phải ngưỡng áp dụng mọi production. Điều quan trọng là điều kiện thành công và dừng được viết ra trước khi triển khai.

Một bản phát hành cần tối thiểu: phiên bản xác định, nội dung thay đổi, điều kiện đưa lên, cách kiểm tra sau triển khai, người chịu trách nhiệm và cách quay về. Rollback bằng image cũ không luôn đủ nếu database schema đã đổi không tương thích. Tập thói quen tách thay đổi schema có thể tương thích ngược, thử migration trên dữ liệu giả và dự tính cách phục hồi.

Cổng năng lực: bạn tự build image, chạy và dừng container; giải thích volume/network; test có thể bắt một lỗi bạn cố ý tạo; pipeline phát hiện lỗi và lưu artifact; bạn nêu được cách xác định phiên bản đang chạy và cách rollback an toàn. Nếu một mục chưa đạt, lặp lại với ứng dụng nhỏ hơn.

### Câu hỏi phỏng vấn để tự trả lời

Image khác container thế nào? Vì sao không nên dùng `latest` làm định danh duy nhất cho release? Unit, integration và smoke test phát hiện các lớp lỗi nào? Nếu pipeline xanh nhưng ứng dụng báo 502 sau deploy, bạn kiểm tra những gì? Vì sao secret trong image là vấn đề ngay cả khi container đã bị xóa?

## Bài 7. Chạy và đọc test thật của Notes API

File `lesson/labs/notes-api/test_app.py` dùng thư viện `unittest`. `setUpClass` tạo thư mục database tạm và khởi động server trên cổng tự chọn; `tearDownClass` dừng server và dọn dữ liệu thử. Test health kiểm tra HTTP 200 cùng JSON `status: ok`; test tạo ghi chú gửi POST rồi GET để xác minh dữ liệu đã lưu; test input rỗng xác nhận HTTP 400. Đây là integration test vì nó thực sự đi qua HTTP handler và SQLite, không chỉ gọi một hàm riêng lẻ.

Mở terminal ở thư mục `lesson/labs/notes-api` và chạy `python -m unittest -v test_app.py`. Mong đợi ba test `ok` và tổng kết `OK`. Nếu một test fail, đọc tên test, dòng assertion và phản hồi thực tế. Đừng chỉ sửa giá trị kỳ vọng cho xanh: hãy hỏi hành vi mong muốn là gì. Thử cố ý đổi `status: ok` trong code thành `status: bad`, chạy lại và dự đoán test nào đỏ. Hoàn nguyên code sau thí nghiệm.

Test có thể pass trên máy nhưng fail CI vì khác Python, working directory, quyền file hoặc timing. File test dùng cổng do hệ điều hành chọn để tránh xung đột với app chạy trên 8000. Nó cũng dùng database tạm để không làm bẩn ghi chú cá nhân. Hai quyết định này làm test lặp được hơn. Nếu test thỉnh thoảng đỏ, ghi tần suất và điều kiện; test không ổn định không nên được giải quyết bằng cách bỏ qua lỗi mà không tìm nguyên nhân.

### Đọc test như hợp đồng hành vi

Hãy viết bảng ba cột: input, expected status, expected data. Dòng 1: `GET /health`, 200, `status=ok`. Dòng 2: POST JSON có body hợp lệ, 201, trả ID. Dòng 3: POST JSON `{}`, 400, báo invalid_note. Sau đó bổ sung một trường hợp bạn muốn test, ví dụ GET path không tồn tại phải 404. Nếu viết được test mới rồi thấy nó fail trước khi sửa code, bạn đã dùng test để làm rõ yêu cầu.

## Bài 8. Đọc workflow CI và nguyên tắc quyền

File `lesson/labs/notes-api/ci-example.yml` là mẫu để sao chép vào `.github/workflows/ci.yml` **sau khi** repository được đưa lên GitHub. Workflow chạy khi push hoặc pull request. `permissions: contents: read` giới hạn token mặc định cho job chỉ đọc mã; nó không cần quyền cloud. Job dùng runner Linux, checkout mã, chuẩn bị Python phiên bản ghi rõ rồi chạy cùng bộ test. Nếu bạn đặt app ở đường dẫn khác, phải sửa `-s` trong lệnh test. Đọc workflow trước khi chạy và kiểm tra phiên bản action theo tài liệu GitHub hiện hành vì chúng có thể thay đổi.

Khi xem một run, đọc từ trên xuống: sự kiện nào kích hoạt, commit SHA nào, runner nào, step đầu tiên fail, exit code và log. Nếu checkout fail thì code chưa tới runner; nếu setup Python fail thì test chưa chạy; nếu unittest fail thì xem assertion; nếu workflow không xuất hiện thì kiểm tra vị trí file và trigger. Đừng gọi mọi trường hợp là "test fail".

Quyền CI nên tăng khi có nhu cầu mới và bằng chứng: build/test không cần quyền deploy. Một job deploy cần điều kiện nhánh/môi trường, identity phù hợp và approval nếu rủi ro yêu cầu. Pull request từ bên ngoài là dữ liệu chưa tin cậy. Không đưa secret vào lệnh `echo` hoặc biến mà test có thể in ra. Sau khi test ổn định, thêm bước build image và artifact theo tài liệu nền tảng; lúc đó cần định nghĩa tag/digest để nối commit với image.

## Bài 9. Chuỗi điều tra khi bản phát hành thất bại

Giả sử CI xanh và image build thành công, nhưng sau khi Compose chạy người dùng không thể truy cập. Hãy đi theo thứ tự: image đang chạy có đúng version không (`docker compose images` hoặc thông tin container); container có chạy không (`docker compose ps`); log khởi động báo gì; mapping port đúng chưa; health endpoint từ máy chủ có trả lời không; request có tới ứng dụng không. Nếu container chết do không ghi được `/data`, vấn đề là quyền/volume, không phải DNS. Nếu API trả 404 cho `/health`, có thể đang chạy image sai hoặc route code đã đổi.

Viết một báo cáo ngắn: triệu chứng, bằng chứng, giả thuyết, thay đổi đã thử, kết quả và hành động tiếp theo. Báo cáo này làm quá trình debug có thể review. Khi thay đổi một yếu tố và kiểm tra lại, bạn biết điều gì đã giúp; khi thay mọi thứ cùng lúc, bạn chỉ biết hệ thống bỗng chạy.

## Tài liệu chính thức

- Docker concepts: https://docs.docker.com/get-started/docker-concepts/
- Docker image: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-an-image/
- GitHub Actions concepts: https://docs.github.com/en/actions/concepts
- GitHub Actions Python CI: https://docs.github.com/en/actions/tutorials/build-and-test-code/python
- DORA continuous delivery: https://dora.dev/capabilities/continuous-delivery/
